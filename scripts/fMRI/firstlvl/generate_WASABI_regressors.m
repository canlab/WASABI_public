function conditions = generate_WASABI_regressors(task, sid, sess, stim_dat, noise_dat, R, mdl_path, varargin)

    if ismac()
        BIDSroot = fullfile('/Volumes', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    elseif ispc()
        BIDSroot = fullfile('\\dartfs-hpc', 'rc', 'lab', 'C', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    else
        BIDSroot = fullfile('//dartfs-hpc', 'rc', 'lab', 'C', 'CANlab', 'labdata', 'data', 'WASABI', '1080_wasabi');
    end

    ses_str=sess;
    
    switch true
        case contains(task, 'bodymap')
            %% 1. Set Bodymap Conditions/Regressors in accordance to your design
            % matrix
            Sitename = varargin{1}{1}; % Grab the charstring from the varargin cell array

            % Create bodymap IV design: Tor: Don't model rest.
            hot = struct('name',{{['hot_', Sitename]}}, 'onset', {{[]}}, 'duration', {{[]}});
            warm = struct('name',{{['warm_', Sitename]}}, 'onset', {{[]}}, 'duration', {{[]}});
            imagine = struct('name',{{['imagine_', Sitename]}}, 'onset', {{[]}}, 'duration', {{[]}});
            imagcue = struct('name',{{['imagcue_', Sitename]}}, 'onset', {{[]}}, 'duration', {{[]}});
            ratings = struct('name',{{'ratings'}}, 'onset', {{[]}}, 'duration', {{[]}});

            %% 2. Data Cleaning
            stim_dat(end-2:end,:) = []   % Delete the last 3 rows of data. Its just time on task.
            numberOfTrials = size(stim_dat,1);

            %%% i. Correct the onset time column if there was a bug with recording the first onset.
            if nnz(stim_dat{2,2} <=2 | stim_dat{2,2} >=3) 
                stim_dat{1,2}=2.75; % Onset timings are totally wrong before session 15 because of a code bug. Before that we will have to make it up until we can mine the Biopac data.
                disp('first stimulus onset time corrected to 2.75 seconds. Please check biopac data for true times.')
            
                % numberOfTrials = size(stim_dat,1)-4;         % Trials are the number of rows, minus header, valence, intensity, and comfort ratings (4)
                % numberOfTrials = size(stim_dat,1);
                for current_row=2:numberOfTrials                    % Process all trials except the the first trial
                    stim_dat{current_row,2}=stim_dat{current_row-1,2}+round(stim_dat{current_row-1,3});
                end
            end
            
            %%% ii. CORRECT STIMULUS trial-types for bodymap
            sess = str2double(sess);               % Makesure the stim_dat is being converted right

            % This session had a very early version of trial ids that were revised later.
            newCondition = [];
            if strcmp(sid, 'SID001651') && sess == 1
                for current_row=1:numberOfTrials
                    if contains(stim_dat{current_row,4}, '3')
                        newCondition = [newCondition 1];
                    elseif contains(stim_dat{current_row,4}, '4')
                        newCondition = [newCondition 2];
                    elseif contains(stim_dat{current_row,4}, '5')                               
                        newCondition = [newCondition 4];
                    elseif contains(stim_dat{current_row,4}, '6')                               
                        newCondition = [newCondition 4];
                    elseif contains(stim_dat{current_row,4}, '7')                               
                        newCondition = [newCondition 5];
                    else
                        newCondition = [newCondition str2num(stim_dat{current_row, 4})];         % All other conditions remain the same
                    end
                end

            % These sessions imagine trials did not separate cue from the imagine trial
            elseif ((strcmp(sid, 'SID001651') || strcmp(sid, 'SID001804')) && sess <= 7) || (strcmp(sid, 'SID001852') && sess <= 4) 
                for current_row=1:numberOfTrials
                    if contains(stim_dat{current_row,4},'3')
                        newCondition = [newCondition 4];
                    elseif contains(stim_dat{current_row,4},'4')                               % reassign the rest trial to a (5)
                        newCondition = [newCondition 5];
                    else
                        newCondition = [newCondition str2num(stim_dat{current_row, 4}{1})];         % All other conditions remain the same
                    end
                end
            
            % These sessions featured the final version of the bodymap paradigm where imagine trial are separated by cue and trial.
            else
                for current_row=1:numberOfTrials
                    if contains(string(stim_dat{current_row,4}),'3') && (current_row==1 || ~contains(string(stim_dat{current_row-1,4}),'3')) % First row is imagine-cue
                        newCondition = [newCondition 3];
                    elseif contains(string(stim_dat{current_row,4}), '3') && contains(string(stim_dat{current_row,4}),'cue')   % imagine trials are always cue (3), Check for cue
                        newCondition = [newCondition 3];
                    elseif contains(string(stim_dat{current_row,4}), '3') && contains(string(stim_dat{current_row-1,4}),'3')   % imagine trials are always cue (3), then trial (4)
                        newCondition = [newCondition 4];
                    elseif contains(stim_dat{current_row,4},'4')                                    % reassign the rest trial to a (5)
                        newCondition = [newCondition 5];
                    else
                        newCondition = [newCondition str2num(stim_dat{current_row, 4}{1})];         % All other conditions remain the same
                    end
                end
            end
            stim_dat.newCondition = newCondition'

            % Add a rating period that will begin after the last trial and
            % last until the end of the scan.
            stim_dat=[stim_dat; {stim_dat{end, 1}+1, stim_dat{end, 2}+stim_dat{end, 3}, 9999, '', '', '', 5}];

            stim_dat

            %% 3. Write out corrected stim_dat as a BIDS .tsv file.
            run=extractBetween(mdl_path, 'run-', filesep);
            outputFile = dir(char(fullfile(BIDSroot, ['sub-', sid], ['ses-', ses_str], 'func', strcat('sub-', sid, '_ses-', ses_str, '_task-', task, '*_run-', run, '*_events.tsv'))));
            outputFile = fullfile(outputFile.folder, outputFile.name)
            writetable(stim_dat, outputFile,  'FileType', 'text',  'Delimiter' , '\t');
            
            %% 4. Fill-out the SPM style design-obj
            for trial = 1:numberOfTrials
                % switch stim_dat{trial,7}              % Column 4 is trial_type; Need to convert 3-cue and 3-trial to 3 and 4 respectively. Converted to Column 7 in code above.
                switch stim_dat.newCondition(trial)
                % switch newCondition(trial)
                    case 1
                        hot.onset{1} = [hot.onset{1} stim_dat{trial,2}];                  % column 2 is onset
                        hot.duration{1} = [hot.duration{1} round(stim_dat{trial,3})];     % column 3 is duration
                    case 2
                        warm.onset{1} = [warm.onset{1} stim_dat{trial,2}];
                        warm.duration{1} = [warm.duration{1} round(stim_dat{trial,3})];
                    case 3
                        imagcue.onset{1} = [imagcue.onset{1} stim_dat{trial,2}];
                        imagcue.duration{1} = [imagcue.duration{1} round(stim_dat{trial,3})];
                    case 4
                        imagine.onset{1} = [imagine.onset{1} stim_dat{trial,2}];
                        imagine.duration{1} = [imagine.duration{1} round(stim_dat{trial,3})];
                    case 5
                        ratings.onset{1} = [ratings.onset{1} stim_dat{trial,2}];
                        ratings.duration{1} = [ratings.duration{1} round(stim_dat{trial,3})];
                end
            end

            %% 5. Save condition structs
            save([mdl_path, hot.name{1}],'-struct','hot');
            save([mdl_path, warm.name{1}],'-struct','warm');
            save([mdl_path, imagine.name{1}],'-struct','imagine');

            save([mdl_path, imagcue.name{1}],'-struct','imagcue');
            save([mdl_path, ratings.name{1}],'-struct','ratings');

            %% 6. Return/Output your conditions
            conditions = {hot.name{1}, warm.name{1}, imagine.name{1} imagcue.name{1}, ratings.name{1}};

        case contains(task, 'movemap')
            stim_dat(end,:) = []   % Delete the last row of data.
            % header = {'row','onset','duration','phase','condition'}
            %% Create movemap IV design: Tor: Don't model rest.
            % Cues
            leftface_cue = struct('name',{{['leftface_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightface_cue = struct('name',{{['rightface_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            leftarm_cue = struct('name',{{['leftarm_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightarm_cue = struct('name',{{['rightarm_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            leftleg_cue = struct('name',{{['leftleg_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightleg_cue = struct('name',{{['rightleg_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            chest_cue = struct('name',{{['chest_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            abdomen_cue = struct('name',{{['abdomen_cue']}}, 'onset', {{[]}}, 'duration', {{[]}});
            % Response Period
            leftface = struct('name',{{['leftface']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightface = struct('name',{{['rightface']}}, 'onset', {{[]}}, 'duration', {{[]}});
            leftarm = struct('name',{{['leftarm']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightarm = struct('name',{{['rightarm']}}, 'onset', {{[]}}, 'duration', {{[]}});
            leftleg = struct('name',{{['leftleg']}}, 'onset', {{[]}}, 'duration', {{[]}});
            rightleg = struct('name',{{['rightleg']}}, 'onset', {{[]}}, 'duration', {{[]}});
            chest = struct('name',{{['chest']}}, 'onset', {{[]}}, 'duration', {{[]}});
            abdomen = struct('name',{{['abdomen']}}, 'onset', {{[]}}, 'duration', {{[]}});

            % Correct the onset time column if there was a bug with recording the first onset.
            if nnz(stim_dat{1,2} <=2 || stim_dat{1,2} >=3) 
                stim_dat{1,2}=2.75; % Onset timings are totally wrong before session 15 because of a code bug. Before that we will have to make it up until we can mine the Biopac data.
                % There was a rather serious problem with recording onsets
                % and durations in the early goings so these had to be
                % corrected in post.
                disp('first stimulus onset time corrected to 2.75 seconds. Please check biopac data for true times.');
                % disp(['duration times are adjusted as ', newDuration]);
            end
            % newDuration=-stim_dat{2,3}+stim_dat{1,3} % Duration timings were also recorded very strangely (large negative numbers)
            newDuration=[];
            conditionNumber=[];

            numberOfTrials = size(stim_dat,1);         % Trials are the number of rows, minus header, valence, intensity, and comfort ratings (4)
%                 for current_row=2:numberOfTrials                    % Process all trials except the first trial
%                     newDuration = [newDuration, -stim_dat{current_row,3}+stim_dat{current_row-1,3}];        % Correct every duration
%                 end
%                 stim_dat.newDuration = newDuration';


            % %%%%% CORRECT STIMULUS trial-types and durations for movemap %%%%%%%
            % Have to combine columns 4 and 5 in order to determine condition
            for current_row=1:numberOfTrials
               condition = strcat(stim_dat{current_row,4}, " ", stim_dat{current_row,5});
               if strcmp(condition, "cue Left Face")
                   % stim_dat{current_row, 6} = 1;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 1];
               elseif strcmp(condition, "movement Left Face")
                   % stim_dat{current_row, 6} = 2;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 2];
               elseif strcmp(condition, "cue Right Face")
                   % stim_dat{current_row, 6} = 3;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 3];
               elseif strcmp(condition, "movement Right Face")
                   % stim_dat{current_row, 6} = 4;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 4];
               elseif strcmp(condition, "cue Left Arm")
                   % stim_dat{current_row, 6} = 5;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 5];
               elseif strcmp(condition, "movement Left Arm")
                   % stim_dat{current_row, 6} = 6;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 6];
               elseif strcmp(condition, "cue Right Arm")
                   % stim_dat{current_row, 6} = 7;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 7];
               elseif strcmp(condition, "movement Right Arm")
                   % stim_dat{current_row, 6} = 8;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 8];
               elseif strcmp(condition, "cue Left Leg")
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 9];
                   % stim_dat{current_row, 6} = 9;
               elseif strcmp(condition, "movement Left Leg")
                   % stim_dat{current_row, 6} = 10;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 10];
               elseif strcmp(condition, "cue Right Leg")
                   % stim_dat{current_row, 6} = 11;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 11];
               elseif strcmp(condition, "movement Right Leg")
                   % stim_dat{current_row, 6} = 12;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 12];
               elseif strcmp(condition, "cue Chest")
                   % stim_dat{current_row, 6} = 13;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 13];
               elseif strcmp(condition, "movement Chest")
                   % stim_dat{current_row, 6} = 14;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 14];
               elseif strcmp(condition, "cue Abdomen")
                   % stim_dat{current_row, 6} = 15;
                   newDuration = [newDuration 1.5];
                   conditionNumber = [conditionNumber 15];
               elseif strcmp(condition, "movement Abdomen")
                   % stim_dat{current_row, 6} = 16;
                   newDuration = [newDuration 16.5];
                   conditionNumber = [conditionNumber 16];
               else
                   % stim_dat{current_row, 6} = 0;
                   newDuration = [newDuration 18];
                   conditionNumber = [conditionNumber 0];
               end
            end
            stim_dat.newDuration = newDuration';
            stim_dat.conditionNumber = conditionNumber';

            % stim_dat{:,6} = newDuration'
            % stim_dat{:,7} = conditionNumber'

            % CORRECT EVERY ONSET
            for current_row=2:numberOfTrials                    % Process all trials except the first trial
                stim_dat{current_row,2}= stim_dat{current_row-1,2}+round(stim_dat{current_row-1,6});  % Correct every onset
            end

            stim_dat
            
            % Swap columns 3 and 6 (duration with newDuration)
            saverows = stim_dat{:,3};
            stim_dat{:,3} = stim_dat{:,6};
            stim_dat{:,6} = stim_dat{:,3};
            stim_dat

            % Write out corrected stim_dat as a BIDS .tsv file.
            run=extractBetween(mdl_path, 'run-', filesep);
            outputFile = dir(char(fullfile(BIDSroot, ['sub-', sid], ['ses-', ses_str], 'func', strcat('sub-', sid, '_ses-', ses_str, '_task-', task, '*_run-', run, '*_events.tsv'))));
            outputFile = fullfile(outputFile.folder, outputFile.name)
            writetable(stim_dat, outputFile,  'FileType', 'text',  'Delimiter' , '\t');

            % initialize SPM style design obj
            for trial = 1:numberOfTrials
                % Append each trial entry to the end of the list (vector)
                % switch stim_dat{trial,6}
                switch stim_dat.conditionNumber(trial)
                % switch conditionNumber(trial)
                    % Cues
                    case 1
                        leftface_cue.onset{1} = [leftface_cue.onset{1} stim_dat{trial,2}];
                        leftface_cue.duration{1} = [leftface_cue.duration{1} round(stim_dat{trial,3})];
                    case 3
                        rightface_cue.onset{1} = [rightface_cue.onset{1} stim_dat{trial,2}];
                        rightface_cue.duration{1} = [rightface_cue.duration{1} round(stim_dat{trial,3})];
                    case 5
                        leftarm_cue.onset{1} = [leftarm_cue.onset{1} stim_dat{trial,2}];
                        leftarm_cue.duration{1} = [leftarm_cue.duration{1} round(stim_dat{trial,3})];
                    case 7
                        rightarm_cue.onset{1} = [rightarm_cue.onset{1} stim_dat{trial,2}];
                        rightarm_cue.duration{1} = [rightarm_cue.duration{1} round(stim_dat{trial,3})];
                    case 9
                        leftleg_cue.onset{1} = [leftleg_cue.onset{1} stim_dat{trial,2}];
                        leftleg_cue.duration{1} = [leftleg_cue.duration{1} round(stim_dat{trial, 3})];
                    case 11
                        rightleg_cue.onset{1} = [rightleg_cue.onset{1} stim_dat{trial,2}];
                        rightleg_cue.duration{1} = [rightleg_cue.duration{1} round(stim_dat{trial,3})];
                    case 13
                        chest_cue.onset{1} = [chest_cue.onset{1} stim_dat{trial,2}];
                        chest_cue.duration{1} = [chest_cue.duration{1} round(stim_dat{trial,3})];
                    case 15
                        abdomen_cue.onset{1} = [abdomen_cue.onset{1} stim_dat{trial,2}];
                        abdomen_cue.duration{1} = [abdomen_cue.duration{1} round(stim_dat{trial,3})];

                    % Responses
                    case 2
                        leftface.onset{1} = [leftface.onset{1} stim_dat{trial,2}];
                        leftface.duration{1} = [leftface.duration{1} round(stim_dat{trial,3})];
                    case 4
                        rightface.onset{1} = [rightface.onset{1} stim_dat{trial,2}];
                        rightface.duration{1} = [rightface.duration{1} round(stim_dat{trial,3})];
                    case 6
                        leftarm.onset{1} = [leftarm.onset{1} stim_dat{trial,2}];
                        leftarm.duration{1} = [leftarm.duration{1} round(stim_dat{trial,3})];
                    case 8
                        rightarm.onset{1} = [rightarm.onset{1} stim_dat{trial,2}];
                        rightarm.duration{1} = [rightarm.duration{1} round(stim_dat{trial,3})];
                    case 10
                        leftleg.onset{1} = [leftleg.onset{1} stim_dat{trial,2}];
                        leftleg.duration{1} = [leftleg.duration{1} round(stim_dat{trial, 3})];
                    case 12
                        rightleg.onset{1} = [rightleg.onset{1} stim_dat{trial,2}];
                        rightleg.duration{1} = [rightleg.duration{1} round(stim_dat{trial,3})];
                    case 14
                        chest.onset{1} = [chest.onset{1} stim_dat{trial,2}];
                        chest.duration{1} = [chest.duration{1} round(stim_dat{trial,3})];
                    case 16
                        abdomen.onset{1} = [abdomen.onset{1} stim_dat{trial,2}];
                        abdomen.duration{1} = [abdomen.duration{1} round(stim_dat{trial,3})];
                end
            end

            % Save Movemap Condition Files
            save([mdl_path, leftface_cue.name{1}],'-struct','leftface_cue');
            save([mdl_path, rightface_cue.name{1}],'-struct','rightface_cue');
            save([mdl_path, leftarm_cue.name{1}],'-struct','leftarm_cue');
            save([mdl_path, rightarm_cue.name{1}],'-struct','rightarm_cue');
            save([mdl_path, leftleg_cue.name{1}],'-struct','leftleg_cue');
            save([mdl_path, rightleg_cue.name{1}],'-struct','rightleg_cue');
            save([mdl_path, chest_cue.name{1}],'-struct','chest_cue');
            save([mdl_path, abdomen_cue.name{1}],'-struct','abdomen_cue');

            save([mdl_path, leftface.name{1}],'-struct','leftface');
            save([mdl_path, rightface.name{1}],'-struct','rightface');
            save([mdl_path, leftarm.name{1}],'-struct','leftarm');
            save([mdl_path, rightarm.name{1}],'-struct','rightarm');
            save([mdl_path, leftleg.name{1}],'-struct','leftleg');
            save([mdl_path, rightleg.name{1}],'-struct','rightleg');
            save([mdl_path, chest.name{1}],'-struct','chest');
            save([mdl_path, abdomen.name{1}],'-struct','abdomen');

            conditions = {leftface_cue.name{1}, rightface_cue.name{1}, leftarm_cue.name{1}, rightarm_cue.name{1}, leftleg_cue.name{1}, rightleg_cue.name{1}, chest_cue.name{1}, abdomen_cue.name{1}, ...
                leftface.name{1}, rightface.name{1}, leftarm.name{1}, rightarm.name{1}, leftleg.name{1}, rightleg.name{1}, chest.name{1}, abdomen.name{1}};

        case contains(task, 'pinellocalizer')
            % [audio1 audio10 audio100 audio11 audio2 audio24 audio25 audio31 audio40 audio41 audio43 audio50 audio52 audio56 audio6 audio67 audio68 audio7 audio72 audio73 audio75 audio77 audio79 audio8 audio80 audio88 audio93 audio96 audio98 audio99 checker12 checker21 checker33 checker4 checker42 checker48 checker51 checker53 checker60 checker64 checker69 checker70 checker71 checker74 checker76 checker84 checker89 checker90 checker91 checker94 visual13 visual14 visual15 visual16 visual17 visual18 visual19 visual20 visual22 visual23 visual26 visual27 visual28 visual29 visual3 visual30 visual32 visual34 visual35 visual36 visual37 visual38 visual39 visual44 visual45 visual46 visual47 visual49 visual5 visual54 visual55 visual57 visual58 visual59 visual61 visual62 visual63 visual65 visual66 visual78 visual81 visual82 visual83 visual85 visual86 visual87 visual9 visual92 visual95 visual97] = set_WASABI_pinel_conditions(stim_dat)
            header = {'trial_type','onset','duration','soa_num','ITI'};
            stim_dat.Properties.VariableNames = header;
            stim_dat(101,:) = [];   % Delete the last row of data. Its just time on task.
            % Use a CANlab function to extract the conditions (event types) and which
            % events belong to each type
            [indic, names] = string2indicator(stim_dat.trial_type);
            indic = logical(indic);
            
            % Write out corrected stim_dat as a BIDS .tsv file.
            run=extractBetween(mdl_path, 'run-', filesep);
            outputFile = dir(char(fullfile(BIDSroot, ['sub-', sid], ['ses-', ses_str], 'func', strcat('sub-', sid, '_ses-', ses_str, '_task-', task, '*_run-', run, '*_events.tsv'))));
            outputFile = fullfile(outputFile.folder, outputFile.name)
            writetable(stim_dat, outputFile,  'FileType', 'text',  'Delimiter' , '\t');
            
            % Get a cell array of onsets for each condition
            [onsets, durations, ~] = deal(cell(1, length(names)));
            for i = 1:length(names)
                onsets{i} = stim_dat.onset(indic(:, i));
                durations{i} = stim_dat.duration(indic(:, i));
            end
% v1 code:  pinel = struct('name',{{['pinel']}}, 'onset', {{[]}}, 'duration', {{[]}});

% v2 code:
%             left={'visual5', 'audio7', 'audio24', 'visual30', 'visual49', 'visual55', 'audio77', 'visual78', 'audio93', 'audio98'};
%             right={'visual9', 'audio10', 'visual22', 'audio25', 'audio40', 'visual58', 'audio72', 'audio73', 'visual86', 'visual87'};
%             comp={'audio6', 'audio8', 'audio11', 'visual14', 'visual15', 'visual20', 'visual26', 'audio31', 'audio41', 'visual45', 'audio50', 'visual54', 'visual57', 'visual66', 'audio80', 'visual83', 'audio96', 'visual97', 'audio99', 'audio100'};
%             mot={'visual5', 'audio7', 'audio24', 'visual30', 'visual49', 'visual55', 'audio77', 'visual78', 'audio93', 'audio98', 'visual9', 'audio10', 'visual22', 'audio25', 'audo40', 'visual58', 'audio72', 'audio73', 'visual86', 'visual87'};
%             lang={'audio1', 'audio2', 'visual13', 'visual16', 'visual17', 'visual29', 'visual37', 'audio43', 'visual46', 'visual47', 'audio52', 'audio56', 'audio59', 'visual65', 'audio67','audio68', 'audio75', 'audio79', 'visual85', 'audio88'};
%             horizontal={'checker4', 'checker21', 'checker51', 'checker60', 'checker64', 'checker74', 'checker76', 'checker84', 'checker90', 'checker91'};
%             vertical={'checker12', 'checker33', 'checker42', 'checker48', 'checker53', 'checker69', 'checker70', 'checker71', 'checker89', 'checker94'};

%             audio = struct('name',{{['audio']}}, 'onset', {{onsets(find(names, contains('audio')))}}, 'duration', {{durations(find(names, contains('audio')))}});
%             checker = struct('name',{{['checker']}}, 'onset', {{onsets(find(names, contains('checker')))}}, 'duration', {{durations(find(names, contains('checker')))}});
%             visual = struct('name',{{['visual']}}, 'onset', {{onsets(find(names, contains('visual')))}}, 'duration', {{durations(find(names, contains('visual')))}});
%             rightbtn = struct('name',{{['rightbtn']}}, 'onset', {{onsets(find(ismember(names, right)))}}, 'duration', {{durations(find(ismember(names, right)))}});
%             leftbtn = struct('name',{{['leftbtn']}}, 'onset', {{onsets(find(ismember(names, left)))}}, 'duration', {{durations(find(ismember(names, left)))}});
%             computation = struct('name',{{['computation']}}, 'onset', {{onsets(find(ismember(names, comp)))}}, 'duration', {{durations(find(ismember(names, comp)))}});
%             motor = struct('name',{{['motor']}}, 'onset', {{onsets(find(ismember(names, mot)))}}, 'duration', {{durations(find(ismember(names, mot)))}});
%             language = struct('name',{{['language']}}, 'onset', {{onsets(find(ismember(names, lang)))}}, 'duration', {{durations(find(ismember(names, lang)))}});
%             horizontalcheck = struct('name',{{['horizontalcheck']}}, 'onset', {{onsets(find(ismember(names, horizontal)))}}, 'duration', {{durations(find(ismember(names, horizontal)))}});
%             verticalcheck = struct('name',{{['verticalcheck']}}, 'onset', {{onsets(find(ismember(names, vertical)))}}, 'duration', {{durations(find(ismember(names, vertical)))}});
% 
%             % Save Pinel Localizer Condition Files
%             save([pwd,'audio'], '-struct', 'audio');
%             save([pwd,'checker'], '-struct', 'checker');
%             save([pwd,'visual'], '-struct', 'visual');
%             save([pwd,'rightbtn'], '-struct', 'rightbtn');
%             save([pwd,'leftbtn'], '-struct', 'leftbtn');
%             save([pwd,'computation'], '-struct', 'computation');
%             save([pwd,'motor'], '-struct', 'motor');
%             save([pwd,'language'], '-struct', 'language');
%             save([pwd,'horizontalcheck'], '-struct', 'horizontalcheck');
%             save([pwd,'verticalcheck'], '-struct', 'verticalcheck');
% 
%             conditions = {{'audio', 'checker','visual','rightbtn','leftbtn','computation','motor','language','horizontalcheck','verticalcheck'}};

            HCheck_trial={'checker4', 'checker21', 'checker51', 'checker60', 'checker64', 'checker74', 'checker76', 'checker84', 'checker90', 'checker91'};
            VCheck_trial={'checker12', 'checker33', 'checker42', 'checker48', 'checker53', 'checker69', 'checker70', 'checker71', 'checker89', 'checker94'};
            VRClick_trial={'visual9', 'visual22', 'visual58', 'visual86', 'visual87'};
            VLClick_trial={'visual5','visual30', 'visual49', 'visual55', 'visual78'};
            VLang_trial={'visual13', 'visual16', 'visual17', 'visual29', 'visual37', 'visual46', 'visual47', 'visual65', 'visual85'};
            VComp_trial={'visual14', 'visual15', 'visual20', 'visual26', 'visual45', 'visual54', 'visual57', 'visual66', 'visual83', 'visual97'};
            ARClick_trial={'audio10', 'audio25', 'audio40', 'audio72', 'audio73'};
            ALClick_trial={'audio7', 'audio24','audio77', 'audio93', 'audio98'};
            ALang_trial={'audio1', 'audio2', 'audio43', 'audio52', 'audio56', 'audio59', 'audio67','audio68', 'audio75', 'audio79', 'audio88'};
            AComp_trial={'audio6', 'audio8', 'audio11', 'audio31', 'audio41', 'audio50', 'audio80', 'audio96', 'audio99', 'audio100'};

            % Regressor structures should have single-cell onset and
            % duration fields with a vector of times in seconds.
            HCheck=struct('name',{{['HCheck']}}, 'onset', {{cell2mat(onsets(find(ismember(names, HCheck_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, HCheck_trial))))}});
            VCheck=struct('name',{{['VCheck']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VCheck_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VCheck_trial))))}});
            VRClick=struct('name',{{['VRClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VRClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VRClick_trial))))}});
            VLClick=struct('name',{{['VLClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VLClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VLClick_trial))))}});
            VLang=struct('name',{{['VLang']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VLang_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VLang_trial))))}});
            VComp=struct('name',{{['VComp']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VComp_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VComp_trial))))}});
            ARClick=struct('name',{{['ARClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ARClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ARClick_trial))))}});
            ALClick=struct('name',{{['ALClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ALClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ALClick_trial))))}});
            ALang=struct('name',{{['ALang']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ALang_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ALang_trial))))}});
            AComp=struct('name',{{['AComp']}}, 'onset', {{cell2mat(onsets(find(ismember(names, AComp_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, AComp_trial))))}});

%             HCheck=struct('name',{{['HCheck']}}, 'onset', {{onsets(find(ismember(names, HCheck_trial)))}}, 'duration', {{durations(find(ismember(names, HCheck_trial)))}});
%             VCheck=struct('name',{{['VCheck']}}, 'onset', {{onsets(find(ismember(names, VCheck_trial)))}}, 'duration', {{durations(find(ismember(names, VCheck_trial)))}});
%             VRClick=struct('name',{{['VRClick']}}, 'onset', {{onsets(find(ismember(names, VRClick_trial)))}}, 'duration', {{durations(find(ismember(names, VRClick_trial)))}});
%             VLClick=struct('name',{{['VLClick']}}, 'onset', {{onsets(find(ismember(names, VLClick_trial)))}}, 'duration', {{durations(find(ismember(names, VLClick_trial)))}});
%             VLang=struct('name',{{['VLang']}}, 'onset', {{onsets(find(ismember(names, VLang_trial)))}}, 'duration', {{durations(find(ismember(names, VLang_trial)))}});
%             VComp=struct('name',{{['VComp']}}, 'onset', {{onsets(find(ismember(names, VComp_trial)))}}, 'duration', {{durations(find(ismember(names, VComp_trial)))}});
%             ARClick=struct('name',{{['ARClick']}}, 'onset', {{onsets(find(ismember(names, ARClick_trial)))}}, 'duration', {{durations(find(ismember(names, ARClick_trial)))}});
%             ALClick=struct('name',{{['ALClick']}}, 'onset', {{onsets(find(ismember(names, ALClick_trial)))}}, 'duration', {{durations(find(ismember(names, ALClick_trial)))}});
%             ALang=struct('name',{{['ALang']}}, 'onset', {{onsets(find(ismember(names, ALang_trial)))}}, 'duration', {{durations(find(ismember(names, ALang_trial)))}});
%             AComp=struct('name',{{['AComp']}}, 'onset', {{onsets(find(ismember(names, AComp_trial)))}}, 'duration', {{durations(find(ismember(names, AComp_trial)))}});

%             % Save Pinel Localizer Condition Files
            save([mdl_path,'HCheck'], '-struct', 'HCheck');
            save([mdl_path,'VCheck'], '-struct', 'VCheck');
            save([mdl_path,'VRClick'], '-struct', 'VRClick');
            save([mdl_path,'VLClick'], '-struct', 'VLClick');
            save([mdl_path,'VLang'], '-struct', 'VLang');
            save([mdl_path,'VComp'], '-struct', 'VComp');
            save([mdl_path,'ARClick'], '-struct', 'ARClick');
            save([mdl_path,'ALClick'], '-struct', 'ALClick');
            save([mdl_path,'ALang'], '-struct', 'ALang');
            save([mdl_path,'AComp'], '-struct', 'AComp');

            conditions = {'HCheck', 'VCheck','VRClick','VLClick','VLang','VComp','ARClick','ALClick','ALang','AComp'};

        case contains(task, 'distractmap')
            % [oneback_trial_start, oneback_heat_start, twoback_trial_start, twoback_heat_trial] = set_WASABI_distractmap_conditions(stim_dat)
            % if width(stim_dat) == 13
            % header={'row','onset','duration','leftclick_rt', 'middleclick_rt', 'rightclick_rt', 'response', 'correct', 'bodySite', 'temperature', 'condition', 'pretrial-jitter', 'posttrial-jitter'}
            if width(stim_dat) == 11
                header = {'row','onset','duration', 'rt','response','correct', 'bodySite', 'temperature', 'condition', 'pretrial-jitter', 'posttrial-jitter'};
            elseif width(stim_dat)==9
                header = {'row','onset','duration', 'rt','response','correct', 'bodySite', 'temperature', 'condition'};
            else
                header = {'row','onset','duration','rt','response','correct', 'bodySite', 'temperature', 'condition', 'pretrial-jitter'};
            end
            stim_dat.Properties.VariableNames = header;
            
            if ~height(stim_dat)==160 % some participants don't have the time on task recorded
                stim_dat(end,:) = [];   % Delete the last row of data. Its just time on task.
            end

            % Write out corrected stim_dat as a BIDS .tsv file.
            run=extractBetween(mdl_path, 'run-', filesep);
            outputFile = dir(char(fullfile(BIDSroot, ['sub-', sid], ['ses-', ses_str], 'func', strcat('sub-', sid, '_ses-', ses_str, '_task-', task, '*_run-', run, '*_events.tsv'))));
            outputFile = fullfile(outputFile.folder, outputFile.name)
            writetable(stim_dat, outputFile,  'FileType', 'text',  'Delimiter' , '\t');

            % Use a CANlab function to extract the conditions (event types) and which
            % events belong to each type
            [indic, names] = string2indicator(stim_dat.condition);
            indic = logical(indic);
            % Get a cell array of onsets for each condition
            [onsets, durations, ~] = deal(cell(1, length(names)));
            for i = 1:length(names)
                onsets{i} = stim_dat.onset(indic(:, i));
                durations{i} = stim_dat.duration(indic(:, i));
            end

            % for DistractMap v3.0.0
            % 2-back vs. Rest 
            % 4-second pre-heat period
            % 16-second stimulation/10-second peak stimulation period
            if contains(names{1}, '2back Instructions')
                % names = {'2back Instructions'}    {'2back-nostim'}x30    {'2back-stim'}x60    {'2back-stim Rating'}    {'PostTrialFixation'}    {'Rest-NoStim'}x6    {'Rest-Stim'}x3    {'Rest-Stim Rating'}
    
                rest_noheat = struct('name',{{'rest_noheat'}}, 'onset', {{[]}}, 'duration', {{[]}});
                rest_preheat = struct('name',{{'rest_preheat'}}, 'onset', {{[]}}, 'duration', {{[]}});
                rest_heat = struct('name',{{'rest_heat'}}, 'onset', {{[]}}, 'duration', {{[]}});
    
                twoback_noheat = struct('name',{{'twoback_noheat'}}, 'onset', {{[]}}, 'duration', {{[]}});
                twoback_preheat = struct('name',{{'twoback_preheat'}}, 'onset', {{[]}}, 'duration', {{[]}});
                twoback_heat = struct('name',{{'twoback_heat'}}, 'onset', {{[]}}, 'duration', {{[]}});

                twoback_noheat.onset = onsets{2}'; twoback_noheat.duration = ones(1, length(onsets{2}))*20;

                rest_noheat.onset = onsets{6}'; rest_noheat.duration = durations{6}';

                twoback.onset = onsets{3}(1:10:end)'; twoback.duration = reshape(durations{3}, 10, 6);
                % Heat onsets occur at the fourth trial onset of every condition.
                twoback_preheat.onset = twoback.onset; twoback_preheat.duration = sum(twoback.duration(1:2, :));
                twoback_heat.onset = onsets{3}(3:10:end)'; twoback_heat.duration = sum(twoback.duration(3:8, :));

                % Heat onsets occur at the fourth trial onset of every condition.
                rest_preheat.onset = onsets{7}'; rest_preheat.duration = ones(1, length(onsets{7}))*4; % 4 seconds at the start of every rest onset
                rest_heat.onset = (onsets{7}+4)'; rest_heat.duration = (durations{7}-4)';

                % The data has to be stored in a cell!
                rest_noheat.onset={rest_noheat.onset}; 
                rest_preheat.onset={rest_preheat.onset};
                rest_heat.onset={rest_heat.onset};
                rest_noheat.duration={rest_noheat.duration}; 
                rest_preheat.duration={rest_preheat.duration};
                rest_heat.duration={rest_heat.duration};
                
                twoback_noheat.onset={twoback_noheat.onset}; 
                twoback_preheat.onset={twoback_preheat.onset};
                twoback_heat.onset={twoback_heat.onset};
                twoback_noheat.duration={twoback_noheat.duration}; 
                twoback_preheat.duration={twoback_preheat.duration};
                twoback_heat.duration={twoback_heat.duration};

                save([mdl_path,'rest_noheat'], '-struct', 'rest_noheat');
                save([mdl_path,'rest_preheat'], '-struct', 'rest_preheat');
                save([mdl_path,'rest_heat'], '-struct', 'rest_heat');

                save([mdl_path,'twoback_noheat'], '-struct', 'twoback_noheat');
                save([mdl_path,'twoback_preheat'], '-struct', 'twoback_preheat');
                save([mdl_path,'twoback_heat'], '-struct', 'twoback_heat');

                conditions = {'rest_noheat', 'rest_preheat', 'rest_heat', 'twoback_noheat', 'twoback_preheat', 'twoback_heat'};



            else
                % temporarily add this; Remove this later!
                % varargin{1}{1}=char(stim_dat.bodySite(end))


                % names = {'1back'}    {'1back Instructions'}    {'1back Rating'}    {'2back'}    {'2back Instructions'}    {'2back Rating'}


                % Older versions:
                % Oh no...durations have to be recomputed by summing the
                % durations of the trials that comprise them? Maybe not...Given
                % 14 seconds every trial, 7 trials each, 3*2= 6 seconds for
                % every pre-heat duration, and 4*2(8) seconds for every heat
                % duration...

                % Sometimes its 10 trials each, 3*2=6 seconds for every
                % pre-heat duration and 7*2=14 seconds for every heat duration

                oneback_trial_start_control = struct('name',{{['oneback_trial_start_control']}}, 'onset', [], 'duration', []);
                twoback_trial_start_control = struct('name',{{['twoback_trial_start_control']}}, 'onset', [], 'duration', []);
                oneback_trial_start_exp = struct('name',{{['oneback_trial_start_exp']}}, 'onset', [], 'duration', []);
                twoback_trial_start_exp = struct('name',{{['twoback_trial_start_exp']}}, 'onset', [], 'duration', []);

                
                % Left Face is the control Condition
                % Set trial_start onsets:
                if contains(varargin{1}{1}, 'leftface')
                    if length(names)==2 % early version with just 1back vs. 2back for SID001651 I think.
                        oneback_trial_start_control.onset = onsets{1}'; oneback_trial_start_control.duration = durations{1}';
                        twoback_trial_start_control.onset = onsets{2}'; twoback_trial_start_control.duration = durations{2}';
                    else
                        oneback_trial_start_control.onset = onsets{1}'; oneback_trial_start_control.duration = durations{1}';
                        twoback_trial_start_control.onset = onsets{4}'; twoback_trial_start_control.duration = durations{4}';
                    end
                else
                    if length(names)==2 % early version with just 1back vs. 2back for SID001651 I think.
                        oneback_trial_start_exp.onset = onsets{1}'; oneback_trial_start_exp.duration = durations{1}';
                        twoback_trial_start_exp.onset = onsets{2}'; twoback_trial_start_exp.duration = durations{2}';
                    else
                        oneback_trial_start_exp.onset = onsets{1}'; oneback_trial_start_exp.duration = durations{1}';
                        twoback_trial_start_exp.onset = onsets{4}'; twoback_trial_start_exp.duration = durations{4}';
                    end
                end

                if contains(varargin{1}{1}, 'leftface')
                    % Only recorded onsets of 8 trials per type
                    if mod(numel(oneback_trial_start_control.onset), 8)==0
                        oneback_noheat_control.onset = oneback_trial_start_control.onset; oneback_noheat_control.duration = ones(1, length(oneback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_control.onset = oneback_trial_start_control.onset+6; oneback_heat_control.duration = ones(1, length(oneback_heat_control.onset))*14;

                        twoback_noheat_control.onset = twoback_trial_start_control.onset; twoback_noheat_control.duration = ones(1, length(twoback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_control.onset = twoback_noheat_control.onset+6; twoback_heat_control.duration = ones(1, length(twoback_heat_control.onset))*14;
                    end
                    % Trial series onsets that occur every 7 trials.
                    if mod(numel(oneback_trial_start_control.onset), 7)==0
                        oneback_noheat_control.onset = oneback_trial_start_control.onset(1:7:end); oneback_noheat_control.duration = ones(1, length(oneback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_control.onset = oneback_trial_start_control.onset(4:4:end); oneback_heat_control.duration = ones(1, length(oneback_heat_control.onset))*8;

                        twoback_noheat_control.onset = twoback_trial_start_control.onset(1:7:end); twoback_noheat_control.duration = ones(1, length(twoback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_control.onset = twoback_noheat_control.onset(4:4:end); twoback_heat_control.duration = ones(1, length(twoback_heat_control.onset))*8;
                        % Trial series onsets that occur every 10 trials.
                    end
                    if mod(numel(oneback_trial_start_control.onset), 10)==0
                        oneback_noheat_control.onset = oneback_trial_start_control.onset(1:10:end); oneback_noheat_control.duration = ones(1, length(oneback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_control.onset = oneback_trial_start_control.onset(4:6:end); oneback_heat_control.duration = ones(1, length(oneback_heat_control.onset))*14;

                        twoback_noheat_control.onset = twoback_trial_start_control.onset(1:10:end); twoback_noheat_control.duration = ones(1, length(twoback_noheat_control.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_control.onset = twoback_noheat_control.onset(4:6:end); twoback_heat_control.duration = ones(1, length(twoback_heat_control.onset))*14;
                    end
                else
                    % Only recorded onsets of 8 trials per type
                    if mod(numel(oneback_trial_start_exp.onset), 8)==0
                        oneback_noheat_exp.onset = oneback_trial_start_exp.onset; oneback_noheat_exp.duration = ones(1, length(oneback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_exp.onset = oneback_trial_start_exp.onset+6; oneback_heat_exp.duration = ones(1, length(oneback_heat_exp.onset))*14;

                        twoback_noheat_exp.onset = twoback_trial_start_exp.onset; twoback_noheat_exp.duration = ones(1, length(twoback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_exp.onset = twoback_trial_start_exp.onset+6; twoback_heat_exp.duration = ones(1, length(twoback_heat_exp.onset))*14;
                    end
                    % Trial series onsets that occur every 7 trials.
                    if mod(numel(oneback_trial_start_exp.onset), 7)==0
                        oneback_noheat_exp.onset = oneback_trial_start_exp.onset(1:7:end); oneback_noheat_exp.duration = ones(1, length(oneback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_exp.onset = oneback_trial_start_exp.onset(4:7:end); oneback_heat_exp.duration = ones(1, length(oneback_heat_exp.onset))*8;

                        twoback_noheat_exp.onset = twoback_trial_start_exp.onset(1:7:end); twoback_noheat_exp.duration = ones(1, length(twoback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_exp.onset = twoback_trial_start_exp.onset(4:7:end); twoback_heat_exp.duration = ones(1, length(twoback_heat_exp.onset))*8;
                    end
                    % Trial series onsets that occur every 10 trials.
                    if mod(numel(oneback_trial_start_exp.onset), 10)==0
                        oneback_noheat_exp.onset = oneback_trial_start_exp.onset(1:10:end); oneback_noheat_exp.duration = ones(1, length(oneback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        oneback_heat_exp.onset = oneback_trial_start_exp.onset(4:10:end); oneback_heat_exp.duration = ones(1, length(oneback_heat_exp.onset))*14;

                        twoback_noheat_exp.onset = twoback_trial_start_exp.onset(1:10:end); twoback_noheat_exp.duration = ones(1, length(twoback_noheat_exp.onset))*6;
                        % Heat onsets occur at the fourth trial onset of every condition.
                        twoback_heat_exp.onset = twoback_trial_start_exp.onset(4:10:end); twoback_heat_exp.duration = ones(1, length(twoback_heat_exp.onset))*14;
                    end
                end

                if contains(varargin{1}{1}, 'leftface')
                    % for pre-DistractMap v3.0.0
                    oneback_noheat_control = struct('name',{{['oneback_noheat_control']}}, 'onset', {{oneback_noheat_control.onset}}, 'duration', {{oneback_noheat_control.duration}});
                    oneback_heat_control = struct('name',{{['oneback_heat_control']}}, 'onset', {{oneback_heat_control.onset}}, 'duration', {{oneback_heat_control.duration}});

                    twoback_noheat_control = struct('name',{{['twoback_noheat_control']}}, 'onset', {{twoback_noheat_control.onset}}, 'duration', {{twoback_noheat_control.duration}});
                    twoback_heat_control = struct('name',{{['twoback_heat_control']}}, 'onset', {{[twoback_heat_control.onset]}}, 'duration', {{twoback_heat_control.duration}});
                else
                    oneback_noheat_exp = struct('name',{{['oneback_noheat_exp']}}, 'onset', {{oneback_noheat_exp.onset}}, 'duration', {{oneback_noheat_exp.duration}});
                    oneback_heat_exp = struct('name',{{['oneback_heat_exp']}}, 'onset', {{oneback_heat_exp.onset}}, 'duration', {{oneback_heat_exp.duration}});

                    twoback_noheat_exp = struct('name',{{['twoback_noheat_exp']}}, 'onset', {{twoback_noheat_exp.onset}}, 'duration', {{twoback_noheat_exp.duration}});
                    twoback_heat_exp = struct('name',{{['twoback_heat_exp']}}, 'onset', {{twoback_heat_exp.onset}}, 'duration', {{twoback_heat_exp.duration}});
                end

                % Save
                if contains(varargin{1}{1}, 'leftface')
                    save([mdl_path,'oneback_noheat_control'], '-struct', 'oneback_noheat_control');
                    save([mdl_path,'oneback_heat_control'], '-struct', 'oneback_heat_control');
                    save([mdl_path,'twoback_noheat_control'], '-struct', 'twoback_noheat_control');
                    save([mdl_path,'twoback_heat_control'], '-struct', 'twoback_heat_control');
                    conditions = {'oneback_noheat_control', 'oneback_heat_control', 'twoback_noheat_control', 'twoback_heat_control'};
                else
                    save([mdl_path,'oneback_noheat_exp'], '-struct', 'oneback_noheat_exp');
                    save([mdl_path,'oneback_heat_exp'], '-struct', 'oneback_heat_exp');
                    save([mdl_path,'twoback_noheat_exp'], '-struct', 'twoback_noheat_exp');
                    save([mdl_path,'twoback_heat_exp'], '-struct', 'twoback_heat_exp');
                    conditions = {'oneback_noheat_exp', 'oneback_heat_exp', 'twoback_noheat_exp', 'twoback_heat_exp'};
                end


                %             if length(names)==2
                %                 if contains(varargin{1}{1}, 'leftface')
                %                     oneback_trial_start_control.onset = onsets{1}'; oneback_trial_start_control.duration = durations{1}';
                %                     twoback_trial_start_control.onset = onsets{2}'; twoback_trial_start_control.duration = durations{2}';
                %
                %                     save([mdl_path,'oneback_trial_start_control'], '-struct', 'oneback_trial_start_control');
                %                     save([mdl_path,'twoback_trial_start_control'], '-struct', 'twoback_trial_start_control');
                %                     conditions = {'oneback_trial_start_control', 'twoback_trial_start_control'};
                %                 else
                %                     oneback_trial_start_exp.onset = onsets{1}'; oneback_trial_start_exp.duration = durations{1}';
                %                     twoback_trial_start_exp.onset = onsets{2}'; twoback_trial_start_exp.duration = durations{2}';
                %                     save([mdl_path,'oneback_trial_start_exp'], '-struct', 'oneback_trial_start_exp');
                %                     save([mdl_path,'twoback_trial_start_exp'], '-struct', 'twoback_trial_start_exp');
                %                     conditions = {'oneback_trial_start_exp', 'twoback_trial_start_exp'};
                %                 end
                %             else
                %                 if contains(varargin{1}{1}, 'leftface') % leftface is the control region
                %                     oneback_trial_start_control.onset = onsets{1}'; oneback_trial_start_control.duration = durations{1}';
                %                     % Trial series onsets occur every 7 trials or
                %                     % 10 trials for 1804....
                %                     oneback_noheat_control.onset = oneback_trial_start_control.onset(1:7:end); oneback_noheat_control.duration = ones(1, length(oneback_trial_start_control.onset))*6;
                %                     % Heat onsets occur at the fourth trial onset of every condition.
                %                     oneback_heat_control.onset = oneback_trial_start_control.onset(4:4:end); oneback_heat_control.duration = ones(1, length(oneback_heat_control.onset))*8;
                %
                %                     twoback_trial_start_control.onset = onsets{4}'; twoback_trial_start_control.duration = durations{4}';
                %                     % Trial series onsets occur every 7 trials.
                %                     twoback_noheat_control.onset = twoback_trial_start_control.onset(1:7:end); twoback_noheat_control.duration = ones(1, length(twoback_noheat_control.onset))*6;
                %                     % Heat onsets occur at the fourth trial onset of every condition.
                %                     twoback_heat_control.onset = twoback_noheat_control.onset(4:4:end); twoback_heat_control.duration = ones(1, length(twoback_heat_control.onset))*8;
                %                     save([mdl_path,'oneback_noheat_control'], '-struct', 'oneback_noheat_control');
                %                     save([mdl_path,'oneback_heat_control'], '-struct', 'oneback_heat_control');
                %                     save([mdl_path,'twoback_noheat_control'], '-struct', 'twoback_noheat_control');
                %                     save([mdl_path,'twoback_heat_control'], '-struct', 'twoback_heat_control');
                %                     conditions = {'oneback_noheat_control', 'oneback_heat_control', 'twoback_noheat_control', 'twoback_heat_control'};
                %                 else
                %                     oneback_trial_start_exp.onset = onsets{1}'; oneback_trial_start_exp.duration = durations{1}';
                %                     % Trial series onsets occur every 7 trials.
                %                     oneback_noheat_exp.onset = oneback_trial_start_exp.onset(1:7:end); oneback_noheat_exp.duration = ones(1, length(oneback_trial_start_exp.onset))*6;
                %                     % Heat onsets occur at the fourth trial onset of every condition.
                %                     oneback_heat_exp.onset = oneback_trial_start_exp.onset(4:4:end); oneback_heat_exp.duration = ones(1, length(oneback_heat_exp.onset))*8;
                %
                %                     twoback_trial_start_exp.onset = onsets{4}'; twoback_trial_start_exp.duration = durations{4}';
                %                     % Trial series onsets occur every 7 trials.
                %                     twoback_noheat_exp.onset = twoback_trial_start_exp.onset(1:7:end); twoback_noheat_exp.duration = ones(1, length(twoback_noheat_exp.onset))*6;
                %                     % Heat onsets occur at the fourth trial onset of every condition.
                %                     twoback_heat_exp.onset = twoback_noheat_exp.onset(4:4:end); twoback_heat_exp.duration = ones(1, length(twoback_heat_exp.onset))*8;
                %                     save([mdl_path,'oneback_noheat_exp'], '-struct', 'oneback_noheat_exp');
                %                     save([mdl_path,'oneback_heat_exp'], '-struct', 'oneback_heat_exp');
                %                     save([mdl_path,'twoback_noheat_exp'], '-struct', 'twoback_noheat_exp');
                %                     save([mdl_path,'twoback_heat_exp'], '-struct', 'twoback_heat_exp');
                %                     conditions = {'oneback_noheat_exp', 'oneback_heat_exp', 'twoback_noheat_exp', 'twoback_heat_exp'};
                %                 end
            end


        case contains(task, 'acceptmap')
            % [heat_trial] = set_WASABI_acceptmap_conditions(stim_dat)
            header = {'row','onset','duration','intensity','bodySite','temperature', 'condition', 'pretrial-jitter'};
            stim_dat.Properties.VariableNames = header;
            stim_dat(end-14:end,:) = [];    % Delete the last 14 rows, which don't have onset/duration data
            
            % Write out corrected stim_dat as a BIDS .tsv file.
            run=extractBetween(mdl_path, 'run-', filesep);
            outputFile = dir(char(fullfile(BIDSroot, ['sub-', sid], ['ses-', ses_str], 'func', strcat('sub-', sid, '_ses-', ses_str, '_task-', task, '*_run-', run, '*_events.tsv'))));
            outputFile = fullfile(outputFile.folder, outputFile.name)
            writetable(stim_dat, outputFile,  'FileType', 'text',  'Delimiter' , '\t');

            % Use a CANlab function to extract the conditions (event types) and which
            % events belong to each type
            [indic, names] = string2indicator(stim_dat.condition);
            indic = logical(indic);
            % Get a cell array of onsets for each condition
            [onsets, durations, ~] = deal(cell(1, length(names)));
            for i = 1:length(names)
                onsets{i} = stim_dat.onset(indic(:, i));
                durations{i} = stim_dat.duration(indic(:, i));
            end    
            
            % names = {'Phase Instruction'}    {'Phase '}    {'Intensity Rating'} 

            acceptmap = struct('name',{{[names{2}]}}, 'onset', {{[]}}, 'duration', {{[]}});
            acceptmap.onset=cell2mat(onsets');
            acceptmap.durations=cell2mat(durations');

            % Regressor structures should have single-cell onset and
            % duration fields with a vector of times in seconds.
            accept_exp
            accept_control

            experience_exp
            experience_control

            trial_ratings
            postrun_ratings

            % HCheck=struct('name',{{['HCheck']}}, 'onset', {{cell2mat(onsets(find(ismember(names, HCheck_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, HCheck_trial))))}});
            % VCheck=struct('name',{{['VCheck']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VCheck_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VCheck_trial))))}});
            % VRClick=struct('name',{{['VRClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VRClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VRClick_trial))))}});
            % VLClick=struct('name',{{['VLClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VLClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VLClick_trial))))}});
            % VLang=struct('name',{{['VLang']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VLang_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VLang_trial))))}});
            % VComp=struct('name',{{['VComp']}}, 'onset', {{cell2mat(onsets(find(ismember(names, VComp_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, VComp_trial))))}});
            % ARClick=struct('name',{{['ARClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ARClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ARClick_trial))))}});
            % ALClick=struct('name',{{['ALClick']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ALClick_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ALClick_trial))))}});
            % ALang=struct('name',{{['ALang']}}, 'onset', {{cell2mat(onsets(find(ismember(names, ALang_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, ALang_trial))))}});
            % AComp=struct('name',{{['AComp']}}, 'onset', {{cell2mat(onsets(find(ismember(names, AComp_trial))))}}, 'duration', {{cell2mat(durations(find(ismember(names, AComp_trial))))}});

            % Save Pinel Localizer Condition Files
            save([mdl_path,'HCheck'], '-struct', 'HCheck');
            save([mdl_path,'VCheck'], '-struct', 'VCheck');
            save([mdl_path,'VRClick'], '-struct', 'VRClick');
            save([mdl_path,'VLClick'], '-struct', 'VLClick');
            save([mdl_path,'VLang'], '-struct', 'VLang');
            save([mdl_path,'VComp'], '-struct', 'VComp');
            save([mdl_path,'ARClick'], '-struct', 'ARClick');
            save([mdl_path,'ALClick'], '-struct', 'ALClick');
            save([mdl_path,'ALang'], '-struct', 'ALang');
            save([mdl_path,'AComp'], '-struct', 'AComp');

            conditions = {'HCheck', 'VCheck','VRClick','VLClick','VLang','VComp','ARClick','ALClick','ALang','AComp'};

            % Save Acceptmap Condition Files
            save([mdl_path,names{2}], '-struct', 'acceptmap');

            conditions = {'accept_exp', 'accept_control', 'experience_exp', 'experience_control', 'trial_ratings', 'postrun_ratings'};

        case contains(task, 'hyperalignment')
            conditions = {'kungfury', 'inscapes', 'restingstate'}

    end

    %%%%%%%% GENERATE HEADMOTION REGRESSORS %%%%%%%%%%%%%%%%%%%
    %% create noise vector design
    % Add 24 Motion Corrections + CSF with and without Whitematter

    R_headmotion=[];
    noise_hdr = cellstr(noise_dat.Properties.VariableNames);
    % CSF and/or White Matter
    for m = 1:size(noise_dat,2)
        this_col = noise_dat{:,m};
        noise_dat(isnan(this_col),m) = {nanmean(this_col)}; % Replace all nans with mean

        % if strcmp('csf',noise_hdr{m})==1 || strcmp('white_matter',noise_hdr{m})==1    % With White Matter
        if strcmp('csf',noise_hdr{m})==1    % Without White Matter. Compare the VIFs of these models.
            R_headmotion=[m,R_headmotion];
        end
    end
    noise_idx=size(R_headmotion, 2);

    xindex=find(strcmp(noise_hdr,'trans_x')==1);
    Mindex=[xindex:xindex+23];
    R_headmotion=[R_headmotion Mindex];
    
    
    R = [R, noise_dat{:,R_headmotion}];
    R = unique(R', 'rows', 'stable')';  % remove any redundant rows. Keep the same order of regressors otherwise.
    
    %% Export noise plots
    figure; 
%     plot(R(:,1:2)); legend({'csf' 'white matter'});
    plot(R(:,1:noise_idx)); legend({'csf'}) % Without white matter
    title('Nuisance regressors')
    fig = gcf;
    exportgraphics(fig, [mdl_path, sid, '_', ses_str, '_', task, '_', 'nuisance_regressor_plot.png']);
    savefig([mdl_path, sid, '_', ses_str, '_', task, '_', 'nuisance_regressor_plot.fig']);
    
%     figure; plot(R(:,3:26));
    figure; plot(R(:,noise_idx:end)); % Without white matter
    legend({'trans x' ...
        'trans x derivative1' ... 
        'trans x derivative1_power2' ...      
        'trans x power2' ...                  
        'trans y' ...                         
        'trans y derivative1' ...             
        'trans y derivative1 power2' ...      
        'trans y power2' ...                  
        'trans z' ...                         
        'trans z derivative1' ...             
        'trans z power2' ...                  
        'trans z derivative1 power2' ...      
        'rot x' ...                           
        'rot x derivative1' ...               
        'rot x derivative1 power2' ...        
        'rot x power2' ...                    
        'rot y' ...                           
        'rot y derivative1' ...               
        'rot y derivative1 power2' ...        
        'rot y power2' ...                    
        'rot z' ...                           
        'rot z derivative1' ...               
        'rot z derivative1 power2' ...        
        'rot z power2'});
    title('Movement regressors')
    fig = gcf;
    exportgraphics(fig, [mdl_path, sid, '_', ses_str, '_', task, '_', 'movement_regressor_plot.png']);
    savefig([mdl_path, sid, '_', ses_str, '_', task, '_', 'movement_regressor_plot.fig']);


%     if ~useAROMA
%         aromaCol = cellfun(@(x1)(logical(any(x1))),strfind(noise_hdr,'aroma'));
%         R = noise_dat{1}(:,~aromaCol);
%     else
%         R = noise_dat{1}; % it's important to name this R, otherwise SPM won't be able to find it
%     end     

%    R=R(:,R_headmotion);

    save([mdl_path, 'noise_model', '.mat'], 'R')

end