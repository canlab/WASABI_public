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
% subs=canlab_list_subjects(firstlvl_derivdir, 'sub-*');
% 
% for sub=1:numel(subs)
%     sess{sub}=canlab_list_subjects(fullfile(firstlvl_derivdir, subs{sub}), 'ses-*');
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

fmriprep_derivdir='\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives'
bidsroot='\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\1080_wasabi'

function WASABI_genfirstlvlDSGNs(fmriprep_derivdir, bidsroot, varargin)
    % Step 1: Put in a firstlvl_derivdir full path.
    % Step 2: 

    if ~exist(fmriprep_derivdir, 'dir')
        error('No fmriprep directory named fmriprep...Cannot find or create firstlvl_derivdir. Run canlab_prep_bidsdir() first to create a first level directory.');
    else
        firstlvl_derivdir = fullfile(fmriprep_derivdir, 'canlab_firstlvl')
        if ~exist(firstlvl_derivdir, 'dir')
            warning('no canlab_firstlvl directory found. Creating one from fmriprep derivatives.')
            canlab_prep_bidsdir(fmriprepdir, 'datatype', 'func', 'outdir', firstlvl_derivdir);
        end
    end

    % Parse varargin for task, space, and subs
    p = inputParser;
    addOptional(p, 'task', '', @ischar);
    addOptional(p, 'space', 'MNI152NLin2009cAsym', @ischar);
    addOptional(p, 'subs', {}, @iscell);
    parse(p, varargin{:});

    task = p.Results.task;
    space = p.Results.space;
    subs = p.Results.subs;

    % Defaults for tasks
    if isempty(task)
        tasks = dir(fullfile(bidsroot, 'task-*'));
        tasks = extractBetween({tasks.name}, 'task-', '_');
        if isempty(tasks)
            error('No tasks identified.');
        end
    else
        tasks = {task}; % If task is specified, use it directly
    end

    % Default for subs if not provided
    if isempty(subs)
        subs = canlab_list_subjects(fullfile(firstlvl_derivdir), 'sub-*');
    end

    % Define the list of allowed templateflow standard spaces
    allowedSpaces = {'MNI152Lin', 'MNI152NLin2009cAsym', 'MNI152NLin6Asym', ...
                     'MNI152NLin6Sym', 'MNIInfant', 'MNIPediatricAsym', ...
                      'NKI', 'OASIS30ANTs', 'PNC', 'fsLR', 'fsaverage', ...
                      'anat', 'T1w', 'run', 'func', 'sbref', 'fsnative', ...
                      'template', 'fsnative', 'fsaverage6', 'fsaverage5'}; 
                        % Add all required standard spaces here
    
    % Check if provided space is one of the allowed spaces
    if ~ismember(space, allowedSpaces)
        error('The specified space "%s" is not one of the allowed templateflow standard spaces.', space);
    end


    for sub = 1:numel(subs)
        sessions=canlab_list_subjects(fullfile(firstlvl_derivdir, subs{sub}), 'ses-*');
        for ses=1:numel(sessions)
            disp(['Processing images for ', subs{sub}, ' ', sessions{ses}]);
            
            % List out all of the functional scans in the MNI Space for each task
            
            % ses_funcs = dir('*MNI*preproc_bold.nii.gz');
            % movemap_funcs = dir('*task-movemap*MNI*preproc_bold.nii.gz');                   % List out all of the functional scans in MNI space
            % bodymap_funcs = dir('*task-bodymap*MNI*preproc_bold.nii.gz');                   % List out all of the functional scans in MNI space
            % pinel_funcs = dir('*task-pinel*MNI*preproc_bold.nii.gz');                       % List out all of the functional scans in MNI space
            % distractmap_funcs = dir('*task-distractmap*MNI*preproc_bold.nii.gz');           % List out all of the functional scans in MNI space
            % acceptmap_funcs = dir('*task-acceptmap*MNI*preproc_bold.nii.gz');               % List out all of the functional scans in MNI space
            % hyperalignment_funcs = dir('*task-hyperalignment*MNI*preproc_bold.nii.gz');     % List out all of the functional scans in MNI space
            
            % For each subject: All funcs in the session:
            ses_funcs = filenames(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, '**', ['*' space, '*desc-preproc_bold.nii.gz']));
            
            
            
            ses_funcs(find(contains(ses_funcs, task)))


            % Plot Session-Montage Comparison
            % For sessions involving multiple runs, Use plot montage to compare the runs for any potential troubleshooting
            if(size(ses_funcs, 1) > 1 & ~exist([subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig'], 'file'))
                % ses_objs=create_fmridat_fromdir(ses_funcs); % This command takes a long time remotely. Best to run this directly on the cluster.
                ses_objs=fmri_data(ses_funcs{1});
                fmri_data('\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\canlab_firstlvl\sub-SID000002\ses-01\func\run-01\sub-SID000002_ses-01_task-movemap_acq-mb8_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz')
                % Hopefully this is now implemented into fmri_data/plot()
                
                if size(ses_objs.image_names, 1) > 1
                    ses_objs=id_images_per_session(ses_objs);
                    plot(ses_objs, 'montages', 'noorthviews', 'nooutliers') % Would be better if we can relabel these?
                    fig = gcf;
                    exportgraphics(fig, fullfile(firstlvl_derivdir, subs{sub}, sessions{ses},[subs{sub}, '_', sessions{ses}, '_run-comparison-plot.png']));
                    savefig(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, [subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig']));
                end
            end
            
            % For each subject's session:
            
            % DSGN_process_job(tasks)
            for t = 1:numel(tasks)
                funcs=dir(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses},'func', '**', ['*',tasks{t},'*']));
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
                    savefig(fig, [subs{sub}, '_', sessions{ses}, '_', tasks{t},'_run-comparison-plot.fig']);
                    exportgraphics(fig, [subs{sub}, '_', sessions{ses}, '_', tasks{t},'_run-comparison-plot.png']);
            
                else
                    % If there is no matching task, then display this message:
                    disp(['No ', tasks{t}, ' runs in this session.']);
            
                end
            
                close all;
            
            
            end
        end
    end

end

% diary off;