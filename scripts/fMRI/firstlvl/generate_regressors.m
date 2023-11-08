function condition_names = generate_regressors(task, sub, sess, events_dat, noise_dat, R, mdl_path, varargin)
    % GENERATE_REGRESSORS Generate regressors to prepare it for first-level modelling in SPM.
    %
    % This function generates regressors for different tasks in BIDS datasets.
    %
    % Usage:
    %   conditions = generate_regressors(BIDSroot, task, sid, sess, stim_dat, noise_dat, R, mdl_path, varargin)
    %
    % Inputs:
    %   BIDSroot    - The root directory of the BIDS dataset
    %   task        - The task name
    %   sid         - Subject ID
    %   sess        - Session ID
    %   stim_dat    - Stimulus data
    %   noise_dat   - Noise data
    %   R           - Regression matrix
    %   mdl_path    - Model path
    %
    % Optional Key-Value Pairs:
    %   'param1', value1, 'param2', value2, ...
    %
    % Outputs:
    %   conditions  - Conditions for the task
    %
    % Example:
    %   conditions = generate_regressors('/path/to/BIDS', 'task1', 'sub-01', 'ses-01', stim_dat, noise_dat, R, '/path/to/model');
    %
    % Author: Michael Sun, Ph.D.
    % Date: 10/24/2023

    p = inputParser;
%     addRequired(p, 'BIDSroot', @ischar);
    addRequired(p, 'task', @ischar);
    addRequired(p, 'sub', @ischar);
    addRequired(p, 'sess', @ischar);
    addRequired(p, 'events_dat', @istable);
    addRequired(p, 'noise_dat', @istable);
    addRequired(p, 'R', @isnumeric);
    addRequired(p, 'mdl_path', @ischar);
    % Add optional parameters here
    parse(p, task, sub, sess, events_dat, noise_dat, R, mdl_path, varargin{:});
    
    %% 1. Set Conditions/Regressors in accordance to your _task.tsv file.
    
    % Create IV Design structure
    
    % Read-in any files and parse any trial_type, or ttl* columns
    
    % Create one struct for every trial_type, with fields: 
    %   name: {{'trial_type1'}}
    %   onset: {{[1 2 3 4 ...]}}
    %   duration: {{[1 1 1 1 ...]}}

    % Example:
    unique_conditions = unique(events_dat.trial_type); % assuming 'trial_type' is a column in your stim_dat table
    conditions_struct = struct;
    for i = 1:length(unique_conditions)
        condition_name = unique_conditions{i};
        conditions_struct.(condition_name) = struct('name', {{condition_name}}, 'onset', {{[]}}, 'duration', {{[]}});
    end

    %% 2. Fill-out the SPM style design-obj
    % varargin can represent onset-duration column pairings from the
    % events_dat to generate further optional regressors.


    numberOfTrials = height(events_dat);
    for trial = 1:numberOfTrials
        condition_name = events_dat.trial_type{trial};
        onset_col={'onset', 'ttl_1', ...'etc'}
        for o = 1:numel(onset_col)
            % conditions_struct.(condition_name).onset{1} = [conditions_struct.(condition_name).onset{1}, events_dat.onset(trial)];
            conditions_struct.(condition_name).(onset_col{o}){1} = [conditions_struct.(condition_name).(onset_col{o}){1}, events_dat.(onset_col{o})(trial)];
        end

        % Probably should save them as additional condition_names instead.

        duration_col={'duration', 'ttl_1', ...'etc'}
        for d = 1:numel(duration_col)
            conditions_struct.(condition_name).(duration_col{d}){1} = [conditions_struct.(condition_name).(duration_col{d}){1}, events_dat.(duration_col{o})(trial)];
        end
    end

    % 2a. Additional onset-columns for regressors, e.g., ttl
    



    %% 3. Save condition structs
    condition_names = fieldnames(conditions_struct);
    for i = 1:length(condition_names)
        condition_name = condition_names{i};
        save(fullfile(mdl_path, [condition_name, '.mat']), '-struct', 'conditions_struct.(condition_name)');
    end
    
    %% 5. create noise vector design
    % Assuming that noise_dat is a table and R is a matrix
    [R, ~, noise_idx] = create_noise_vector(noise_dat, R, mdl_path);

    %% 6. Export noise plots
    export_noise_plots(R, noise_idx, mdl_path, sub, sess, task);
    
   
end
    

%% Helper Functions:
% These noise functions follow the typical first-level workflow of the
% CANLab, which regressed out CSF but not white-matter, and accounts for 24
% motion regressors (i.e., x,y,z,pitch,yaw,roll,and derivatives). Edit
% below if you have different needs:


function [R, R_nuisance, noise_idx] = create_noise_vector(noise_dat, R, mdl_path)
    R_nuisance = [];
    noise_hdr = noise_dat.Properties.VariableNames;

    % ==CANLAB Standard 1st-Level Nuisance Covariates==
    % 1a. Top k Anatomical Component-Based Noise Correction (aCompCorr) Covariates
    %   aCompCorr is a method to reduce noise in fMRI.
    %   acompcor_idx=find(contains(noise.Properties.VariableNames,'a_comp_cor'));
    %   acompcor_idx=acompcor_idx(1:min(10, end)); % This grabs the top 10 components.

    % 1b. CSF and/or White Matter
    for n = 1:numel(noise_hdr)
        this_col = noise_dat{:, n};
        noise_dat{isnan(this_col), n} = nanmean(this_col);  % Replace all nans with mean
        if strcmp('csf', noise_hdr{n})==1                   % Without White Matter. Compare the VIFs of these models.
            R_nuisance = [n, R_nuisance];
        end
        % if strcmp('white_matter', noise_hdr{n})==1
        %     R_nuisance = [n, R_nuisance];
        % end
    end
    noise_idx = size(R_nuisance, 2);

    % 1c. (24) Movement Parameters
    xindex = find(strcmp(noise_hdr, 'trans_x') == 1);
    % 6 Movement Parameters
%     search_strings = {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z'};
%     indices = find(cellfun(@(x) any(strcmp(x, search_strings)), noise_hdr));
    % 12 Movement Parameters
%     search_strings = {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z', ...
%         'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1', ...
%         'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1'};
%     indices = find(cellfun(@(x) any(strcmp(x, search_strings)), noise_hdr));
    % 24 Movement Parameters
    find(strcmp(noise_hdr, 'trans_x') == 1);
    Mindex = [xindex:xindex + 23];
    R_nuisance = [R_nuisance, Mindex];
    
    % 2. Concatenate with the RMSSD/DVARS and spike regressors and return the R noise matrix
    R = [R, noise_dat{:, R_nuisance}];
    R = unique(R', 'rows', 'stable')';  % remove any redundant rows. Keep the same order of regressors otherwise.

    % 3. Save the nuisance regressors.
    save(fullfile(mdl_path, 'noise_model.mat'), 'R');
end

function export_noise_plots(R, noise_idx, mdl_path, sub, sess, task)
    figure;
    plot(R(:, 1:noise_idx)); legend({'csf'}) % Without white matter
    title('Nuisance regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, ['sub-', sub, '_', 'ses-', sess, '_', 'task-', task, '_', 'nuisance_regressor_plot.png']));
    savefig(fullfile(mdl_path, ['sub-', sub, '_', 'ses-', sess, '_', 'task-', task, '_', 'nuisance_regressor_plot.fig']));
    
    figure; plot(R(:, noise_idx:end)); % Without white matter
    legend({'trans x', 'trans x derivative1', 'trans x derivative1_power2', 'trans x power2', 'trans y', 'trans y derivative1', 'trans y derivative1 power2', 'trans y power2', 'trans z', 'trans z derivative1', 'trans z power2', 'trans z derivative1 power2', 'rot x', 'rot x derivative1', 'rot x derivative1 power2', 'rot x power2', 'rot y', 'rot y derivative1', 'rot y derivative1 power2', 'rot y power2', 'rot z', 'rot z derivative1', 'rot z derivative1 power2', 'rot z power2'});
    title('Movement regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, ['sub-', sub, '_', 'ses-', sess, '_', 'task-', task, '_', 'movement_regressor_plot.png']));
    savefig(fullfile(mdl_path, ['sub-', sub, '_', 'ses-', sess, '_', 'task-', task, '_', 'movement_regressor_plot.fig']));
end