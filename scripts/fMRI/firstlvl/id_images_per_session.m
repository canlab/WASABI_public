function id_images_per_session(fmri_data)

    % Problem with this right now is that different nifti images can have a different number of images.
    fmri_data.images_per_session = [];
    for k=1:size(fmri_data.image_names, 1)
        fmri_data.images_per_session = [fmri_data.images_per_session sum(contains(cellstr(fmri_data.fullpath),strtrim(fmri_data.image_names(k,:))))];
        disp(['Run ', num2str(k), ': ', fmri_data.image_names(k,:), ' has ', num2str(sum(contains(cellstr(fmri_data.fullpath),strtrim(fmri_data.image_names(k,:))))), ' images.']);
    end

end