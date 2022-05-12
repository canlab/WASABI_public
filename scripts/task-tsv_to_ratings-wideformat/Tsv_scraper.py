import os
import sys

# Authors: Claire Collins and Malka Hershkop
# Instructions: code scrapes neccesary data from a directory of subdirectories which contain .tsv files
# .tsv files must have uniform structure in both filename and data structure
# (note this code can be easily adjusted if initial files are .csv as long as initial format remains)
#gets relative directory path from command line argument in form: Python3 Tsv_scraper.py <directory_path>
write_location = 'ratings.csv' #sets name of file to write entries in
w = open(write_location, 'a') #opens above mentioned file
def read_tsv(filename):
    global w
    data = filename.split('_')  #
    header = data[0] + ',' + data[1] + ',' + data[3][4:] + ',' + data[4] + ','
    f_proper = os.path.join(directory, filename)
    f = open(f_proper, "r")
    f.readline()  # gets rid of header
    temps = []
    end = ''
    for line in f:
        line = line.strip()
        line = line.split('\t')
        if line[-1][0].isnumeric() and line[1] not in ['Valence Rating:', 'Intensity Rating:', 'Comfort Rating:']:
            num = float(line[-1])
            if num > 30 and num not in temps:
                temps.append(num)
        elif line[1] in ['Valence Rating:', 'Intensity Rating:', 'Comfort Rating:']:
            end += line[1] + ',' + str(line[-1]) + ','
    w.write(header + str(min(temps)) + ',' + str(max(temps)) + ',' + end + '\n')
    f.close()


os.chdir(sys.argv[1]) #gets the path of the directory the python script is sitting in
rootdir = os.getcwd()

for rootdir, dirs, files in os.walk(rootdir): #collects all files and subdirectory in current directory
    for subdir in dirs: #runs on only subdirectory
        directory=os.path.join(rootdir, subdir) #gets path of current subdirectory
        for filename in os.listdir(directory): #gets all files in subdirectory and runs through them
            if filename[-4:len(filename)] != '.tsv': #if file is not a .tsv file, prints to console (for debugging)
                print(filename,': is not a run')
                continue
            read_tsv(filename)

w.close()