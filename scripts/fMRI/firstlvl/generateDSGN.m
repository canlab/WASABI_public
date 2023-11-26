function DSGN = generateDSGN(funcs, firstlvl_derivdir, fmriprep_derivdir, task, spike_def, plot)    
    

    %% This is all by-subject

    % 1. Set up metadata
    DSGN = setupMetadata(funcs, task);
    % 2. Set up directories
    DSGN = setupDirectories(firstlvl_derivdir, fmriprep_derivdir, funcs, task, DSGN);
    % 3. Set up design parameters
    DSGN = setupDesignParameters(DSGN);
    % 4. Process functional runs
    DSGN = processFunctionalRuns(funcs, task, spike_def, DSGN);
    % 5. Process functional runs
    % DSGN = configPmods(DSGN);
    % 6. Save the resulting DSGN
    save(fullfile(DSGN.modeldir,[task,'DSGN.mat']),'DSGN');

    % Diagnostic Plots
    if plot==1
        try
            plotDSGN(DSGN);
        % plotPMODS(DSGN)
        catch
            warning(['Problem plotting ' DSGN.modelingfilesdir]);
        end
    end


end

function DSGN = setupMetadata(funcs, task)
    % USER TO EDIT: Field for annotation with study info, or whatever you like
    % Example: DSGN.metadata = "proj-bitter-reward first level analysis model with FID task, i.e. modeling 6 conditions for cues with 0,2 or 10 win, and feedback with 0,2 or 10 win"; 

    % Default:
    % DSGN.metadata = sprintf('First-level DSGN for task-%s', task);

    % For WASABI N-of-Few, dynamic metadata creation:
    if length(funcs) == 1
        [sub, ses, run, ~] = getBIDSSubSesRunTask(funcs(1).name);
        DSGN.metadata = sprintf('sub-%s ses-%s task-%s run-%s design structure', sub, ses, task, run);
    elseif length(funcs) > 1
        [sub, ses, runMin, ~] = getBIDSSubSesRunTask(funcs(1).name);
        [~, ~, runMax, ~] = getBIDSSubSesRunTask(funcs(end).name);
        DSGN.metadata = sprintf('sub-%s ses-%s task-%s runs-%s-%s design structure', sub, ses, task, runMin, runMax);
    end
end

function DSGN = setupDirectories(firstlvl_derivdir, fmriprep_derivdir, funcs, task, DSGN)
    % Directories where you want to write first level results for this model
    % DSGN.modeldir = '/data/proj_bitter-reward/firstlevel/model_2_FID'; % directory where you want to write first level results for this model

    [sub, ses, run, ~]=getBIDSSubSesRunTask({funcs(:).name});
    % sub = cellfun(@(c) c{1}, sub, 'UniformOutput', false); % Flatten the cell array
    % ses = cellfun(@(c) c{1}, ses, 'UniformOutput', false); % Flatten the cell array
    % run = cellfun(@(c) c{1}, run, 'UniformOutput', false); % Flatten the cell array
    sub=cellstr(sub);
    ses=cellstr(ses);
    run=cellstr(run);
    sub=unique(sub);
    ses=unique(ses);
    run=unique(run);
    % task=unique(task); % User may want to mix tasks into one firstlvl model
    
    if numel(sub)>1
        % Are there multiple subjects? If so, then the DSGN should be saved at the firstlvl_derivdir level.
        DSGN.modeldir = fullfile(firstlvl_derivdir, 'firstlvl', task);
        % Create folder to dump regressor structs into
        DSGN.modelingfilesdir = char(strcat('task-',task,'_firstlvl'));  % This folder gets appended to every session folder
        

        modelingfilesdirs = fullfile(firstlvl_derivdir, DSGN.modelingfilesdir);

        
        if any(~isfolder(modelingfilesdirs))
            if ~iscell(modelingfilesdirs)
                mkdir(modelingfilesdirs);
            else
                for i = 1:numel(modelingfilesdirs)
                    mkdir(modelingfilesdirs{i});
                end
            end
        end
    elseif numel(sub) == 1 && numel(ses) == 1
        % If there are multiple sessions within subject, set the modeldir to be at the ses-*/func level
        DSGN.modeldir = fullfile(firstlvl_derivdir, ['sub-',sub{1}], ['ses-', ses{1}], 'func', 'firstlvl', task);
        % Create folder to dump regressor structs into
        DSGN.modelingfilesdir = char(strcat('sub-',sub{1},'_ses-', ses{1},'_task-',task,'_firstlvl'));  % This folder gets appended to every session folder
        
        
        if ~isempty(run)
            modelingfilesdirs = fullfile(firstlvl_derivdir,strcat('sub-', sub),strcat('ses-', ses), 'func', strcat('run-', run), DSGN.modelingfilesdir);
        else
            modelingfilesdirs = fullfile(firstlvl_derivdir, strcat('sub-', sub),strcat('ses-', ses), 'func', DSGN.modelingfilesdir);
        end
        
        if any(~isfolder(modelingfilesdirs))
            if ~iscell(modelingfilesdirs)
                mkdir(modelingfilesdirs);
            else
                for i = 1:numel(modelingfilesdirs)
                    mkdir(modelingfilesdirs{i});
                end
            end
        end
    end
    % Create folder to dump betas into
    if ~isfolder(DSGN.modeldir)
        mkdir(DSGN.modeldir)
    end

    DSGN.subjects = fullfile(firstlvl_derivdir, strcat('sub-', unique(sub)));
end

function DSGN = setupDesignParameters(DSGN)
    % USER PLEASE ADJUST THESE:

    % Some reasonable defaults:
    DSGN.allowmissingfunc = true;       % default: false; true will prevent erroring out when functional file is missing for at least one run is missing for at least one subject
    DSGN.allowmissingcondfiles = true;  % default:false; if true, throw warning instead of error when no file(s) are found corresponding to a MAT-file name/wildcard
    DSGN.allowemptycond = true;         % default:false; if true, allow empty conditions, meaning not all condition combinations are present in every run.
    DSGN.notimemod = true;              % default: false; if true, turn off time modulation of conditions, i.e. when you do not expect linear trends over time
    DSGN.multireg = 'noise_model.mat';  % specify name for matfile with noise parameters you want to save

    % Study-Specific Parameters:
    DSGN.tr = 0.46;       % repetition time (TR) in seconds
    DSGN.hpf = 180;       % roughly 1/2 scan time; high pass filter in seconds; SPM default is 128, CANlab default is 180 since the brain response to pain stimuli last long and variance may be lost at shorter lengths, use scn_spm_design_check output, and review the SPM.mat in spm for diagnostics; 
    DSGN.fmri_t0 = 8;     % microtime onset - reference slice used in slice timing correction; spm (and CANlab) default 1 can be kept for multiband w/o slice timing. spm default is 8.
    DSGN.fmri_t = 16;     % microtime resolution - number of slices since we did slice timing; default 16 can be kept for multiband w/o slice timing; LabGAS does 30. CHECK IF YOU HAVE MULTIBAND WITH SLICE TIMING
    
    DSGN.fast = true;
    % if true, uses the FAST autoregressive model to model serial correlations (req spm12 r7771). This method was developed for sub-second TRs. For details see Bollmann, et al. (2018) Neuroimage. 
    % Note: if DSGN.fast = true, DSGN.ar1 must be false. These are mutually exclusive options. Note: the resultant SPM.mat files may be quite large. You may need to set spm_defaults.m to set defaults.mat.format to '-v7.3' to save them. 
    DSGN.ar1 = false;       % autoregressive AR(1) to model serial correlations; SPM default is true, CANlab default is false, Tor recommends turning autocorrelation off, because this algorithm pools across the whole brain, and does not perform well in some situations; if you are performing a group analysis, the autocorrelation problem is not as concerning

    % Optional Fields:
    %     DSGN.concatenation = {[1:6]}; % default: none; cell array of arrays of runs to concatenate; see documentation for when to concatenate, and how it works exactly
    %     DSGN.customrunintercepts = {1:6}; % default: none; will only work if DSGN.concatenation is specified; cell array of vectors specifying custom intercepts, NOT YET FULLY TESTED 

    %     DSGN.singletrials = {{}}; % a cell array (1 cell per session) of cell arrays (1 cell per condition) of (corresponding to DSGN.conditions) of true/false values indicating whether to convert specified condition to set of single trial conditions
    %     DSGN.singletrialsall = false; % default: false; if true, set DSGN.singletrials to true for all conditions
    %     
    %     DSGN.convolution.type; default hrf, which means canonical hrf - other options: fir, spline (spline not yet implemented)
    %     DSGN.convolution.time; default 0, which means no time derivative
    %     DSGN.convolution.dispersion: default 0, which means no dispersion derivative
end

function DSGN = processFunctionalRuns(funcs, task, DSGN)
    DSGN.funcnames={};
    DSGN.conditions={};
    DSGN.onsets={};
    DSGN.durations={};

    for i = 1:length(funcs)
        % Import events.tsv data, confounds_timeseries.tsv data

        [sub, ses, run, ~] = getBIDSSubSesRunTask(funcs(i).name);

        % 1. Find the *_events.tsv file
        events_fname = fullfile(funcs(i).folder, '*_events.tsv');

        funcname=fullfile(['ses-' ses], 'func', ['run-', run], funcs(i).name);
        fullpath=fullfile(findParentSubDir(DSGN.modeldir), funcname);
        if contains(funcname, '.gz') && ~isfile(erase(fullpath, '.gz'))
            disp(['Unzipping ', funcname]);
            % This will only work for a single-subject DSGN.
            gunzip(fullpath);
            funcname=erase(funcname, '.gz');
        end

        DSGN.funcnames{end+1}=funcname;  % Make sure you are only adding relative paths starting with session number the files you are adding are .nii and not .nii.gz
        % cell array (one cell per session) of paths to functional files, relative to absolute path specified in DSGN.subjects
        
        model_path = fullfile(funcs(i).folder, [DSGN.modelingfilesdir filesep]);
        
        % 2. Find noise related files for the func
        noise_fname = fullfile(funcs(i).folder, '*confounds_timeseries.tsv');
        noise_tsv = dir(noise_fname);   % confounds_timseries.tsv regular expression search string.
        % noise_dat = importBIDSfile(fullfile(noise_tsv.folder, noise_tsv.name));
        noise_dat = readtable(fullfile(noise_tsv.folder, noise_tsv.name),'FileType', 'text', 'Delimiter', 'tab');
        

        % 4. Generate regressors. Call a generate_WASABI_regressors function to do most of the heavy lifting.
        % Specify alternative onset-duration columns as a tuple e.g., {'name', 'ttl_2', 'ttl_3-ttl_2'}
        if ismember(task, {'bodymap', 'acceptmap'})
            ons_dur={{'ttl_2','ttl_3-ttl_2'}, {'ttl_1', 'ttl_4-ttl_1'}};
        end

        if strcmpi(task, 'distractmap')
            events_dat.nback_prestim=events_dat(endsWith(events_dat.conditions, 'back_stim'),:).onset;
            events_dat(endsWith(events_dat.conditions, 'timRating'),:).conditions='intensity_rating_start'; % Make sure all the rating events are called the same thing.
            ons_dur={{'ttl_2','ttl_3-ttl_2'}, {'ttl_1', 'ttl_4-ttl_1'}, {'nback_prestim', 'ttl_1-nback_onset'}};
        end
        % This set of onsets and durations:
        % ttl_2: The start of the peak heat stimulation
        % ttl_1: The start of the heat stimulation onset
        % *back_stim: For the NoF distractmap specifically, generate a
        % regressor where onset time is the start of the nback trial but
        % before the heat stimulation onset.
        % Will probably have to find a way to generate this for nback*
        % runs.

        % If you desire Parametric Modulators

        % DSGN.pmods={};
        % [DSGN.conditions{end+1}, DSGN.onsets{end+1}, DSGN.durations{end+1}, DSGN.pmods{end+1}]=generate_regressors(func_fullpath, events_fname, noise_fname, model_path)
        % [DSGN.pmods{end+1}, ]=configPmods(funcs, events_dat, DSGN.conditions{end})

        % If you don't have pmods:
        func_fullpath=fullfile(funcs(i).folder, funcs(i).name);
        [DSGN.conditions{end+1}, DSGN.onsets{end+1}, DSGN.durations{end+1}, ~]=generate_regressors(func_fullpath, events_fname, noise_fname, model_path, 'ons_dur', ons_dur);

        % 5. Generate contrasts. Call generate_WASABI_contrasts function to do most of the heavy lifting.
        DSGN = generate_contrasts(task, DSGN);
    end
end

function [pmods] = configPmods(funcs, events_dat, conditions, options)
    %% PARAMETRIC MODULATORS IF SPECIFIED
    
    % prep work for parametric modulators
    %  O is the events.tsv
    % pmod column needs to have a value for every trial row it is
    % modulating.

    % defaults
    if isempty(options.pmods)
        options.pmods.pmod_name = 'rating';
        options.pmods.pmod_polynom = 1;
        options.pmods.pmod_ortho_off = false;
        options.pmods.pmod_type = 'parametric_standard';
    end

    pmods={options.pmods.pmod_name};

    events_dat.trial_type = categorical(events_dat.trial_type);

    % Rename any column in events.tsv that matches the pmod.pmod_name to 'pmod'
    events_dat.Properties.VariableNames(categorical(events_dat.Properties.VariableNames) == options.pmods.pmod_name) = {'pmod'};
    

    % 'De-mean' pmod per run
    mean_pmod_run = mean(events_dat.pmod,'omitnan'); % this demeans pmods per run rather than condition (as spm does), which may be useful in some cases, see https://www.researchgate.net/post/How_to_define_parametric_modulators_for_multiple_conditions_in_SPM
    
    for trial = 1:height(events_dat)
        if ~isnan(events_dat.pmod(trial))
            events_dat.pmod_demean_run(trial) = events_dat.pmod(trial) - mean_pmod_run;
        else
            events_dat.pmod_demean_run(trial) = events_dat.pmod(trial);
        end
    end
    
    clear trial
    
    for cond = 1:size(conditions)
        mean_pmod_cond{cond} = mean(events_dat.pmod(events_dat.trial_type == conditions{cond})); % this demeans pmods per condition, as spm does
            for trial = 1:height(events_dat)
                if ~isnan(events_dat.pmod(trial))
                    if events_dat.trial_type(trial) == conditions{cond}
                        events_dat.pmod_demean_cond(trial) = events_dat.pmod(trial) - mean_pmod_cond{cond};
                    else
                        continue
                    end
                else
                    events_dat.pmod_demean_cond(trial) = events_dat.pmod(trial);
                end
            end
            clear trial
    end
    
    clear cond
    
    % add pmods to structures for conditions of interest
    cond_struct={};
    for pmod = 1:size(pmods)
        cond_struct{pmod}.pmod = struct('name',{pmods(pmod)}, ...
            'param',{{[]}}, ...
            'poly',{{options.pmods.pmod_polynom}});
        pmod_demean_run_struct{pmod}.pmod = struct('name',{strcat(pmods(pmod),'_demeaned_run')}, ...
            'param',{{[]}}, ...
            'poly',{{options.pmods.pmod_polynom}}); % structure for demeaned pmods per run
        pmod_demean_cond_struct{pmod}.pmod = struct('name',{strcat(pmods(pmod),'_demeaned_cond')}, ...
            'param',{{[]}}, ...
            'poly',{{options.pmods.pmod_polynom}}); % structure for demeaned pmods per condition
        if options.pmods.pmod_ortho_off
            cond_struct{pmod}.orth = {[0]};
        end

%         % Generate structure for conditions of interest
%         .pmod = struct('name', 'param', 'poly')
%         % Generate structure for demeaned pmods per run
%         pmod_demean_run_struct{pmod}.pmod = struct('name',{strcat(pmods(pmod),'_demeaned_run')}, ...
%             'param',{{[]}}, ...
%             'poly',{{options.pmods.pmod_polynom}}); 
%         % Generate structure for demeaned pmods per condition
%         pmod_demean_cond_struct{pmod}.pmod = struct('name',{strcat(pmods(pmod),'_demeaned_cond')}, ...
%             'param',{{[]}}, ...
%             'poly',{{options.pmods.pmod_polynom}});
    end

    clear pmod

    for trial = 1:size(events_dat.trial_type,1)
        pmod = 1;
        while pmod < numel(pmods) + 1
            % If the condition contains the trial_type...
            if contains(conditions{cond},char(events_dat.trial_type(trial))) % changed from original script to allow different condition names in different runs, to be tested
               
               cond_struct{pmod}.pmod.param{1} = [cond_struct{pmod}.pmod.param{1},events_dat.pmod(trial)];
               pmod_demean_run_struct{pmod}.pmod.param{1} = [pmod_demean_run_struct{pmod}.pmod.param{1},events_dat.pmod_demean_run(trial)];
               pmod_demean_cond_struct{pmod}.pmod.param{1} = [pmod_demean_cond_struct{pmod}.pmod.param{1},events_dat.pmod_demean_cond(trial)];
                % append the pmod value to each struct.

               if options.pmods.pmod_ortho_off
                   cond_struct{pmod}.orth = {[0]};
               end
            end
        pmod = pmod + 1;
        end
        continue
    end

    clear pmod trial


end



function plotDSGN(DSGN)
    % Plots a 2x1 figure for every functional run. Figure 1 depicts the
    % convolved Time(s) x Condition Predicted Activity. Figure 2 depicts the Condition x TR Design Matrix.

    for r = 1:numel(DSGN.conditions)
        [sub, ses, run, task]=getBIDSSubSesRunTask(DSGN.funcnames{r});

        %plot
        cat_conds = reordercats(categorical(DSGN.conditions{r}));
        cat_conds = categories(cat_conds);
    
        % If single subject. Otherwise will have to iterate through
        % DSGN.subjects
        nii_hdr = read_hdr(fullfile(findParentSubDir(DSGN.modeldir), DSGN.funcnames{r})); % reads Nifti header of smoothed image into a structure
        % This command doesn't work with .nii.gz files. FIXED NOW.
    
        if isfield(DSGN,'convolution')
            switch DSGN.convolution.type
                case 'hrf'
                    if DSGN.convolution.time == 0
                        hrf_name = spm_hrf(1);
                    elseif DSGN.convolution.time == 1
                        if DSGN.convolution.dispersion == 0
                            hrf_name = 'hrf (with time derivative)';
                        elseif DSGN.convolution.dispersion == 1
                            hrf_name = 'hrf (with time and dispersion derivatives)';
                        else
                            error('\nUnrecognized convolution type: %s',DSGN.convolution.dispersion)
                        end
                    else
                       error('\nUnrecognized convolution type: %s',DSGN.convolution.type)
                    end
                case 'fir'
                    hrf_name = 'Finite Impulse Response';
                otherwise
                    error('\nUnrecognized convolution type: %s',DSGN.convolution.type)
            end
        else
            hrf_name = spm_hrf(1);
        end                                
    
        ons_durs = cell(1,size(cat_conds,1));
    
        for cond = 1:size(cat_conds)
            try
                % Have to somehow access a list of onsets and durations for
%                 % each condition
%                 ons_durs{cond}(:,1) = conditions_struct.(cat_conds{cond}).onset{1};
%                 ons_durs{cond}(:,2) = conditions_struct.(cat_conds{cond}).duration{1};
                
                ons_durs{cond}(:,1) = DSGN.onsets{r}{cond};
                ons_durs{cond}(:,2) = DSGN.durations{r}{cond};
            catch
                warning(sprintf('Cannot create onset columns for %s', cat_conds{cond}));
            end
    
        end
    
        clear cond
    
        [Xfull,~,~,hrf_full] = onsets2fmridesign({ons_durs{2:end}},DSGN.tr,nii_hdr.tdim.*DSGN.tr, hrf_name);  
    
        % Get the screen size
        screenSize = get(0, 'ScreenSize'); % Returns [left, bottom, width, height]
        
        % Create a figure that fills the screen
        f1 = figure('Position', screenSize);
    
        subplot(2,1,1);
        plotDesign({ons_durs{2:end}},[],DSGN.tr,'samefig','basisset',hrf_name);
        ax1 = gca;
        ax1.TickLabelInterpreter = 'none';
        ax1.YTick = [1:size(cat_conds(2:end),1)];
        ax1.YTickLabel = (cat_conds(2:end));
        ax1.YLabel.String = 'condition';
        ax1.YLabel.FontSize = 12;
        ax1.YLabel.FontWeight = 'bold';
        ax1.XLabel.FontSize = 12;
        ax1.XLabel.FontWeight = 'bold';
        ax1.FontSize = 11;
        ax1.Title.FontSize = 14;
        ax1.Title.FontWeight = 'bold';
        ax1.TitleHorizontalAlignment = 'left';
    
        subplot(2,1,2);
        imagesc(zscore(Xfull(:,1:end-1)));
        colorbar
        ax2 = gca;
        ax2.TickLabelInterpreter = 'none';
        ax2.XTick = [1:size(cat_conds(2:end),1)];
        ax2.XTickLabel = (cat_conds(2:end));
        ax2.XTickLabelRotation = 45;
        ax2.XLabel.String = 'condition';
        ax2.XLabel.FontSize = 12;
        ax2.XLabel.FontWeight = 'bold';
        ax2.YLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
        ax2.YLabel.FontSize = 12;
        ax2.YLabel.FontWeight = 'bold';
        ax2.FontSize = 11;
        ax2.Title.FontSize = 14;
        ax2.Title.String = 'Design matrix';
        ax2.Title.FontWeight = 'bold';
        ax2.TitleHorizontalAlignment = 'left';
    
        sgtitle(['sub-', sub,' run-',run],'Color','red','FontSize',18, 'FontWeight','bold');
    
        % Save the figure out
        print(f1,fullfile(DSGN.modeldir,['design_sub-',sub,'_ses-',ses,'_run-',run,'_task-',task,'.png']),'-dpng','-r300');
    
        clear f1 ax1 ax2

        % get design matrix and plot
        
%         if display.plotdesign
%             
%             ons_durs_int = cell(1,size(DSGN.pmods{run},2));
%             pmods_raw = cell(1,size(DSGN.pmods{run},2));
%             pmods_demean_run = cell(1,size(DSGN.pmods{run},2));
%             pmods_demean_cond = cell(1,size(DSGN.pmods{run},2));
%                 for cond = 1:size(DSGN.pmods{run},2)
%                         ons_durs_int{cond}(:,1) = cond_struct{cond}.onset{1};
%                         ons_durs_int{cond}(:,2) = cond_struct{cond}.duration{1};
%                         pmods_raw{cond}(:,1) = cond_struct{cond}.pmod.param{1};
%                         pmods_demean_run{cond}(:,1) = pmod_demean_run_struct{cond}.pmod.param{1};
%                         pmods_demean_cond{cond}(:,1) = pmod_demean_cond_struct{cond}.pmod.param{1};
%                 end
% 
%                 clear cond
% 
%                 switch options.pmods.pmod_type
%                     case 'parametric_singleregressor'
%                         [X_pmod_raw,~,~,hrf_pmod_raw] = onsets2fmridesign(ons_durs_int,DSGN.tr,nii_hdr.tdim .*DSGN.tr, hrf_name,'parametric_singleregressor',pmods_raw);
% 
%                         f2 = figure('WindowState','maximized');
% 
%                         colors = get(gcf, 'DefaultAxesColorOrder');
%                         colors = mat2cell(colors, ones(size(colors, 1), 1), 3);
% 
%                         subplot(2,1,1);
%                         plot_matrix_cols(zscore(X_pmod_raw(:,1:end-1)),'horizontal',[],colors,3,[0 nii_hdr.tdim]);
%                         ax1 = gca;
%                         ax1.TickLabelInterpreter = 'none';
%                         ax1.YTick = [1:size(DSGN.pmods{run},2)];
%                         ax1.YTickLabel = DSGN.pmods{run};
%                         ax1.YLabel.String = 'condition';
%                         ax1.YLabel.FontSize = 12;
%                         ax1.YLabel.FontWeight = 'bold';
%                         ax1.XLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
%                         ax1.XLabel.FontSize = 12;
%                         ax1.XLabel.FontWeight = 'bold';
%                         ax1.XLim = [0 (nii_hdr.tdim + 2)];
%                         ax1.FontSize = 11;
%                         ax1.Title.String = 'Predicted activity';
%                         ax1.Title.FontSize = 14;
%                         ax1.Title.FontWeight = 'bold';
%                         ax1.TitleHorizontalAlignment = 'left';
% 
%                         subplot(2,1,2);
%                         imagesc(zscore(X_pmod_raw(:,1:end-1)));
%                         colorbar
%                         ax2 = gca;
%                         ax2.TickLabelInterpreter = 'none';
%                         ax2.XTick = [1:size(DSGN.pmods{run},2)];
%                         ax2.XTickLabel = (DSGN.pmods{run});
%                         ax2.XTickLabelRotation = 45;
%                         ax2.XLabel.String = 'condition';
%                         ax2.XLabel.FontSize = 12;
%                         ax2.XLabel.FontWeight = 'bold';
%                         ax2.YLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
%                         ax2.YLabel.FontSize = 12;
%                         ax2.YLabel.FontWeight = 'bold';
%                         ax2.FontSize = 11;
%                         ax2.Title.FontSize = 14;
%                         ax2.Title.String = 'Design matrix';
%                         ax2.Title.FontWeight = 'bold';
%                         ax2.TitleHorizontalAlignment = 'left';
% 
%                         sgtitle([derivsubjs{sub},' ',subjrundirnames{run}],'Color','red','FontSize',18, 'FontWeight','bold');
% 
%                         print(f2,fullfile(runmodeldir,['design_',pmods.pmod_type,'_',derivsubjs{sub},'_',subjrundirnames{run},'.png']),'-dpng','-r300');
% 
%                         clear f2 ax1 ax2
% 
%                     case 'parametric_standard'
%                         [X_unmod,delta_unmod,delta_hires_unmod,hrf_unmod] = onsets2fmridesign(ons_durs_int,DSGN.tr,nii_hdr.tdim .*DSGN.tr, hrf_name);  
%                         [X_pmod_run,delta,delta_hires,hrf_pmod] = onsets2fmridesign(ons_durs_int,DSGN.tr,nii_hdr.tdim .*DSGN.tr, hrf_name,'parametric_singleregressor',pmods_demean_cond); % unclear what to add as first column in matrix following 'parametric_standard' option
% 
%                         f2 = figure('WindowState','maximized');
% 
%                         colors = get(gcf, 'DefaultAxesColorOrder');
%                         colors = mat2cell(colors, ones(size(colors, 1), 1), 3);
% 
%                         subplot(2,2,[1 2]);
%                         l1 = plot_matrix_cols(zscore(X_unmod(:,1:end-1)),'horizontal',[],colors,3,[0 nii_hdr.tdim]);
%                         ax1 = gca;
%                         ax1.TickLabelInterpreter = 'none';
%                         ax1.YTick = [1:size(DSGN.pmods{run},2)];
%                         ax1.YTickLabel = conditions(1:size(DSGN.pmods{run},2));
%                         ax1.YLabel.String = 'condition';
%                         ax1.YLabel.FontSize = 12;
%                         ax1.YLabel.FontWeight = 'bold';
%                         ax1.XLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
%                         ax1.XLabel.FontSize = 12;
%                         ax1.XLabel.FontWeight = 'bold';
%                         ax1.XLim = [0 (nii_hdr.tdim + 2)];
%                         ax1.FontSize = 11;
%                         ax1.Title.String = 'Predicted activity';
%                         ax1.Title.FontSize = 14;
%                         ax1.Title.FontWeight = 'bold';
%                         ax1.TitleHorizontalAlignment = 'left';
% 
%                         hold on
% 
%                         l2 = plot_matrix_cols(zscore(X_pmod_run(:,1:end-1)),'horizontal',[],colors,1.5,[0 nii_hdr.tdim]);
%                          for line = 1:size(l2,2)
%                              l2(line).LineStyle = '--';
%                          end
% 
%                         hold off
% 
%                         subplot(2,2,3);
%                         imagesc(zscore(X_unmod(:,1:end-1)));
%                         colorbar
%                         ax2 = gca;
%                         ax2.TickLabelInterpreter = 'none';
%                         ax2.XTick = [1:size(DSGN.pmods{run},2)];
%                         ax2.XTickLabel = conditions(1:size(DSGN.pmods{run},2));
%                         ax2.XTickLabelRotation = 45;
%                         ax2.XLabel.String = 'condition';
%                         ax2.XLabel.FontSize = 12;
%                         ax2.XLabel.FontWeight = 'bold';
%                         ax2.YLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
%                         ax2.YLabel.FontSize = 12;
%                         ax2.YLabel.FontWeight = 'bold';
%                         ax2.FontSize = 11;
%                         ax2.Title.FontSize = 14;
%                         ax2.Title.String = 'Design matrix unmodulated';
%                         ax2.Title.FontWeight = 'bold';
%                         ax2.TitleHorizontalAlignment = 'left';
% 
%                         subplot(2,2,4);
%                         imagesc(zscore(X_pmod_run(:,1:end-1)));
%                         colorbar
%                         ax3 = gca;
%                         ax3.TickLabelInterpreter = 'none';
%                         ax3.XTick = [1:size(DSGN.pmods{run},2)];
%                         ax3.XTickLabel = DSGN.pmods{run};
%                         ax3.XTickLabelRotation = 45;
%                         ax3.XLabel.String = 'condition';
%                         ax3.XLabel.FontSize = 12;
%                         ax3.XLabel.FontWeight = 'bold';
%                         ax3.YLabel.String = ['#volume (TR = ',num2str(DSGN.tr),' sec)']; 
%                         ax3.YLabel.FontSize = 12;
%                         ax3.YLabel.FontWeight = 'bold';
%                         ax3.FontSize = 11;
%                         ax3.Title.FontSize = 14;
%                         ax3.Title.String = 'Design matrix modulated';
%                         ax3.Title.FontWeight = 'bold';
%                         ax3.TitleHorizontalAlignment = 'left';
% 
%                         sgtitle([derivsubjs{sub},' ',subjrundirnames{run}],'Color','red','FontSize',18, 'FontWeight','bold');
% 
%                         print(f2,fullfile(runmodeldir,['design_',pmods.pmod_type,'_',derivsubjs{sub},'_',subjrundirnames{run},'.png']),'-dpng','-r300');
% 
%                         clear f2 ax1 ax2 ax3 l1 l2
% 
%                     otherwise
%                         error('\nInvalid pmods.pmod_type option %s specified in <study_name>_firstlevel_<mx>_s1_options_dsgn_struct, please check before proceeding',pmods.pmod_type)
%                 
%                 end % switch pmod_type
%                 
%         end % if loop plotdesign




    end
end

function pathToSub = findParentSubDir(startPath)
    % This function finds the first parent directory of startPath
    % that starts with 'sub-'
    % Usage
    % DSGN.modeldir = 'path/to/your/directory/sub-xxx/...';
    % pathToSub = findParentSubDir(DSGN.modeldir);
    % disp(pathToSub);



    currentPath = startPath;

    while true
        [parentPath, name, ~] = fileparts(currentPath);

        % Check if the name matches the pattern 'sub-*'
        if startsWith(name, 'sub-')
            pathToSub = currentPath;
            return;
        end

        % If reached the top of the directory tree without finding a match
        if isempty(parentPath) || isequal(currentPath, parentPath)
            error('No parent directory starting with ''sub-'' found.');
        end

        % Move up one level in the directory tree
        currentPath = parentPath;
    end
end



