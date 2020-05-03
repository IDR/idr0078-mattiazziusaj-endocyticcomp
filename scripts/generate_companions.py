#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate companion files for screenA of the idr0078 study.

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


def get_html_color(r, g, b):
    import int
    return int.from_bytes((r, g, b, 255), byteorder='big', signed=True)


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
            name = "Well %s%s Field %s" % (
                string.ascii_uppercase[row - 1], column, field + 1)
            image = Image(
                name, 1305, 879, 5, 3, 1,
                order="XYCZT", type="uint16")
            # Populate pixel size (in microns)
            image.data['Pixels']['PhysicalSizeX'] = '0.1076'
            image.data['Pixels']['PhysicalSizeY'] = '0.1076'
            image.add_channel("Sla1-GFP", get_html_color(0, 255, 0))
            image.add_channel("Sac6-tdTomato", get_html_color(255, 0, 0))
            image.add_channel("Dextran", get_html_color(255, 255, 255))
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
