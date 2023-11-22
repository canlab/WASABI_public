function [sub, ses, run, task] = getBIDSSubSesRunTask(bids_filename)
    % Extracts sub, ses, run, and task values from a BIDS filename or cell
    % array of BIDS filenames
    % Updated: Michael Sun, Ph.D.

    % Determine if the input is a cell array
    if ~iscell(bids_filename)
        bids_filename = {bids_filename}; % Convert to cell array for uniformity
    end

    % Initialize the output cell arrays
    sub = cell(size(bids_filename));
    ses = cell(size(bids_filename));
    run = cell(size(bids_filename));
    task = cell(size(bids_filename));

    for i = 1:length(bids_filename)
        fname = bids_filename{i};
        
        % Extract the subject, session, run, and task from the filename
        sub{i} = regexp(fname, 'sub-([^\-_/]+)', 'tokens', 'once');
        ses{i} = regexp(fname, 'ses-([^\-_/]+)', 'tokens', 'once');
        run{i} = regexp(fname, 'run-([^\-_/]+)', 'tokens', 'once');
        task{i} = regexp(fname, 'task-([^\-_/]+)', 'tokens', 'once');

        sub{i}=sub{i}{1};
        ses{i}=ses{i}{1};
        run{i}=run{i}{1};
        task{i}=task{i}{1};
    end

    % If only one filename was provided, convert from cell array to string
    if length(bids_filename) == 1
        sub = char(sub{1});
        ses = char(ses{1});
        run = char(run{1});
        task = char(task{1});
    end
end

