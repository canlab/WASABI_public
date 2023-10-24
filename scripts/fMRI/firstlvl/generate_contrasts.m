function [contrasts, contrastweights, contrastnames] = generate_contrasts(task)
    % GENERATE_CONTRASTS Generate SPM-style contrasts for different tasks in your study
    % 
    % Usage:
    %   [contrasts, contrastweights, contrastnames] = generate_contrasts(task)
    %
    % Inputs:
    %   task - A string representing the task name. E.g., 'bodymap', 'movemap', etc.
    %
    % Outputs:
    %   contrasts - A cell array of contrasts. Each contrast is a cell array of condition names.
    %   contrastweights - A cell array of contrast weights. Each set of weights is a vector.
    %   contrastnames - A cell array of contrast names. Each name is a string.
    %
    % Example:
    %   [contrasts, contrastweights, contrastnames] = generate_contrasts('bodymap');
    %
    % Author: Michael Sun, Ph.D.
    % Date: 10/24/2023

    contrasts = {};
    contrastweights = {};
    contrastnames = {};
    
    %% USER TODO:
    % Define the contrast information for each of your tasks
    task_contrasts = struct();
    
    % Examples below:
    % task_contrasts.bodymap = {
    %     {{'hot'}, 'avgHot', []}
    %     {{'warm'}, 'avgWarm', []}
    %     {{'imagine'}, 'avgImagine', []}
    %     % ... (other contrasts for bodymap)
    % };
    % 
    % task_contrasts.movemap = {
    %     {{'leftface'}, 'avgLeftface', []}
    %     {{'rightface'}, 'avgRightface', []}
    %     % ... (other contrasts for movemap)
    % };
    
    % ... (define contrasts for other tasks)

    if isempty(fieldnames(task_contrasts))
        error('No tasks defined, please define your tasks first to generate contrasts.');
    end


    % Check if the task is defined in the contrast information
    if isfield(task_contrasts, task)
        task_data = task_contrasts.(task);
        num_contrasts = size(task_data, 1);
        
        for i = 1:num_contrasts
            contrast_info = task_data{i};
            contrasts{end+1} = contrast_info{1};
            contrastnames{end+1} = contrast_info{2};
            if isempty(contrast_info{3})
                contrastweights{end+1} = ones(1, length(contrast_info{1}));
            else
                contrastweights{end+1} = contrast_info{3};
            end
        end
    else
        warning('Task not recognized: %s', task);
    end
end
