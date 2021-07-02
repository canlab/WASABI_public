@echo off
set /p id="Enter Dartmouth ID: "

SET CMD="rsync -rltv /mnt/c/Users/Dartmouth/Documents/GitHub/canlab/WASABI_public %id%@discovery7.dartmouth.edu:/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/"

bash -c %CMD%



