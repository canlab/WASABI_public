function run_firstlevel_DSGN(firstlvl_dir, task, sub, sess, events_dat, noise_dat, R, mdl_path, varargin)
    DSGN_objs=dir(fullfile(firstlvl_dir, '**/firstlvl/bodymap*/*.mat'))
    
    % Remove DSGN Objects you don't want to process.
    files=fullfile({DSGN_objs(:).folder}', {DSGN_objs(:).name}');
    
    for i = 1:length(files)
        load(files(i));
    %     DSGN=DSGN.(erase(DSGN_objs(i).name, '.mat'))
        % DSGN=DSGN.DSGN;
    
        canlab_glm_subject_levels(DSGN, 'overwrite')
    %     canlab_glm_subject_levels(DSGN, 'onlycons')
    
    end
end