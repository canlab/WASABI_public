function groups = groupTasksByPrefix(tasks)
    % Ensure the input is a cell array of strings
    if ~iscell(tasks) || ~all(cellfun(@ischar, tasks))
        error('Input must be a cell array of strings');
    end
    
    % Sort the task names
    sortedTasks = sort(tasks);
    
    % Initialize variables
    groups = {};
    currentGroup = {};
    currentPrefix = '';
    
    % Loop through the sorted task names
    for i = 1:length(sortedTasks)
        % If this is the first task, just add it to the current group
        if isempty(currentGroup)
            currentGroup{end+1} = sortedTasks{i};
            currentPrefix = sortedTasks{i};
        else
            % Find the common prefix between the current task and the previous one
            commonPrefix = findCommonPrefix(currentPrefix, sortedTasks{i});
            
            % If there is a common prefix, add the current task to the group
            if ~isempty(commonPrefix)
                currentGroup{end+1} = sortedTasks{i};
                currentPrefix = commonPrefix;  % Update the current prefix
            else
                % If no common prefix, start a new group
                groups{end+1} = currentGroup;
                currentGroup = {sortedTasks{i}};
                currentPrefix = sortedTasks{i};
            end
        end
    end
    
    % Add the last group
    if ~isempty(currentGroup)
        groups{end+1} = currentGroup;
    end
end

function commonPrefix = findCommonPrefix(str1, str2)
    % Find the longest common prefix of two strings
    minLength = min(length(str1), length(str2));
    commonPrefix = '';
    for i = 1:minLength
        if str1(i) == str2(i)
            commonPrefix = [commonPrefix, str1(i)];
        else
            break;
        end
    end
end
