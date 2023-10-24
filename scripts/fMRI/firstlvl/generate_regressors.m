function conditions = generate_regressors(BIDSroot, task, sid, sess, stim_dat, noise_dat, R, mdl_path, varargin)
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
    addRequired(p, 'BIDSroot', @ischar);
    addRequired(p, 'task', @ischar);
    addRequired(p, 'sid', @ischar);
    addRequired(p, 'sess', @ischar);
    addRequired(p, 'stim_dat', @istable);
    addRequired(p, 'noise_dat', @istable);
    addRequired(p, 'R', @isnumeric);
    addRequired(p, 'mdl_path', @ischar);
    % Add optional parameters here
    parse(p, BIDSroot, task, sid, sess, stim_dat, noise_dat, R, mdl_path, varargin{:});
    

    % if ismac()
    %     BIDSroot = fullfile('/Volumes', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    % elseif ispc()
    %     BIDSroot = fullfile('\\dartfs-hpc', 'rc', 'lab', 'C', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    % else
    %     BIDSroot = fullfile('//dartfs-hpc', 'rc', 'lab', 'C', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    % end

    ses_str=sess;
    
    %% 1. Set Conditions/Regressors in accordance to your _task.tsv file.
    
    % Create IV Design structure
    
    % Read-in any files and parse any trial_type, or ttl* columns
    
    % Create one struct for every trial_type, with fields: 
    %   name: {{'trial_type1'}}
    %   onset: {{[1 2 3 4 ...]}}
    %   duration: {{[1 1 1 1 ...]}}

    % Example:
    unique_conditions = unique(stim_dat.condition); % assuming 'condition' is a column in your stim_dat table
    conditions_struct = struct;
    for i = 1:length(unique_conditions)
        condition_name = unique_conditions{i};
        conditions_struct.(condition_name) = struct('name', {{condition_name}}, 'onset', {{[]}}, 'duration', {{[]}});
    end


    %% 2. Fill-out the SPM style design-obj
    numberOfTrials = height(stim_dat);
    for trial = 1:numberOfTrials
        condition_name = stim_dat.condition{trial};
        conditions_struct.(condition_name).onset{1} = [conditions_struct.(condition_name).onset{1}, stim_dat.onset(trial)];
        conditions_struct.(condition_name).duration{1} = [conditions_struct.(condition_name).duration{1}, stim_dat.duration(trial)];
    end

    %% 3. Save condition structs
   condition_names = fieldnames(conditions_struct);
    for i = 1:length(condition_names)
        condition_name = condition_names{i};
        save(fullfile(mdl_path, [condition_name, '.mat']), '-struct', 'conditions_struct.(condition_name)');
    end

    %% 4. Return/Output your conditions
    conditions = condition_names;
    
    %% 5. create noise vector design
    % Assuming that noise_dat is a table and R is a matrix
    [R, R_headmotion, noise_idx] = create_noise_vector(noise_dat, R);

    %% 6. Export noise plots
    export_noise_plots(R, noise_idx, mdl_path, sid, ses_str, task);
    
    save(fullfile(mdl_path, 'noise_model.mat'), 'R');
end
    

%% Helper Functions:
% These noise functions follow the typical first-level workflow of the
% CANLab, which regressed out CSF but not white-matter, and accounts for 24
% motion regressors (i.e., x,y,z,pitch,yaw,roll,and derivatives). Edit
% below if you have different needs:


function [R, R_headmotion, noise_idx] = create_noise_vector(noise_dat, R)
    R_headmotion = [];
    noise_hdr = noise_dat.Properties.VariableNames;
    
    % CSF and/or White Matter
    for m = 1:size(noise_dat, 2)
        this_col = noise_dat{:, m};
        noise_dat{isnan(this_col), m} = nanmean(this_col); % Replace all nans with mean
        if strcmp('csf', noise_hdr{m})==1    % Without White Matter. Compare the VIFs of these models.
            R_headmotion = [m, R_headmotion];
        end
    end
    noise_idx = size(R_headmotion, 2);
    
    xindex = find(strcmp(noise_hdr, 'trans_x') == 1);
    Mindex = [xindex:xindex + 23];
    R_headmotion = [R_headmotion, Mindex];
    
    R = [R, noise_dat{:, R_headmotion}];
    R = unique(R', 'rows', 'stable')';  % remove any redundant rows. Keep the same order of regressors otherwise.
end

function export_noise_plots(R, noise_idx, mdl_path, sid, ses_str, task)
    figure;
    plot(R(:, 1:noise_idx)); legend({'csf'}) % Without white matter
    title('Nuisance regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, [sid, '_', ses_str, '_', task, '_', 'nuisance_regressor_plot.png']));
    savefig(fullfile(mdl_path, [sid, '_', ses_str, '_', task, '_', 'nuisance_regressor_plot.fig']));
    
    figure; plot(R(:, noise_idx:end)); % Without white matter
    legend({'trans x', 'trans x derivative1', 'trans x derivative1_power2', 'trans x power2', 'trans y', 'trans y derivative1', 'trans y derivative1 power2', 'trans y power2', 'trans z', 'trans z derivative1', 'trans z power2', 'trans z derivative1 power2', 'rot x', 'rot x derivative1', 'rot x derivative1 power2', 'rot x power2', 'rot y', 'rot y derivative1', 'rot y derivative1 power2', 'rot y power2', 'rot z', 'rot z derivative1', 'rot z derivative1 power2', 'rot z power2'});
    title('Movement regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, [sid, '_', ses_str, '_', task, '_', 'movement_regressor_plot.png']));
    savefig(fullfile(mdl_path, [sid, '_', ses_str, '_', task, '_', 'movement_regressor_plot.fig']));
end