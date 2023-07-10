% Code by Michael Sun, 10/30/2021
% The following code mines a directory of BIDS *.json files for headcoil
% information. HEA stands for anterior headcoil. HEP is posterior. The lack
% of HEA can lead to frontal lobe noise distortion and blurrier images.

% cd \\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\fmriprep\lesion

% EDIT: cd to your BIDS directory
% cd /Volumes/WASABI/1080_wasabi.lesion-reckless.1
cd /Volumes/WASABI/lesion-datasets
% cd /Volumes/WASABI/1080_wasabi

% ** recursively goes through all subdirectories
% files = dir('**/*bold.json')
files = dir('**/*T1w.json')
val = {}
for i= 1:length(files)    
    fname = [files(i).folder, filesep, files(i).name]; 
    fid = fopen(fname); 
    if fid~=-1
        raw = fread(fid,inf); 
        str = char(raw'); 
        fclose(fid); 
        val{end+1} = jsondecode(str);
        if isfield(val{end}, 'ReceiveCoilActiveElements')
            disp([fname, ' headcoil status is: ', val{end}.ReceiveCoilActiveElements])
        else
            disp([fname, ' does not have the field ReceiveCoilActiveElements'])
        end
    end
end