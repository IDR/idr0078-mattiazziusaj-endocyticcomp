#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import argparse
import logging
import xml.etree.ElementTree as ElementTree

FILESET_PATH = (
    "/uod/idr/filesets/idr0078-mattiazziusaj-endocyticcomp/20200707-ometiff/")

NS = {'OME': "http://www.openmicroscopy.org/Schemas/OME/2016-06"}
ElementTree.register_namespace("", NS['OME'])


def find_missing_elements(tree):
    root = tree.getroot()
    # Find images with empty TiffData elements
    images = []
    for i in root.findall('OME:Image', NS):
        for p in i.findall('OME:Pixels', NS):
            for t in p.findall('OME:TiffData', NS):
                if list(t) == []:
                    images.append(i.attrib['ID'])

    # Find associated well samples
    wellsamples = []
    for p in root.findall('OME:Plate', NS):
        for w in p.findall('OME:Well', NS):
            for ws in w.findall('OME:WellSample', NS):
                for i in ws.findall('OME:ImageRef', NS):
                    if i.attrib['ID'] in images:
                        wellsamples.append(ws.attrib['ID'])
    return images, wellsamples


def remove_and_reindex(tree, images, wellsamples):
    root = tree.getroot()

    # Remove missing well samples and reindex remaining well samples/image
    # references
    ws_incr = 0
    for p in root.findall('OME:Plate', NS):
        for w in p.findall('OME:Well', NS):
            for ws in w.findall('OME:WellSample', NS):
                if ws.attrib['ID'] in wellsamples:
                    logging.debug('Removing %s' % ws.attrib['ID'])
                    w.remove(ws)
                    ws_incr = ws_incr + 1
                elif ws_incr > 0:
                    logging.debug('Reindexing %s' % ws.attrib['ID'])
                    new_index = int(ws.attrib['Index']) - ws_incr
                    ws.set('Index', str(new_index))
                    for i in ws.findall('OME:ImageRef', NS):
                        new_index = int(i.attrib['ID'][6:]) - ws_incr
                        i.set('ID', "Image:%s" % new_index)
        for pa in p.findall('OME:PlateAcquisition', NS):
            for ws in pa.findall('OME:WellSampleRef', NS):
                if ws.attrib['ID'] in wellsamples:
                    logging.debug('Removing %s' % ws.attrib['ID'])
                    pa.remove(ws)

    # Remove missing images and reindex remaining Image/Pixel/Channel elements
    image_incr = 0
    for i in root.findall('OME:Image', NS):
        if i.attrib['ID'] in images:
            logging.debug('Removing %s' % i.attrib['ID'])
            root.remove(i)
            image_incr = image_incr + 1
        elif image_incr > 0:
            logging.debug('Reindexing %s' % i.attrib['ID'])
            new_index = int(i.attrib['ID'][6:]) - image_incr
            i.set('ID', "Image:%s" % new_index)
            for p in i.findall('OME:Pixels', NS):
                p.set('ID', "Pixels:%s" % new_index)
                for c in p.findall('OME:Channel', NS):
                    channel_index = int(c.attrib['ID'][-1:])
                    c.set('ID', "Channel:%s:%s" % (new_index, channel_index))
    logging.info('Removed %s images and %s well samples' % (
        image_incr, ws_incr))
    return tree


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--quiet', '-q', action='count', default=0)
    parser.add_argument('file', type=str)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO - 10 * args.verbose + 10 * args.quiet)

    logging.info('Opening %s' % args.file)
    with open(args.file, 'r') as f:
        tree = ElementTree.parse(f)

    images, wellsamples = find_missing_elements(tree)
    tree = remove_and_reindex(tree, images, wellsamples)
    tree.write(args.file, encoding='UTF-8', xml_declaration=True)
