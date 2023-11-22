function [condition_names, onsets, durations, pmods] = generate_regressors(task, events_dat, noise_dat, R, spike_def, mdl_path, varargin)
    % GENERATE_REGRESSORS Generate regressors for first-level modeling in SPM.
    %
    % This function generates regressors for specified tasks in BIDS datasets.
    %
    % Usage:
    %   [condition_names, pmods] = generate_regressors(task, sub, sess, events_dat, noise_dat, R, spike_def, mdl_path, varargin)
    %
    % Inputs:
    %   task        - The task name
    %   events_dat  - Stimulus data (event timings and types)
    %   noise_dat   - Noise data (nuisance regressors)
    %   R           - Existing regression matrix
    %   spike_def   - Definitions for spike regressors
    %   mdl_path    - Model path where outputs will be saved
    %
    % Optional Key-Value Pairs:
    %   'ons_dur', {{'onset', 'duration'}} - Cell array containing names of the onset and duration columns
    %
    % Outputs:
    %   condition_names - Names of the conditions used for modeling
    %   pmods           - Parametric modulators, if any
    %
    % Example:
    %   [condition_names, pmods] = generate_regressors('task1', 'sub-01', 'ses-01', stim_dat, noise_dat, R, spike_def, '/path/to/model');
    %
    % Author: Michael Sun, Ph.D.
    % Date: 10/24/2023

    p = inputParser;
    addRequired(p, 'task', @ischar);
    addRequired(p, 'events_dat', @istable);
    addRequired(p, 'noise_dat', @istable);
    addRequired(p, 'R', @isnumeric);
    addRequired(p, 'mdl_path', @ischar);
    % Add optional ons_dur parameter with default column names 'onset' and 'duration'
    addParameter(p, 'ons_dur', {{'onset', 'duration'}}, @(x) iscell(x) && all(cellfun(@(y) iscell(y) && length(y) == 2, x)));
    
    % Parse the inputs
    parse(p, task, events_dat, noise_dat, R, mdl_path, varargin{:});
 
    % Retrieve ons_dur argument
    ons_dur={{'onset', 'duration'}};
    for i = 2:numel(p.Results.ons_dur)+1
        ons_dur{i} = p.Results.ons_dur{i-1};
    end


    [sub, ses, run, ~]=getBIDSSubSesRunTask(mdl_path);

    for i = 1:numel(ons_dur)
        % Check if onset and duration columns exist
        if ~ismember(ons_dur{i}{1}, events_dat.Properties.VariableNames)
            warning(sprintf('The onset column specified: %s does not exist in the events data. Skipping this regressor.', ons_dur{i}{1}));
            ons_dur(i)=[];
        
        elseif ~ismember(ons_dur{i}{2}, events_dat.Properties.VariableNames)
            % Duration column does not exist, so we need to create it
            warning(sprintf('The duration column specified: %s does not exist in the events data. Attempting to compute it mathematically.', ons_dur{i}{2}));
            try
                % Attempt to calculate the duration using the expression provided
                events_dat.(ons_dur{i}{2}) = calculate_duration_from_expression(ons_dur{i}{2}, events_dat);
            catch ME
                % If there's an error, rethrow it with more context
                error('Error calculating duration: %s. Skipping this regressor.', ME.message);
                ons_dur(i)=[];
            end
        end
    end

    
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
        condition_name = matlab.lang.makeValidName(unique_conditions{i});
        conditions_struct.(condition_name) = struct('name', {{condition_name}}, 'onset', {{[]}}, 'duration', {{[]}});
    end

    %% 2. Fill-out the SPM style design-obj
    % varargin can represent onset-duration column pairings from the
    % events_dat to generate further optional regressors.
    % generate all possible onset and duration condition .mat files, but
    % only put in DSGN.conditions either the default or what is
    % user-specified.
    numberOfTrials = height(events_dat);
    display([sub, ses, run])
    disp(numberOfTrials)
    for trial = 1:numberOfTrials

        for i=1:numel(ons_dur)
            if ~isnan(events_dat.(ons_dur{i}{1})(trial)) && ~isnan(events_dat.(ons_dur{i}{2})(trial))
                % For custom onsets and durations, check to ensure that valid onsets and durations exist for that trial.
                if ~strcmpi(ons_dur{i}{1}, 'onset')
                    condition_name = [matlab.lang.makeValidName(events_dat.trial_type{trial}), '_', ons_dur{i}{1}]; % New, separate name.
                    if ~isfield(conditions_struct, condition_name)
                        conditions_struct.(condition_name) = struct('name', {{condition_name}}, 'onset', {{[]}}, 'duration', {{[]}});
                    end
                else
                    condition_name = matlab.lang.makeValidName(events_dat.trial_type{trial});
                end
                conditions_struct.(condition_name).onset{1} = [conditions_struct.(condition_name).onset{1}, events_dat.(ons_dur{i}{1})(trial)];
                conditions_struct.(condition_name).duration{1} = [conditions_struct.(condition_name).duration{1}, events_dat.(ons_dur{i}{2})(trial)];
            end
        end
    end

    % Perhaps purge any redundant conditions here

    % Purge any conditions that don't have any onsets
    condition_names = fieldnames(conditions_struct);
    for i = 1:length(condition_names)
        fieldName = condition_names{i}; % Get the name of the current field
        if isempty(conditions_struct.(fieldName).onset{1}) % Check if the 'onset' field is empty
            conditions_struct = rmfield(conditions_struct, fieldName); % Remove the field
        end
    end


    %% 3. Save condition structs
    condition_names = fieldnames(conditions_struct);
    onsets={};
    durations={};
    for i = 1:length(condition_names)
        condition_name = condition_names{i};
        tempStruct = conditions_struct.(condition_name);
        onsets{i}=conditions_struct.(condition_name).onset{1};
        durations{i}=conditions_struct.(condition_name).duration{1};
        save(fullfile(mdl_path, [condition_name, '.mat']), '-struct', 'tempStruct');
    end
    
    %% 5. create noise vector design
    % Assuming that noise_dat is a table and R is a matrix
    [R, R_added, R_hdr] = create_noise_vector(noise_dat, R, mdl_path, spike_def);

    %% 6. Export noise plots
    export_noise_plots(R_added, R_hdr, mdl_path, sub, ses, run, task);

    %% 7. PMods
    % Configure pmods
    pmods = {};
    % pmods={'intensity', 'valence', 'comfort'};
   
end
    

%% Helper Functions:
% These noise functions follow the typical first-level workflow of the
% CANLab, which regressed out CSF but not white-matter, and accounts for 24
% motion regressors (i.e., x,y,z,pitch,yaw,roll,and derivatives). Edit
% below if you have different needs:


function [R, R_added, R_hdr] = create_noise_vector(noise_dat, R, mdl_path, spike_def)
    R_nuisance = [];
    R_hdr = {};
    noise_hdr = noise_dat.Properties.VariableNames;

    % Collect all header indices with specified nuisance regressors
    
    % ==CANLAB Standard 1st-Level Nuisance Covariates==
    % 1a. Top k Anatomical Component-Based Noise Correction (aCompCorr) Covariates
    %   aCompCorr is a method to reduce noise in fMRI.
    %   acompcor_idx=find(contains(noise_dat.Properties.VariableNames,'a_comp_cor'));
    %   acompcor_idx=acompcor_idx(1:min(10, end)); % This grabs the top 10 components.

    % 1b. CSF and/or White Matter
    csf_idx=find(contains(noise_dat.Properties.VariableNames,'csf'));
    csf_idx=csf_idx(1);
    R_nuisance = [R_nuisance, csf_idx];
    R_hdr{end+1}='csf';

    % wm_idx=find(contains(noise_dat.Properties.VariableNames,'white_matter'));
    % wm_idx=wm_idx(1);
    % R_nuisance = [R_nuisance, wm_idx];
    % R_hdr{end+1}='wm';

    % 1c. (6, 12, or 24) Movement Parameters
    
    % 6 Movement Parameters
    % search_strings = {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z'};
    % m_idx = find(cellfun(@(x) any(strcmp(x, search_strings)), noise_hdr));
    % R_hdr=[R_hdr, {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z'}];

    % 12 Movement Parameters
    % search_strings = {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z', ...
    % 'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1', ...
    % 'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1'};
    % m_idx = find(cellfun(@(x) any(strcmp(x, search_strings)), noise_hdr));
    % R_hdr=[R_hdr, {'trans_x', 'trans_y', 'trans_z','rot_x','rot_y','rot_z', ...
    % 'trans_x_derivative1', 'trans_y_derivative1', 'trans_z_derivative1', ...
    % 'rot_x_derivative1','rot_y_derivative1','rot_z_derivative1'}];
    
    % 24 Movement Parameters
    xindex = find(strcmp(noise_hdr, 'trans_x') == 1);
    m_idx = [xindex:xindex + 23];
    R_nuisance = [R_nuisance, m_idx];
    R_hdr=[R_hdr, noise_hdr([xindex:xindex + 23])];
    
    % 1d. If we allow fmriprep to define our rmssd and dvars, here's what
    % we might do:
    if strcmpi(spike_def, 'fmriprep')
        dvars_idx=find(strcmpi(noise_dat.Properties.VariableNames,'dvars'));
        % fd_idx=find(strcmpi(noise_dat.Properties.VariableNames,'framewise_displacement'));
        rmsd_idx=find(strcmpi(noise_dat.Properties.VariableNames,'rmsd'));
        % mout_idx=find(contains(noise_dat.Properties.VariableNames,'motion_outlier'));
        % R_nuisance = [R_nuisance, dvars_idx, fd_idx, rmsd_idx, mout_idx];
        % R_hdr=[R_hdr, noise_hdr([dvars_idx, fd_idx, rmsd_idx, mout_idx])];
        R_nuisance = [R_nuisance, dvars_idx, rmsd_idx];
        R_hdr=[R_hdr, noise_hdr([dvars_idx, rmsd_idx])];

    end

    % 1e. Average-interpolation over any nan-values
    for n = R_nuisance
        this_col = noise_dat{:, n};
        noise_dat{isnan(this_col), n} = nanmean(this_col); 
    end

    % 2. If spike_def was 'CANlab', concatenate with the RMSSD/DVARS and spike regressors and return the R noise matrix
    R_added=noise_dat{:, R_nuisance};
    R = [R, R_added];
    R = unique(R', 'rows', 'stable')';  % remove any redundant rows. Keep the same order of regressors otherwise.

    % 3. Save the nuisance regressors.
    save(fullfile(mdl_path, 'noise_model.mat'), 'R');
end

function export_noise_plots(R_added, R_hdr, mdl_path, sub, ses, task, run)
    % This function assumes that R_nuisance is a matrix with regressor
    % values and R_hdr is a cell array of regressor names.

    % Define motion-related regressor names
    motion_keywords = {'trans', 'rot', 'dvars', 'framewise_displacement', 'rmsd', 'motion'};
    
    % Find indices of motion-related and nuisance regressors
    motion_reg_indices = contains(R_hdr, motion_keywords);
    nuisance_reg_indices = ~motion_reg_indices;

    % Plot nuisance regressors
    figure;
    plot(R_added(:, nuisance_reg_indices));
    legend(R_hdr(nuisance_reg_indices), 'Interpreter', 'none');
    title('Nuisance regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, ['sub-', sub, '_ses-', ses, '_task-', task, '_run-', run, '_nuisance_regressor_plot.png']));
    savefig(fullfile(mdl_path, ['sub-', sub, '_ses-', ses, '_task-', task, '_run-', run, '_nuisance_regressor_plot.fig']));

    % Plot motion regressors
    figure;
    plot(R_added(:, motion_reg_indices));
    legend(R_hdr(motion_reg_indices), 'Interpreter', 'none');
    title('Movement regressors');
    fig = gcf;
    exportgraphics(fig, fullfile(mdl_path, ['sub-', sub, '_ses-', ses, '_task-', task, '_run-', run, '_movement_regressor_plot.png']));
    savefig(fullfile(mdl_path, ['sub-', sub, '_ses-', ses, '_task-', task, '_run-', run, '_movement_regressor_plot.fig']));

    close all;
end



function result = calculate_duration_from_expression(expression, events_dat)
    % This function calculates a new duration column based on an expression
    % like 'col1^col2'. It supports +, -, *, /, and ^ operators.

    % Define a regular expression to match operands and operators
    % This pattern matches words (column names) and the operators +, -, *, /, and ^
    pattern = '(?<operand1>\w+)(?<operator>[+\-*/^])(?<operand2>\w+)';

    % Match the expression against the pattern
    tokens = regexp(expression, pattern, 'names');
    
    if isempty(tokens)
        error('The expression does not match the expected format (operand1 operator operand2).');
    end

    % Extract the operands and operator from the tokens
    operand1 = tokens.operand1;
    operator = tokens.operator;
    operand2 = tokens.operand2;

    % Check if the operands exist as columns
    if ~ismember(operand1, events_dat.Properties.VariableNames)
        error(['The column ' operand1 ' does not exist in the events data.']);
    end
    if ~ismember(operand2, events_dat.Properties.VariableNames)
        error(['The column ' operand2 ' does not exist in the events data.']);
    end

    % Perform the operation
    switch operator
        case '+'
            result = events_dat.(operand1) + events_dat.(operand2);
        case '-'
            result = events_dat.(operand1) - events_dat.(operand2);
        case '*'
            result = events_dat.(operand1) .* events_dat.(operand2);
        case '/'
            result = events_dat.(operand1) ./ events_dat.(operand2);
        case '^'
            result = events_dat.(operand1) .^ events_dat.(operand2);
        otherwise
            error(['The operator ' operator ' is not supported.']);
    end
end


