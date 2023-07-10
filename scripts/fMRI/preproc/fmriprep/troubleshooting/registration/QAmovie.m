function QAmovie(sub_bids_dir)
    % QA Script for looping through 4-d scans and generating slice_movies for
    % all of a subject's functional scans
    
    % Michael Sun, PhD - 12/17/2021
    
    
    % Requires canlabtools for filenames
    which("filenames")
    % Throw an error if it doesn't find the right filenames.m
    
    % 1. Enter the BIDS directory
    % cd '\\dartfs-hpc\rc\lab\C\CANlab\labdata\projects\WASABI\WASABI_N_of_Few\Michael\bodymap\analysis\data'
    cd(sub_bids_dir)
    % 2. loop through all sessions
    image_names = sort(filenames(fullfile('ses*/func/*bold.nii.gz'), 'absolute'))
    % Unzip them all
    for i = 1:length(image_names)
        gunzip(image_names{i})
    end
    image_names = sort(filenames(fullfile('ses*/func/*bold.nii'), 'absolute'))
    % Better here to do some error checking to see if any files were collected

    % 3. make a QA_movies folder if it exists.
    if ~exist('QA_movies', 'dir')
        mkdir('QA_movies')
    end
    cd 'QA_movies'
    
    image_objs={}
    for i = 1:length(image_names)
        [path, name, ext] = fileparts(image_names{i})
        image_objs{i} = fmri_data(image_names{i})
        slice_movie(image_objs{i}, 'writetofile', 'movieoutfile', [name + "_movie.tiff"])
    end
end
