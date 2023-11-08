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
if isunix
    fmriprep_derivdir=strrep(fmriprep_derivdir, '\', '/')
    bidsroot=strrep(bidsroot, '\', '/')
end

space='MNI152NLin2009cAsym'

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
    tasks = dir(fullfile(bidsroot, 'task-*'));
    tasks = extractBetween({tasks.name}, 'task-', '_');
    if isempty(tasks(contains(tasks, task)))
        error(['No tasks identified with keyword ' task]);
    else
        tasks=task;
    end


    % Default for subs if not provided
    if isempty(subs)
        subs = canlab_list_subjects(firstlvl_derivdir, 'sub-*');
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

            % For each subject: All funcs in the session:
            % ses_funcs = filenames(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, '**', ['*' space, '*desc-preproc_bold.nii.gz']));
            ses_funcs = dir(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, '**', ['*' space, '*desc-preproc_bold.nii.gz']));
            ses_funcs = fullfile({ses_funcs(:).folder}', {ses_funcs(:).name}');
            
            % Plot Session-Montage Comparison
            % For sessions involving multiple runs, Use plot montage to compare the runs for any potential troubleshooting
            if(size(ses_funcs, 1) > 1 && ~exist([subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig'], 'file'))
                % ses_objs=create_fmridat_fromdir(ses_funcs); % This command takes a long time remotely. Best to run this directly on the cluster.
                try
                    ses_objs=fmri_data(ses_funcs);
                catch
                    error(['Unable to generate fmri_data objects from ' ses_funcs '. Perhaps they are symlinks generated from a different operating system.'])
                end
                % Hopefully this is now implemented into fmri_data/plot()
                
                if size(ses_objs.image_names, 1) > 1
                    ses_objs=id_images_per_session(ses_objs);
                    plot(ses_objs, 'montages', 'noorthviews', 'nooutliers')
                    fig = gcf;
                    exportgraphics(fig, fullfile(firstlvl_derivdir, subs{sub}, sessions{ses},[subs{sub}, '_', sessions{ses}, '_run-comparison-plot.png']));
                    savefig(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, [subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig']));
                end
            end
            close all
            
            % For each subject's session:
            
            % DSGN_process_job(tasks)
            for t = 1:numel(tasks)
                funcs=dir(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses},'func', '**', ['*',tasks{t},'*desc-preproc_bold*']));
                
                if ~isempty(funcs) % If there are scans the pertain to the task
                    % 1. Generate a DSGN structure for that task and make a folder to
                    % house the .mat file it will reside in.
                    DSGN=generateDSGN(funcs);
            
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