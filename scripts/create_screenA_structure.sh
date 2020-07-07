#! /usr/bin/env sh
# Create a secondary structure

set -u
set -e

mkdir -p 20200707-ometiff/Sac6-tdTomato
mkdir -p 20200707-ometiff/Sla1-yEGFP
mkdir -p 20200707-ometiff/Snf7-yEGFP
mkdir -p 20200707-ometiff/Vph1-yEGFP

cd  20200707-ometiff/Sac6-tdTomato/
for i in $(ls ../../20200204-rsync/raw/GW/Sac6-tdTomato/); do mkdir $i; done
rmdir 10_2 S1_2 TS1-37_2 TS2-37_2
for i in $(ls .); do (cd $i && ln -sv ../../../20200204-rsync/raw/GW/Sac6-tdTomato/$i/* .); done
(cd 10/ && ln -sv ../../../20200204-rsync/raw/GW/Sac6-tdTomato/10_2/* .)
(cd S1/ && ln -sv ../../../20200204-rsync/raw/GW/Sac6-tdTomato/S1_2/* .)
(cd TS1-37/ && ln -sv ../../../20200204-rsync/raw/GW/Sac6-tdTomato/TS1-37_2/* .)
(cd TS2-37/ && ln -sv ../../../20200204-rsync/raw/GW/Sac6-tdTomato/TS2-37_2/* .)

cd ../Sla1-yEGFP/
for i in $(ls ../../20200204-rsync/raw/GW/Sla1-yEGFP/); do mkdir $i; done
for i in $(ls .); do (cd $i && ln -sv ../../../20200204-rsync/raw/GW/Sla1-yEGFP/$i/* .); done

cd ../Snf7-yEGFP/
for i in $(ls ../../20200204-rsync/raw/GW/Snf7-yEGFP/); do mkdir $i; done
for i in $(ls .); do (cd $i && ln -sv ../../../20200204-rsync/raw/GW/Snf7-yEGFP/$i/* .); done

cd ../Vph1-yEGFP/
for i in $(ls ../../20200204-rsync/raw/GW/Vph1-yEGFP/); do mkdir $i; done
rmdir rmkDM_2
for i in $(ls .); do (cd $i && ln -sv ../../../20200204-rsync/raw/GW/Vph1-yEGFP/$i/* .); done
(cd rmkDM/ && ln -sv ../../../20200204-rsync/raw/GW/Vph1-yEGFP/rmkDM_2/* .)
