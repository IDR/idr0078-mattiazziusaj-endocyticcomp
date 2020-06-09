#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The original raw data uploaded by the submitter contained Opera Flex data
# where odd and even rows had been acquired separately using different plate
# barcodes.
#
# This script creates rich companion OME-XML files for the combined
# plate layout using a priori knowledge of the dataset as well. This requires
# a custom version of Bio-Formats which disables the plate barcode check.
# For each Flex plate:
# 1. a MetadataOnly OME-XML string is generated using the Bio-Formats showinf
#    command-line tool.
# 2. the MetadataOnly element is replaced by TiffData elements pointing to the
#    relevant Flex file for each field of view


import argparse
import glob
import logging
import os
from os.path import abspath, dirname, join
import re
import string
import subprocess
import uuid
import xml.etree.ElementTree as ElementTree


NS = {'OME': "http://www.openmicroscopy.org/Schemas/OME/2016-06"}
NAME_PATTERN = re.compile("Well ([A-Z])-(\d+); Field #(\d)")
ElementTree.register_namespace("", NS['OME'])


def generate_companion(folder):
    files = sorted(glob.glob('%s/*.flex' % (folder)))
    source_file = files[0]
    proc = subprocess.Popen(
        ['showinf', '-nopix', '-omexml-only', source_file],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    (output, error_output) = proc.communicate()
    logging.debug("Generated OME-XML for %s" % source_file)

    tree, well_uuids = update_companion(output, folder)
    # Files sanity check
    assert files == sorted(well_uuids.keys())

    # Rewrite companion file
    companion_file = '%s.companion.ome' % folder.replace('/', '_')
    tree.write(companion_file, encoding='UTF-8', xml_declaration=True)
    logging.debug("Generated %s" % companion_file)
    return companion_file


def update_companion(xml_string, prefix):
    tree = ElementTree.ElementTree(ElementTree.fromstring(xml_string))
    root = tree.getroot()
    well_uuids = {}

    for i in root.findall('OME:Image', NS):
        name = i.attrib['Name']
        # Parse the image name and retrieve row/column/field
        m = NAME_PATTERN.match(name)
        row = string.ascii_uppercase.index(m.group(1))
        column = int(m.group(2)) - 1
        field = int(m.group(3)) - 1

        for p in i.findall('OME:Pixels', NS):
            # Dimension sanity check
            assert int(p.attrib['SizeC']) == 3
            assert int(p.attrib['SizeT']) == 1
            assert int(p.attrib['SizeZ']) == 5
            assert p.attrib['DimensionOrder'] == 'XYCZT'

            # Find the metadataonly element
            c = p.find('OME:MetadataOnly', NS)
            tail = c.tail
            index = list(p).index(c)

            # Determine field filename/UUID
            well_filename = "%s/%03d%03d000.flex" % (
                prefix, row + 1, column + 1)
            well_uuid = well_uuids.setdefault(well_filename, uuid.uuid4().urn)

            # Create a TiffData/UUID element
            field_tiffdata = ElementTree.Element(
                'TiffData', FirstC='0', FirstT='0', FirstZ='0',
                PlaneCount='15', IFD=str(field * 15))
            field_tiffdata.tail = tail
            field_uuid = ElementTree.SubElement(
                field_tiffdata, "UUID", {'FileName': well_filename})
            field_uuid.text = well_uuid
            field_uuid.tail = tail

            # Replace MetadataOnly element by TiffData
            p.remove(c)
            p.insert(index, field_tiffdata)
    logging.debug("Updated the OME-XML with TiffData elements")
    return tree, well_uuids


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--quiet', '-q', action='count', default=0)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO - 10 * args.verbose + 10 * args.quiet)

    metadata_dir = dirname(dirname(abspath(__file__)))
    companions_dir = join(metadata_dir, 'screenA', 'companions')
    os.chdir(companions_dir)

    plates_file = join(metadata_dir, 'screenA', 'idr0078-screenA-plates.tsv')
    with open(plates_file, 'w') as f:
        for folder in sorted(glob.glob('*/*')):
            logging.info("Generating companion file for %s" % folder)
            companion_file = generate_companion(folder)
            f.write("%s\t%s\n" % (folder.replace('/', ' '),
                    "/uod/idr/metadata/idr0078-mattiazziusaj-endocyticcomp/"
                    "screenA/companions/%s" % companion_file))
