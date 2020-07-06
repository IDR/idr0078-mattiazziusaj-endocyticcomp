#! /usr/bin/env python

SECONDARY_PATH = (
    "idr0078-mattiazziusaj-endocyticcomp/20200204-rsync/raw/secondary")


from os.path import abspath, dirname, join

scripts_dir = dirname(abspath(__file__))
screenB_plates = "%s/screenB/idr0078-screenB-plates.tsv" % dirname(scripts_dir) 

with open(join(scripts_dir, 'screenB_index_list.txt'), 'r') as f:
    lines = [x.rstrip() for x in f.readlines()]

with open(screenB_plates, 'w') as f:
    for line in lines:
        split_path = line.split('_')
        if len(split_path) == 5:
            plate_name = "_".join(split_path[0:4])
            index_path = split_path[0] + "/" + split_path[1] + "/" + split_path[2] + "_" + split_path[3] + "/" + split_path[4]
        else:
            plate_name = "_".join(split_path[0:3])
            index_path = "/".join(split_path)
        plate_path = "/uod/idr/filesets/%s/%s" % (SECONDARY_PATH, index_path)
        print("ln -sfv ../../../../../../20200626-gdrive/%s"
              " /nfs/bioimage/drop/%s/%s" % (
             line, SECONDARY_PATH,index_path))
        f.write("%s\t%s\n" % (plate_name, plate_path))