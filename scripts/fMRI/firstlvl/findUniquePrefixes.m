function shortestCommonPrefixes = findShortestCommonPrefixes(tasks)
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
    
    % Find the shortest common prefix for each group and store unique prefixes
    shortestCommonPrefixes = {};
    groupValues = groups.values;
    for i = 1:length(groupValues)
        if length(groupValues{i}) > 1
            shortestCommonPrefix = findShortestCommonPrefix(groupValues{i});
            if ~isempty(shortestCommonPrefix)
                shortestCommonPrefixes{end+1} = shortestCommonPrefix;
            end
        end
    end
    
    % Ensure uniqueness
    shortestCommonPrefixes = unique(shortestCommonPrefixes);
end

function shortestCommonPrefix = findShortestCommonPrefix(strings)
    if length(strings) == 1
        shortestCommonPrefix = strings{1};
        return;
    end
    
    % Sort strings to bring similar strings together
    sortedStrings = sort(strings);
    
    % Start with the first string as the potential common prefix
    commonPrefix = sortedStrings{1};
    
    for i = 2:length(sortedStrings)
        currentString = sortedStrings{i};
        j = 1;
        while j <= length(commonPrefix) && j <= length(currentString) && commonPrefix(j) == currentString(j)
            j = j + 1;
        end
        commonPrefix = commonPrefix(1:j-1);
    end
    
    % Ensure the common prefix is not the full name of any task
    shortestCommonPrefix = commonPrefix;
    for i = 1:length(strings)
        if strncmp(strings{i}, shortestCommonPrefix, length(shortestCommonPrefix)) && length(strings{i}) > length(shortestCommonPrefix)
            shortestCommonPrefix = shortestCommonPrefix(1:end-1);
            break;
        end
    end
end
