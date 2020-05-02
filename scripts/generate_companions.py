#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate companion files for experimentA of the idr0065 study. This script
# assumes the following layout for the original data:
#
#  <microscopic_slide>/        All data associated with a microscopic slide
#    pheno/                    Phenotypic acquisition
#      metadata.txt            Metadata for the phenotyping acquisition
#      Pos101/                 Position on a microscopyic slide
#        fluor/                Fluorescence timelapse images
#        phase/                Phase timelapse images
#    geno/                     Genotypic acqusition
#      Pos101/                 Position on the microscopyic slide
#        1_cy5_fluor/          Fluorescence acquisition (11 cycles)
#        2_cy3_fluor/          Fluorescence acquisition (11 cycles)
#        3_TxR_fluor/          Fluorescence acquisition (11 cycles)
#        4_fam_flour/          Fluorescence acquisition (11 cycles)
#        phase/                Phase acquisition (11 cycles)

import argparse
import logging

from ome_model.experimental import Image, Plate, create_companion
import os
from os.path import join, dirname, basename
import glob
import string
import re
import subprocess

BASE_DIRECTORY = "/uod/idr/filesets/idr0078-mattiazziusaj-endocyticcomp/"
DATA_DIRECTORY = join(BASE_DIRECTORY, "20200204-rsync")


def write_companion(plate, file_path):
    # Generate companion OME-XML file
    if not os.path.exists(dirname(file_path)):
        os.makedirs(dirname(file_path))
        logging.info("Created %s" % dirname(file_path))
    create_companion(plates=[plate], out=file_path)

    # Indent XML for readability
    proc = subprocess.Popen(
        ['xmllint', '--format', '-o', file_path, file_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    (output, error_output) = proc.communicate()
    logging.info("Created %s" % file_path)


def parse_well(filename):
    FLEX_PATTERN = re.compile(r'(?P<row>\d{3})(?P<column>\d{3})\d{3}.flex')
    m = FLEX_PATTERN.match(filename)
    return int(m.group('row')), int(m.group('column'))


def create_screen_companions():
    """Screen metadata files"""

    logging.info("Generating screen companion files")

    plates = []
    files = (glob.glob('screenA/companions/Sac6-tdTomato/10/*.flex') +
             glob.glob('screenA/companions/Sac6-tdTomato/10_2/*.flex'))
    flex_files = [f[len('screenA/companions/'):] for f in files]
    logging.debug("Found %s files" % len(flex_files))

    wells = []
    for flex_file in flex_files:
        row, column = parse_well(basename(flex_file))
        wells.append((row, column, flex_file))

    rows = max(wells)[0]
    columns = max(wells)[1]
    logging.debug("Detected %s rows and %s columns" % (rows, columns))
    plate = Plate("10", rows, columns)
    for row, column, flex_file in wells:
        w = plate.add_well(row - 1, column - 1)
        for field in range(3):
            name = "%s%s Field %s" % (
                string.ascii_uppercase[row - 1], column, field)
            image = Image(
                "Field. %g" % field, 1305, 879, 5, 3, 1,
                order="XYZCT", type="uint16")
            image.add_channel("GFP", -1)
            image.add_channel("tdTomato", -1)
            image.add_channel("Dextran", -1)
            image.add_tiff(
                flex_file, c=0, z=0, t=0, ifd=15*field, planeCount=15)
            w.add_wellsample(field, image)

    companion_file = join(
        'screenA', 'companions', 'Sac6-tdTomato_10.companion.ome')
    write_companion(plate, companion_file)

    plates.append(
        "Screen:name:idr0078-mattiazziusaj-endocyticcomp/screenA/\t"
        "%s\n" % companion_file)

    tsv = join('screenA', 'idr0078-experimentA-plates.tsv')
    with open(tsv, 'w') as f:
        for p in plates:
            f.write(p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)
    args = parser.parse_args()

    levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    level = levels[min(len(levels)-1, args.verbose)]
    logger = logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s %(message)s")

    create_screen_companions()
