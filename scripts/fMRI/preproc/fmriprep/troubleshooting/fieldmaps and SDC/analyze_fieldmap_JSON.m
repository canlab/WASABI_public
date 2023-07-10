% Code by Michael Sun, 04/06/2022
% The following code mines a directory of BIDS *.json files for fieldmap
% IntendedFor fields.


%% Select the starting directory, pick either a raw or derivative BIDS directory ideally
%cd '\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\dup files'
% cd /Volumes/WASABI/scripts/derivatives/fmriprep/lesion
% cd '\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\lesion-datasets\'
% cd '\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\1080_wasabi'
cd(strrep('\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\1080_wasabi', '\', '/'));
%% Use this to search through derivatives
% files = dir('**\*fieldmap.json')    % recursively search through the directories
%% Use this to search through raw BIDS
files = dir('**\*epi.json')

files = dir(['**', filesep, '*epi.json'])
%% Start the mining:
val = {}
for i= 1:length(files)    
    fname = [files(i).folder,filesep,files(i).name]; 
    fid = fopen(fname); 
    raw = fread(fid,inf); 
    str = char(raw'); 
    fclose(fid); 
    val{end+1} = jsondecode(str);
    if isfield(val{i}, 'IntendedFor')
        if ~isempty(val{i}.IntendedFor)
            disp([files(i).name, ' IntendedFor status is: ' newline, sprintf('\t'), strjoin(val{i}.IntendedFor', ', \n\t')])
        else
            disp([files(i).name, ' no files listed in IntendedFor'])
        end
    else
        disp([files(i).name, ' does not have the field IntendedFor'])
    end
end


% fmap images look like *acq-mb8_dir-ap_epi.nii.gz; *acq-mb8_dir-pa_epi.nii.gz 