function fdat=id_images_per_session(fdat)

    % Problem with this right now is that different nifti images can have a different number of images.
    fdat.images_per_session = [];
    for k=1:size(fdat.image_names, 1)
        fdat.images_per_session = [fdat.images_per_session sum(contains(cellstr(fdat.fullpath),strtrim(fdat.image_names(k,:))))];
        disp(['Run ', num2str(k), ': ', fdat.image_names(k,:), ' has ', num2str(sum(contains(cellstr(fdat.fullpath),strtrim(fdat.image_names(k,:))))), ' images.']);
    end

    if sum(fdat.images_per_session) > size(fdat.dat,2)
        error('Size mismatch between .image_names and .dat size. Is .image_names set correctly?');
    end

end