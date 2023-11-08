function DSGN = generateDSGN(funcs, fmriprep_dir, task)    
    
    % 1. Set up directories and paths
    root=fileparts(funcs(1).folder);
    % fmriprep_dir='/dartfs-hpc/rc/lab/C/CANlab/labdata/data/WASABI/derivatives/fmriprep/'
    % 2. Extract session, subject, and task information
    [sub, sess, run, ~] = getBIDSSubSesRunTask(funcs(1).name);
    disp(['Currently processing sub-', sub, '_ses-',sess,'_run-',run, '_task-', task]);
    % 3. Set up metadata
    DSGN = setupMetadata(sub, sess, task, funcs);
    % 4. Set up directories
    DSGN = setupDirectories(root, fmriprep_dir, sub, task, DSGN);
    % 5. Set up design parameters
    DSGN = setupDesignParameters(DSGN);
    % 6. Process functional runs
    DSGN = processFunctionalRuns(funcs, task, sub, sess, DSGN);
    % 7. Save the resulting DSGN
    save(fullfile(DSGN.modeldir,[task,'DSGN.mat']),'DSGN');
end

function [sub, sess, run, task] = getBIDSSubSesRunTask(funcName)
    sub = char(extractBetween(funcName, "sub-", "_ses"));
    sess = char(extractBetween(funcName, "ses-", "_task"));
    run = char(extractBetween(funcName, "ses-", "_task"));
    task = char(extractBetween(funcName, "task-", "_"));
end

function DSGN = setupMetadata(sub, sess, task, funcs)
    if length(funcs) == 1
        run = char(extractBetween(funcs(1).name, "run-", "_space"));
        DSGN.metadata = sprintf('sub-%s ses-%s task-%s run-%s design structure', sub, sess, task, run);
    elseif length(funcs) > 1
        runMin = char(extractBetween(funcs(1).name, "run-", "_space"));
        runMax = char(extractBetween(funcs(end).name, "run-", "_space"));
        DSGN.metadata = sprintf('sub-%s ses-%s task-%s runs-%s-%s design structure', sub, sess, task, runMin, runMax);
    end
end

function DSGN = setupDirectories(firstlvl_funcdir, fmriprep_dir, sub, run, task, DSGN)
    DSGN.modeldir = fullfile(firstlvl_funcdir, 'firstlvl', task);
    DSGN.subjects = {fullfile(fmriprep_dir, ['sub-', sub])};
    DSGN.funcnames = {};
    DSGN.conditions = {}; 
    DSGN.modelingfilesdir = sprintf('sub-%s_task-%s_firstlvl', sub, task);  % This folder gets appended to every session folder

    % Create folder to dump betas into
    if ~isfolder(DSGN.modeldir)
        mkdir(DSGN.modeldir)
    end

    % Create folder to dump regressor structs into
    if ~isfolder(DSGN.modelingfilesdir)
        mkdir(fullfile(firstlvl_funcdir, ['run-', run], DSGN.modelingfilesdir))
    end

end

function DSGN = setupDesignParameters(DSGN)
    % USER PLEASE ADJUST THESE:

    % Some reasonable defaults:
    DSGN.allowmissingfunc = true;
    DSGN.multireg = 'noise_model.mat'; % name of the things regressed out during preproc
    DSGN.allowmissingcondfiles = true;
    DSGN.notimemod = true; % provided by Bogdan
    DSGN.allowemptycond = true; % Not all condition combinations are present in every run.

    % Study-Specific:
    DSGN.tr = 0.46;
    DSGN.hpf = 180; % roughly 1/2 scan time
    DSGN.fmri_t0 = 8; % no idea what to set this to, we don't do slice timing correction
    % LABGAS does 15
    % DSGN.fmri_t = 30;
    DSGN.fast = true;
    DSGN.ar1 = false;
%     DSGN.convolution.type; default hrf, which means canonical hrf - other options: fir, spline (the latter is not yet implemented @LaBGAS, help needed from Tor/Martin/Bogdan)
%     DSGN.convolution.time; default 0, which means no time derivative
%     DSGN.convolution.dispersion: default 0, which means no dispersion derivative
%     DSGN.ar1 = false; % autoregressive AR(1) to model serial correlations; SPM default is true, CANlab default is false, Tor recommends turning autocorrelation off, because this algorithm pools across the whole brain, and does not perform well in some situations; if you are performing a group analysis, the autocorrelation problem is not as concerning
%     DSGN.singletrials = {{}}; % a cell array (1 cell per session) of cell arrays (1 cell per condition) of (corresponding to DSGN.conditions) of true/false values indicating whether to convert specified condition to set of single trial conditions
%     DSGN.singletrialsall = false; % default: false; if true, set DSGN.singletrials to true for all conditions
%     DSGN.allowemptycond = false; % default:false; if true, allow empty conditions
%     DSGN.allowmissingcondfiles = false; % default:false; if true, throw warning instead of error when no file(s) are found corresponding to a MAT-file name/wildcard
%    DSGN.multireg = 'noise_regs'; % specify name for matfile with noise parameters you want to save


    % cell array (one cell per session) of cell arrays (one cell per condition) of cell arrays (one cell per modulator) of MAT-file names; set to {{}} if you don't want parametric modulators
%     c=0;
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};
%     c=c+1;DSGN.pmods{c}={'liking_sucrose' 'liking_erythritol' 'liking_sucralose' 'liking_water'};


end

function [DSGN, R] = processFunctionalRuns(funcs, task, sub, sess, DSGN)
    for i = 1:length(funcs)
        [sub, sess, run, ~] = getBIDSSubSesRunTask(funcs(i).name);

        % 1. Find the *_events.tsv file
        events_fname = fullfile(funcs(i).folder, '*_events.tsv');
        events_tsv = dir(events_fname);
        events_dat = importBIDSfile(fullfile(events_tsv.folder, events_tsv.name));

        DSGN.funcnames{end+1}=fullfile(['ses-' sess], 'func', ['run-', run], [erase(funcs(i).name, '.gz')]);  % Make sure you are only adding relative paths starting with session number the files you are adding are .nii and not .nii.gz
        model_path = fullfile(funcs(i).folder, [DSGN.modelingfilesdir filesep]);
        
        % 2. Find noise related files for the func
        noise_fname = fullfile(funcs(i).folder, '*confounds_timeseries.tsv');
        noise_tsv = dir(noise_fname);   % confounds_timseries.tsv regular expression search string.
        noise_dat = importBIDSfile(fullfile(noise_tsv.folder, noise_tsv.name));
        
        % 3. Generate RMSSD/DVARS Image-wise Nuisance Indicator vectors
        % Please note, fmriprep confounds include regressors for dvars,
        % framewise_displacement, rmsd, motion_outlier* and I am not sure
        % how well they compare with our rmssd methods so they are not used for now.
        if isfile([erase(funcs(i).name, '.nii'), '.mat'])
            load([erase(funcs(i).name, '.nii'), '.mat']);
        else
            image = fmri_data(fullfile(funcs(i).folder, funcs(i).name));
            save([erase(funcs(i).name, '.nii') '.mat'], 'image', '-mat');
        end
    
        R_spikes=[];
        [D2, D2_expected, pval, wh_outlier_uncorr, wh_outlier_corr] = mahal(image, 'noplot');
        outlier_index=find(wh_outlier_uncorr==1);     % You can toggle between the two: corrected or uncorrected outliers.
        % outlier_index=find(wh_outlier_corr==1);
        if length(outlier_index)>0
           for covi=1:length(outlier_index)
              A=zeros(1,size(image.dat,2));
              A(outlier_index(covi))=1;   %%%%% Outlier regressor e.g [0 0 0 0 0 0 1 0 0 0 0 0 ....]
              R_spikes=[R_spikes A'];
           end
        end
    
        if isfile(['sub-' sub '_ses-' sess '_task-' task '_run-' run '_rmssd-movie.tiff'])
            [rmssd, rmssd_outlier_regressor_matrix] = rmssd_movie(image, 'nomovie');
        else
            [rmssd, rmssd_outlier_regressor_matrix] = rmssd_movie(image, 'writetofile', 'movieoutfile', ['sub-' sub '_ses-' sess '_task-' task '_run-' run '_rmssd-movie.tiff']);
        end
        R_dvars = rmssd_outlier_regressor_matrix;  % save these
        R = [R_spikes R_dvars];
    
        % 4. Generate regressors. Call a generate_WASABI_regressors function to do most of the heavy lifting.
        DSGN.conditions{end+1}=generate_regressors(task, sub, sess, events_dat, noise_dat, R, model_path)

        % 5. Generate contrasts. Call generate_WASABI_contrasts function to do most of the heavy lifting.
        [DSGN.contrasts, DSGN.contrastweights, DSGN.contrastnames] = generate_contrasts(task);
    end
end
