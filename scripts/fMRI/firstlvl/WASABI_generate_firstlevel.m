% canlab_glm_subject_levels_BIDS
% A wrapper for running first-level GLMs on a BIDS derivative directory
% with preproc_bold.nii.gz files, using canlab_glm_subject_levels.

% The logic of first-level GLM in WASABI is that first-level beta estimates
% should be estimated for each subject's session-level to best manage
% storage space and computational time concerns.


% Does 2 Things:
% 1. Plots a Session-Montage Comparison
% 2. a. Generates a DSGN structure for each session
%    b. Create an fmri_data object from these task scans and compare the
%       mean EPIs across the run for the task.
%   c. Save all your files.


% Start a log
% diary(fullfile('firstlvl_generate_2.log');
% 
% 
% subs=canlab_list_subjects(bidsdir, 'sub-*');
% 
% for sub=1:numel(subs)
%     sess{sub}=canlab_list_subjects(fullfile(bidsdir, subs{sub}), 'ses-*');
% end
% 
% tasks=dir('task-*');
% tasks=erase({tasks}, {'task-','.json'});
% 
% % Build a FUNCS structure
% FUNCS.tasks=tasks;
% FUNCS.subjects=subs;
% FUNCS.sessions=sess;
% % FUNCS.runs=runs;
% FUNCS.funcs;



function WASABI_genfirstlvlDSGNs(bidsdir, subs)
    cd(fullfile(bidsdir,subs))
    
    tasks=dir('task-*');
    tasks=erase({tasks}, {'task-','.json'});
    sess=canlab_list_subjects(fullfile(bidsdir, subs), 'ses-*');

    for i=1:numel(sess)
        % Try not to cd, instead directly access the folder.
        disp(['Processing images for ', subs, '_', sess(i)]);
        
        % List out all of the functional scans in the MNI Space for each task
        
        % ses_funcs = dir('*MNI*preproc_bold.nii.gz');
        % movemap_funcs = dir('*task-movemap*MNI*preproc_bold.nii.gz');                   % List out all of the functional scans in MNI space
        % bodymap_funcs = dir('*task-bodymap*MNI*preproc_bold.nii.gz');                   % List out all of the functional scans in MNI space
        % pinel_funcs = dir('*task-pinel*MNI*preproc_bold.nii.gz');                       % List out all of the functional scans in MNI space
        % distractmap_funcs = dir('*task-distractmap*MNI*preproc_bold.nii.gz');           % List out all of the functional scans in MNI space
        % acceptmap_funcs = dir('*task-acceptmap*MNI*preproc_bold.nii.gz');               % List out all of the functional scans in MNI space
        % hyperalignment_funcs = dir('*task-hyperalignment*MNI*preproc_bold.nii.gz');     % List out all of the functional scans in MNI space
        
        % For each subject: All funcs in the session:
        ses_funcs = dir('*MNI*preproc_bold.nii.gz');
        
        % Plot Session-Montage Comparison
        % For sessions involving multiple runs, Use plot montage to compare the runs for any potential troubleshooting
        if(size(ses_funcs, 1) > 1 & ~exist([subs, '_', sess(i), '_run-comparison-plot.fig'], 'file'))
            ses_objs=create_fmridat_fromdir(ses_funcs);
            % Hopefully this is now implemented into fmri_data/plot()
            
            if size(ses_objs.image_names, 1) > 1
                ses_objs=id_images_per_session(ses_objs);
                plot(ses_objs, 'montages', 'noorthviews', 'nooutliers') % Would be better if we can relabel these?
                fig = gcf;
                exportgraphics(fig, [subs, '_', sess(i), '_run-comparison-plot.png']);
                savefig([subs, '_', sess(i), '_run-comparison-plot.fig']);
            end
        end
        
        % For each subject's session:
        
        % DSGN_process_job(tasks)
        for t = 1:numel(tasks)
            funcs=dir(fullfile('session-folder','funcs',tasks{t}));
            if ~isempty(funcs) % If there are scans the pertain to the task
                % 1. Generate a DSGN structure for that task and make a folder to
                % house the .mat file it will reside in.
                DSGN=generateDSGN(funcs);
                if ~isfolder(DSGN.modeldir)
                    mkdir(DSGN.modeldir);
                end
        
                % 2. Create and fmri_data object from those task scans, and compare
                % the mean EPIs across each run for the task
                for k=1:length(funcs)
                    msg = [char(extractBetween(funcs(k), 'sub-','_ses')), '''s Session ', char(extractBetween(funcs(k), 'ses-','_task')), ', Run number ', char(extractBetween(movemap_funcs(k), 'run-','_space')), ' is a ', tasks{t}, '.'];
                    disp(msg);
                end
                disp([num2str(length(funcs)), ''' functional ', tasks{t}, ' run(s).']);
                func_objs=create_fmridat_fromdir(funcs);
        
                func_objs.images_per_session = [];
                for k=1:size(func_objs.image_names, 1)
                    func_objs=id_images_per_session(func_objs);
                    disp(['Run ', num2str(k), ': ', func_objs.image_names(k,:), ' has ', num2str(sum(contains(cellstr(func_objs.fullpath),strtrim(func_objs.image_names(k,:))))), ' images.']);
                end
                plot(func_objs, 'montages', 'noorthviews', 'nooutliers') % Would be better if we can relabel these? New changes to plot should have better labels
                fig = gcf;
        
                % 3. Generate a metadata table
                % Metadata table should contain...list of DSGNs? 

        
                % 4. Save all your files
                save(fullfile(DSGN.modeldir,[tasks{t},'DSGN.mat']),'DSGN');
                save([tasks{t}, '_objs'], [tasks{t}, '_objs'], '-v7.3');
                savefig(fig, [subs, '_', sess(i), '_', tasks{t},'_run-comparison-plot.fig']);
                exportgraphics(fig, [subs, '_', sess(i), '_', tasks{t},'_run-comparison-plot.png']);
        
            else
                % If there is no matching task, then display this message:
                disp(['No ', tasks{t}, ' runs in this session.']);
        
            end
        
            close all;
        
        
        end
    end

end

% diary off;


function id_images_per_session(fmri_data)

    % Problem with this right now is that different nifti images can have a different number of images.
    fmri_data.images_per_session = [];
    for k=1:size(fmri_data.image_names, 1)
        fmri_data.images_per_session = [fmri_data.images_per_session sum(contains(cellstr(fmri_data.fullpath),strtrim(fmri_data.image_names(k,:))))];
        disp(['Run ', num2str(k), ': ', fmri_data.image_names(k,:), ' has ', num2str(sum(contains(cellstr(fmri_data.fullpath),strtrim(fmri_data.image_names(k,:))))), ' images.']);
    end

end