function groups = groupTasks(tasks)
    % Ensure the input is a cell array of strings
    if ~iscell(tasks) || ~all(cellfun(@ischar, tasks))
        error('Input must be a cell array of strings');
    end
    
    % Set a threshold for similarity (you might need to adjust this)
    similarityThreshold = 5;
    
    % Initialize the groups cell array
    groups = {};
    
    % Loop through each task
    for i = 1:length(tasks)
        % Flag to check if the current task has been grouped
        isGrouped = false;
        
        % Loop through existing groups
        for j = 1:length(groups)
            % Calculate the Levenshtein distance between the current task and the first task in the current group
            dist = levenshteinDistance(tasks{i}, groups{j}{1});
            
            % If the distance is below the threshold, add the task to the current group
            if dist <= similarityThreshold
                groups{j}{end+1} = tasks{i};
                isGrouped = true;
                break;
            end
        end
        
        % If the task hasn't been grouped, create a new group
        if ~isGrouped
            groups{end+1} = {tasks{i}};
        end
    end
end

function distance = levenshteinDistance(str1, str2)
    % Calculate the Levenshtein distance between two strings
    lenStr1 = length(str1);
    lenStr2 = length(str2);
    matrix = zeros(lenStr1+1, lenStr2+1);
    for i = 0:lenStr1
        matrix(i+1,1) = i;
    end
    for j = 0:lenStr2
        matrix(1,j+1) = j;
    end
    for i = 1:lenStr1
        for j = 1:lenStr2
            cost = (str1(i) ~= str2(j));
            matrix(i+1,j+1) = min([matrix(i,j+1)+1, matrix(i+1,j)+1, matrix(i,j)+cost]);
        end
    end
    distance = matrix(lenStr1+1, lenStr2+1);
end
