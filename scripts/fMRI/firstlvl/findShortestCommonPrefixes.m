function commonPrefixes = findCommonPrefixes(tasks)
    % Ensure the input is a cell array of strings
    if ~iscell(tasks) || ~all(cellfun(@ischar, tasks))
        error('Input must be a cell array of strings');
    end
    
    % Initialize variables
    groups = containers.Map('KeyType', 'char', 'ValueType', 'any');
    
    % Loop through the task names
    for i = 1:length(tasks)
        % Extract the root of the task name (all initial alphabetic characters)
        root = regexp(tasks{i}, '^[a-zA-Z]*', 'match', 'once');
        
        if isempty(root)
            disp(['Skipping task with no alphabetic prefix: ', tasks{i}]);
            continue;
        end
        
        % Check if the root is already a key in the map
        if isKey(groups, root)
            % If the root is already a key, retrieve the group, add the task name, and put it back
            groups(root) = [groups(root), tasks(i)];
        else
            % If the root is not already a key in the map, add it with the full task name as the first item in a new group
            groups(root) = {tasks{i}};
        end
    end
    
    % Find the common prefix for each group and store unique prefixes
    commonPrefixes = {};
    groupValues = groups.values;
    for i = 1:length(groupValues)
        commonPrefix = findCommonPrefix(groupValues{i});
        if ~isempty(commonPrefix)
            commonPrefixes{end+1} = commonPrefix;
        end
    end
    
    % Ensure uniqueness
    commonPrefixes = unique(commonPrefixes);
end

function commonPrefix = findCommonPrefix(strings)
    if length(strings) == 1
        commonPrefix = strings{1};
        return;
    end
    
    % Sort strings to bring similar strings together
    sortedStrings = sort(strings);
    
    % Find common prefix of first and last string
    firstStr = sortedStrings{1};
    lastStr = sortedStrings{end};
    
    commonPrefix = '';
    for i = 1:min(length(firstStr), length(lastStr))
        if firstStr(i) == lastStr(i)
            commonPrefix = [commonPrefix, firstStr(i)];
        else
            break;
        end
    end
end
