function DAT = create_fmridat_fromdir(dir_obj)
    names = {};
    for i=1:length(dir_obj)
        % Ensure we are concatenating only .nii files and unzipping .nii.gz
        % files first
        [filepath, filename, fileext]=fileparts(dir_obj(i).name);
        if contains(fileext,'.gz') && ~exist(fullfile(filepath,filename))
            tic
            gunzip(fullfile(dir_obj(i).folder,dir_obj(i).name), dir_obj(i).folder);
            toc
            % Wait for the file to fully unzip
            while ~exist(fullfile(fullfile(dir_obj(i).folder,filename)))
                pause(1);
            end
        end
        names{end+1} = [dir_obj(i).folder, filesep, erase(dir_obj(i).name,'.gz')];
    end
    DAT = fmri_data(names);
end