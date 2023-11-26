function [R, R_hdr, n_spike_regs,n_spike_regs_percent] = create_noise_regressors(func, fmriprep_confounds_tsv, varargin)
    % create_noise_regressors - Function to create noise regressors for fMRI data analysis.
    %
    % Inputs:
    %   func - String, path to the functional MRI data file (.nii or .nii.gz).
    %   fmriprep_confounds_tsv - String, path to the fmriprep confounds file (.tsv).
    %   varargin - Additional optional arguments.
    %
    % Outputs:
    %   R - Matrix containing the noise regressors.
    %   R_hdr - Cell array containing the header names of the noise regressors.
    %   n_spike_regs - Number of spike regressors.
    %   n_spike_percent - Percentage of total volumes identified as spikes.
    %
    % Example usage:
    %   [R, R_hdr, n_spike_regs, n_spike_percent] = create_noise_regressors(func, fmriprep_confounds_tsv);
    %
    % Author: Michael Sun, Ph.D.
    % Copyright 2023 Dartmouth College
    %     This program is free software: you can redistribute it and/or modify
    %     it under the terms of the GNU General Public License as published by
    %     the Free Software Foundation, either version 3 of the License, or
    %     (at your option) any later version.
    %
    %     This program is distributed in the hope that it will be useful,
    %     but WITHOUT ANY WARRANTY; without even the implied warranty of
    %     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    %     GNU General Public License for more details.
    %
    %     You should have received a copy of the GNU General Public License
    %     along with this program.  If not, see <http://www.gnu.org/licenses/>.

    % Bug fixing
    % addpath(genpath('/dartfs-hpc/rc/lab/C/CANlab/labdata/projects/WASABI/software'))
    % addpath '/dartfs-hpc/rc/lab/C/CANlab/modules/spm12'
    % 
    % func =    '\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\fmriprep\sub-SID000002\ses-21\func\sub-SID000002_ses-21_task-distractmap_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii'
    % funcgz='\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\fmriprep\sub-SID000002\ses-21\func\sub-SID000002_ses-21_task-distractmap_run-01_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'
    % fmriprep_confounds_tsv = '\\dartfs-hpc\rc\lab\C\CANlab\labdata\data\WASABI\derivatives\fmriprep\sub-SID000002\ses-21\func\sub-SID000002_ses-21_task-distractmap_run-01_desc-confounds_timeseries.tsv'
    % func=strrep(func, '\', filesep)
    % funcgz=strrep(funcgz, '\', filesep)
    % fmriprep_confounds_tsv = strrep(fmriprep_confounds_tsv, '\',filesep);
    % fmriprep_confounds_dat =    importBIDSfile(fmriprep_confounds_tsv);
    % func_img=fmri_data(func);
    % noiseopts=[];

    % Initialize input parser
    p = inputParser;

    % Set up parsing schema
    addRequired(p, 'func');
    addRequired(p, 'noise_dat');
    addParameter(p, 'noiseopts',[], @isstruct);

    % Parse the input
    parse(p, func, fmriprep_confounds_tsv, varargin{:});
    noiseopts = p.Results.noiseopts;

    % If its empty, use CANlab Defaults
    if isempty(noiseopts)
        noiseopts.spike_def='CANlab';
        noiseopts.canlabmethod='default';
        noiseopts.rmssd_movie=1;
        noiseopts.spike_additional_vols=0;
        noiseopts.spikes_percent_threshold=100; % We don't typically scrub for spikes
        noiseopts.dvars_threshold=2;
        noiseopts.movement_regs=24;
        noiseopts.csf=1;
        noiseopts.wm=0;
        noiseopts.acompcor=6;
        noiseopts.tcompcor=6;
        noiseopts.global=0;
        
        % Not yet implemented:
        % funcTR = niftiinfo(funcname).PixelDimension(4);
        % if funcTR < 2
        %     noiseopts.fastTR=1;
        % end
        % noiseopts.dvarsopts; % fmriprep vs. rmssd_movie()
        % noiseopts.global;
        % noiseopts.fdspikecutoff=0.5;
        % noiseopts.stddvarscutoff=2;
        % noiseopts.icaaroma;  % Useful when dealing with resting state
        % data, but less helpful with task-based data.
        % noiseopts.pcadenoising;
    end

    R = table; % Initialize the R table;
    R_hdr = {}; % Initialize the R_hdr cell-array;
    fmriprep_confounds_dat = importBIDSfile(fmriprep_confounds_tsv);
    noise_hdr = fmriprep_confounds_dat.Properties.VariableNames;
    % replace NaNs in first row with Os
    wh_replace = ismissing(fmriprep_confounds_dat(1,:));
    if any(wh_replace)
        fmriprep_confounds_dat{1, wh_replace} = zeros(1, sum(wh_replace)); % make array of zeros of the right size
    end


    % 1a. Handle spikes.
    switch noiseopts.spike_def
        case 'fmriprep'
            % dvars_idx=find(strcmpi(noise_dat.Properties.VariableNames,'dvars'));
            % % fd_idx=find(strcmpi(noise_dat.Properties.VariableNames,'framewise_displacement'));
            % rmsd_idx=find(strcmpi(noise_dat.Properties.VariableNames,'rmsd'));
            % % R_nuisance = [R_nuisance, dvars_idx, fd_idx, rmsd_idx, mout_idx];
            % % R_hdr=[R_hdr, noise_hdr([dvars_idx, fd_idx, rmsd_idx, mout_idx])];
            % R_nuisance = [R_nuisance, dvars_idx, rmsd_idx];
            % R_hdr=[R_hdr, noise_hdr([dvars_idx, rmsd_idx])];

            % define regressors in fMRIprep output
            spike_cols = contains(noise_hdr,'motion_outlier');
            Rspikes=fmriprep_confounds_dat(:,spike_cols);
            Rspikeopts.spikes=sum(Rspikes{:,1:end},2);
            volume_idx = [1:height(fmriprep_confounds_dat)]; 
            spikes = volume_idx(Rspikeopts.spikes==1);

            % flag user-specified number of volumes after each spike
            % Motion can create artifacts lasting longer than the single image we
            % usually account for using spike id scripts. we're also going to flag the
            % following TRs, the number of which is defined by the user. If
            % 'spikeopts.spike_additional_vols' remains unspecified, everything will proceed as
            % it did before, meaning spikes will be identified and flagged in the
            % creation of nuisance regressors without considering the following TRs
            % Add them if user requested, for both nuisance_covs and dvars_spikes_regs
            if noiseopts.spike_additional_vols ~= 0
                additional_spikes_regs = zeros(height(fmriprep_confounds_dat),size(spikes,2)*noiseopts.spike_additional_vols);
                % This loop will create a separate column with ones in each row (TR) 
                % we would like to consider a nuisance regressor
                for spike = 1:size(spikes,2) 
                    additional_spikes_regs(spikes(spike)+1 : spikes(spike)+noiseopts.spike_additional_vols,(spike*noiseopts.spike_additional_vols-(noiseopts.spike_additional_vols-1)):(spike*noiseopts.spike_additional_vols)) = eye(noiseopts.spike_additional_vols);
                end
                clear spike

                % if any spikes went beyond the end, trim it down
                additional_spikes_regs = additional_spikes_regs(1:height(fmriprep_confounds_dat),:);
                % add the additional spikes to the larger matrix
                fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(additional_spikes_regs)];
            end

            if noiseopts.spike_additional_vols ~= 0
                % if any spikes went beyond the end, trim it down
                additional_spikes_regs = additional_spikes_regs(1:height(fmriprep_confounds_dat),:);
                % add the additional spikes to the larger matrix
                fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(additional_spikes_regs)];
            end

            % remove redundant spike regressors
            spike_cols = contains(noise_hdr,'motion_outlier');
            additional_spike_cols = contains(noise_hdr,'additional_spikes'); 
            [duplicate_rows, ~] = find(sum(fmriprep_confounds_dat{:, spike_cols | additional_spike_cols}, 2)>1);
            for row = 1:length(duplicate_rows) % This loop sets duplicate values to zero; drops them later (to keep indices the same during the loop)
                [~,curr_cols] = find(fmriprep_confounds_dat{duplicate_rows(row),:}==1);
                fmriprep_confounds_dat{duplicate_rows(row), curr_cols(2:end)} = 0;
            end
            clear row
            fmriprep_confounds_dat = fmriprep_confounds_dat(1:height(fmriprep_confounds_dat), any(table2array(fmriprep_confounds_dat)));

            % FMRIPREP DVARS
            % ==================================================
            % In accordance with LukasVO's code, here we are using DVARS
            % from fmriprep. Although Tor likes our own dvars extraction
            % from rmssd_movie(), this takes a little bit of time.
            % add in dvars spike regressors that are non-redundant with mahal spikes
            dvarsZ = [0; zscore(fmriprep_confounds_dat.dvars(2:end))]; % first element of dvars always = 0, drop it from zscoring and set it to Z=0
            dvars_spikes = find(dvarsZ > noiseopts.dvars_threshold);
            same = ismember(dvars_spikes,spike_indices);
            dvars_spikes(same) = []; % drop the redundant ones
            dvars_spikes_regs = zeros(height(fmriprep_confounds_dat),size(dvars_spikes,1));
            for dvar=1:size(dvars_spikes,1)
                dvars_spikes_regs(dvars_spikes(dvar),dvar) = 1;
            end
            fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(dvars_spikes_regs)];

        case 'CANlab'
            if isfield(noiseopts, 'canlabmethod')
                switch noiseopts.canlabmethod
                    case 'make_nuisance_covs_from_fmriprep_output'
                        % METHOD 1: Yoni's way
                        % This way has some advantages. It does not require loading the fmri data, only extracts from fmriprep. It computes FD following Power 2019, filtering out pseudomotion
                        % frequencies from HMPs as a modification of the spike
                        % regressor calculation for fastTRs. This bottom code needs to
                        % be modified for each study.
                        % =============================================
                        disp('Generating spike regressors with make_nuisance_covs_from_fmriprep_output() using a 0.2 (strict) framewise-displacement spike cutoff...')
                        funcTR = niftiinfo(func).PixelDimensions(4);
                        if funcTR < 2
                        %   % How you would use it normally:
                        %   [nuis_matrix, n_spike_regs, n_spike_regs_percent] = make_nuisance_covs_from_fmriprep_output(noise_fname, funcTR, .2, 0, 'gs', 'wm', 'csf', 'aCompCor', 'tCompCor', 'fastTR');
                            [nuis_matrix, ~, ~] = make_nuisance_covs_from_fmriprep_output(fmriprep_confounds_tsv, funcTR, .2, 0, 'fastTR');
                        else
                        %   [nuis_matrix, n_spike_regs, n_spike_regs_percent] = make_nuisance_covs_from_fmriprep_output(noise_fname, funcTR, .2, 0, 'gs', 'wm', 'csf', 'aCompCor', 'tCompCor');
                            [nuis_matrix, ~, ~] = make_nuisance_covs_from_fmriprep_output(fmriprep_confounds_tsv, funcTR, .2, 0);
                        end
                        % disp(['This run has exhibited ' num2str(n_spike_regs) ' spikes, which is ' num2str(n_spike_regs_percent) '% of the scan.'])
                        % R = nuis_matrix
                        % return R;
                        spike_regs=nuis_matrix(:,25:end);
                    case 'mahal'
                        func_img=fmri_data(func);
                        % METHOD 1: Michael and Ke's way
                        % ===============================
                        % add in canlab spike detection (Mahalanobis distance)
                        disp('Generating spike regressors with mahal() using an uncorrected threshold...')
                        spike_regs=[];
                        [D2, D2_expected, pval, wh_outlier_uncorr, wh_outlier_corr] = mahal(func_img, 'noplot');
                        outlier_index=find(wh_outlier_uncorr==1);     % You can toggle between the two: corrected or uncorrected outliers.
                        % outlier_index=find(wh_outlier_corr==1);
                        if length(outlier_index)>0
                           for covi=1:length(outlier_index)
                              A=zeros(1,size(func_img.dat,2));
                              A(outlier_index(covi))=1;   %%%%% Outlier regressor e.g [0 0 0 0 0 0 1 0 0 0 0 0 ....]
                              spike_regs=[R_spikes A'];
                           end
                        end
                    case 'preprocess'
                        func_img=fmri_data(func);
                        disp('Generating spike regressors with CANlab preprocess()...')
                        % METHOD 2: WANI SUGGESTED 
                        % =========================
                        func_img.images_per_session=size(func_img.dat, 2)
                        dat = preprocess(func_img, 'outliers', 'plot');  % Spike detect and globals by slice
                        dat = preprocess(dat, 'outliers_rmssd', 'plot');  % RMSSD Spike detect
                        spike_regs = dat.covariates;
                    
                    case 'scn_session_spike_id'
                        func_img=fmri_data(func);
                        disp('Generating spike regressors with CANlab scn_session_spike_id()...')
                        % METHOD 3: Traditional/Marianne Hackpad/LukasVO LabGAS CANLab Implementation
                        % ============================================================================
                        [~, mahal_spikes, ~, spike_regs, ~] = scn_session_spike_id(func, 'doplot', 0); % CANlab function needs to be on your Matlab path
                        delete(fullfile(fileparts(func),'implicit*.img')); % delete implicit mask .hdr/.img files generated by the CANlab function on the line above, since we don't need/use them
                        delete(fullfile(fileparts(func),'*.hdr'));
                        delete(fullfile(fileparts(func),'qc_results.yaml'));
                        delete(erase(fullfile(fileparts(func), '.gz'))); % delete unzipped image since we don't need it anymore and it eats up space
                        spike_regs(:,1) = []; %drop gtrim which is the global signal
                    
                    case 'default'
                        disp('Generating spike regressors with default method CANlab outliers() with an uncorrected threshold...');
                    otherwise
                        disp('Unrecognized CANlab spike method. Generating spike regressors with default method CANlab outliers() with an uncorrected threshold...');
                end
            end

            if ~exist('spike_regs', 'var')
                % METHOD 5: Tor's latest 11/17/2023 Suggestion
                % ===============================================
                func_img=fmri_data(func);
                disp('Extracting spike regressors with CANlab outliers()...');
                [spikes_uncorr, spikes_corr, ~] = outliers(func_img, 'noplot'); % You can choose between the two: corrected or uncorrected outliers.
                % Expand them out into separate 1/0 spike column regressors.
                spike_regs=spikes_uncorr;
                % Initialize the matrix
                % Find indices of spikes
                spike_indices = find(spike_regs);
                spike_regs = zeros(length(spike_regs), length(spike_indices));
                % Populate the matrix
                for i = 1:length(spike_indices)
                    spike_regs(spike_indices(i), i) = 1;
                end
            end

            % Whichever method you choose above, add the columns to
            % fmriprep_confounds_dat
            fmriprep_confounds_dat(:,contains(fmriprep_confounds_dat.Properties.VariableNames,'motion_outlier'))=[]; % drop fmriprep motion outliers since we do not use them when noiseopts.spike_def = CANlab, and they cause redundancies
            fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(spike_regs)];


            % CANLAB DVARS
            % ==================================================
            disp('Extracting DVARS');
            [filedir, filename, ~]=fileparts(func);
            rmssd_file=fullfile(fileparts(func), [filename '_rmssd-movie.tiff']);
            if isfile(rmssd_file)
                [~, dvars_spikes_regs] = rmssd_movie(func_img, 'nomovie');
            else
                disp('Generated RMSSD Movie...');
                [~, dvars_spikes_regs] = rmssd_movie(func_img, 'writetofile', 'movieoutfile', rmssd_file);
            end
            dvars_spikes=find(sum(dvars_spikes_regs,2));
            fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(dvars_spikes_regs)];

    end

    % flag user-specified number of volumes after each spike
    % Motion can create artifacts lasting longer than the single image we
    % usually account for using spike id scripts. we're also going to flag the
    % following TRs, the number of which is defined by the user. If
    % 'spikeopts.spike_additional_vols' remains unspecified, everything will proceed as
    % it did before, meaning spikes will be identified and flagged in the
    % creation of nuisance regressors without considering the following TRs
    % Add them if user requested, for both nuisance_covs and dvars_spikes_regs
    if noiseopts.spike_additional_vols ~= 0
        % concatenate generated spike and DVARS regs. We
        % would like to flag subsequent TR's with respect to both of these
        % measures.
        spikes = [spike_indices;dvars_spikes];
        additional_spikes_regs = zeros(size(spike_indices,1),size(spikes,1)*noiseopts.spike_additional_vols);
        % This loop will create a separate column with ones in each row (TR) 
        % we would like to consider a nuisance regressor
        % Performs this function for spikes and DVARS. 
        for spike = 1:size(spikes,1) 
            additional_spikes_regs(spikes(spike) + 1:spikes(spike) + noiseopts.spike_additional_vols,(spike*noiseopts.spike_additional_vols-(noiseopts.spike_additional_vols-1)):(spike*noiseopts.spike_additional_vols)) = eye(noiseopts.spike_additional_vols);
        end
        clear spike
        % if any spikes went beyond the end, trim it down
        additional_spikes_regs = additional_spikes_regs(1:height(fmriprep_confounds_dat),:);
        % add the additional spikes to the larger matrix
        fmriprep_confounds_dat = [fmriprep_confounds_dat array2table(additional_spikes_regs)];
    end

    % remove redundant spike regressors
    noise_hdr = fmriprep_confounds_dat.Properties.VariableNames;
    spike_cols = contains(noise_hdr,'spike_regs'); 
    dvars_cols = contains(noise_hdr,'dvars_spikes'); 
    additional_spike_cols = contains(noise_hdr,'additional_spikes'); 

    [duplicate_rows, ~] = find(sum(fmriprep_confounds_dat{:, spike_cols | dvars_cols | additional_spike_cols}, 2)>1);
    % set duplicate values to zero; drops them later (to keep indices the same during the loop)
    for row = 1:size(duplicate_rows,1) 
        [~,curr_cols] = find(fmriprep_confounds_dat{duplicate_rows(row),:}==1);
        fmriprep_confounds_dat{duplicate_rows(row), curr_cols(2:end)} = 0;
    end
    clear row
    fmriprep_confounds_dat = fmriprep_confounds_dat(1:size(spike_regs,1), any(table2array(fmriprep_confounds_dat)));            

    noise_hdr = fmriprep_confounds_dat.Properties.VariableNames;
    spike_cols = contains(noise_hdr,'spike_regs') | contains(noise_hdr,'motion_outlier'); 
    dvars_cols = contains(noise_hdr,'dvars_spikes'); 
    additional_spike_cols = contains(noise_hdr,'additional_spikes');
    
    Rspikes = fmriprep_confounds_dat(:,spike_cols | dvars_cols | additional_spike_cols);

    % get row indices for spikes for later use
    Rspikeopts.spikes=sum(Rspikes{:,1:end},2);
    volume_idx = [1:height(fmriprep_confounds_dat)]; 
    spikes = volume_idx(Rspikeopts.spikes==1)';

    % compute and output how many spikes total
    n_spike_regs = sum(dvars_cols | spike_cols | additional_spike_cols);
    n_spike_regs_percent = n_spike_regs*100 / height(fmriprep_confounds_dat);

    % print warning if #volumes identified as spikes exceeds
    % user-defined threshold
    disp(['This run has exhibited ' num2str(n_spike_regs) ' spikes, which is ' num2str(100*n_spike_regs/height(fmriprep_confounds_dat)) '% of the scan.']);
    if n_spike_regs_percent > noiseopts.spikes_percent_threshold
        warning('\n%d volumes identified as spikes exceeds the %d percent threshold in %s', n_spike_regs, noiseopts.spikes_percent_threshold, func)
    end

   % Select the confounds and spike regressors to return for use in GLM 
   R = [R, Rspikes];

    noise_hdr = fmriprep_confounds_dat.Properties.VariableNames;
    
    % 1b. Handle Motion Regressors
    if isfield(noiseopts, 'movement_regs')
        motion_cols_6 = (contains(noise_hdr,'rot') | contains(noise_hdr,'trans')) & ~contains(noise_hdr,'derivative1') & ~contains(noise_hdr,'power2');
        motion_cols_12 = (contains(noise_hdr,'rot') | contains(noise_hdr,'trans')) & ~contains(noise_hdr,'power2');
        motion_cols_24 = contains(noise_hdr,'rot') | contains(noise_hdr,'trans');
        
        switch noiseopts.movement_regs
            case {6, '6'}
                Rmotion = fmriprep_confounds_dat(:,motion_cols_6);
            case {12, '12'}
                Rmotion = fmriprep_confounds_dat(:,motion_cols_12);
            case {24, '24'}
                Rmotion = fmriprep_confounds_dat(:,motion_cols_24);
            otherwise
                error('Unsupported number of movement regressors set.');
        end

        % If including more than 6 movement regressors, recalculate derivatives, z-score, and recalculate quadratics to orthogonalize
        regsmotion = Rmotion.Properties.VariableNames;
        if numel(regsmotion)>6
            regsnot2keep = contains(regsmotion,'derivative') | contains(regsmotion,'power');
            regsderiv = regsmotion(~contains(regsmotion,'power'));
            regsderiv = regsderiv(contains(regsderiv,'derivative'));
            Rmotion = Rmotion(:,~regsnot2keep);
            deriv = @(x) gradient(x);
    
            Rmotionderiv = varfun(deriv,Rmotion);
            for regderiv = 1:size(Rmotionderiv.Properties.VariableNames,2)
                Rmotionderiv.Properties.VariableNames{regderiv} = regsderiv{regderiv};
            end
            Rmotionderiv = [Rmotion,Rmotionderiv];
            regsmotion2 = Rmotionderiv.Properties.VariableNames;
            % zscore = @(x) zscore(x);
            Rmotionzscore = varfun(deriv,Rmotionderiv);
    
            for regz = 1:size(Rmotionzscore.Properties.VariableNames,2)
                Rmotionzscore.Properties.VariableNames{regz} = regsmotion2{regz};
            end
        
            if numel(regsmotion)==24
                quad = @(x) x.^ 2;
                Rmotionquad = varfun(quad,Rmotionzscore);
                Rmotionfinal = [Rmotionzscore,Rmotionquad];
            else Rmotionfinal = Rmotionzscore;
            end
        end

        % FD-based spikes. Not yet implemented. 
        % First, compute FD following Power 2019
        % First-order Rotation parameters
        % first_order_rotation=find(contains(regsmotion, 'rot') & ~(contains(regsmotion, 'derivative') | contains(regsmotion, 'power')));
        % Rmotion(:, first_order_rotation) = (Rmotion{:, first_order_rotation} / (2*pi)) * 100 * pi; % fraction of circle (radians / 2pi) * diameter (pi*d).   convert rotation to mm. assume head is 50mm sphere (Power et al 2012)
        % 
        % if fast_TR % filter and compare to ~2sec prev rather than framewise
        %     fd = filtFD(motion, TR);
        % else    
        %     fd = sum(abs(diff(motion)),2);
        %     fd = [0; fd];
        % end
        % 
        % % define spikes based off FD
        % FD_spikes = fd > noiseopts.FD_spike_cutoff;

    end
    R = [R, Rmotionfinal];

    % Just as above, the rest of the regressors will also be z-scored to
    % keep all signals e.g., linear trend on similar scales.

    % 1c. Handle CSF
    if isfield(noiseopts, 'csf')
        if noiseopts.csf
            Rcsf = table(zscore(fmriprep_confounds_dat.csf),'VariableNames',{'csf'});
            R = [R, Rcsf];
        end
    end

    % 1d. Handle WM
    if isfield(noiseopts, 'wm')
        if noiseopts.wm
            Rwm = table(zscore(fmriprep_confounds_dat.white_matter),'VariableNames',{'white_matter'});
            R = [R, Rwm];
        end
    end

    % 1e. Handle Anatomical Component Correction (aCompCor)
    if isfield(noiseopts, 'acompcor')
        acompcor_idx = find(contains(noise_hdr, 'a_comp_cor'));
        acompcor_idx = acompcor_idx(1:min(noiseopts.acompcor, length(acompcor_idx)));
        Racompcor = zscore(fmriprep_confounds_dat{:,acompcor_idx});
        Racompcor = array2table(Racompcor, 'VariableNames', fmriprep_confounds_dat.Properties.VariableNames(acompcor_idx));
        R = [R, Racompcor];
    end

    % 1f. Handle Temporal Component Correction (tCompCor)
    if isfield(noiseopts, 'tcompcor')
        tcompcor_idx = find(contains(noise_hdr, 't_comp_cor'));
        tcompcor_idx = tcompcor_idx(1:min(noiseopts.tcompcor, length(tcompcor_idx)));
        Rtcompcor = zscore(fmriprep_confounds_dat{:,tcompcor_idx});
        Rtcompcor = array2table(Rtcompcor, 'VariableNames', fmriprep_confounds_dat.Properties.VariableNames(tcompcor_idx));
        R = [R, Rtcompcor];
    end

    % 1g. Handle global signal
    if isfield(noiseopts, 'global')
        if noiseopts.global
            Rglobal = table(zscore(fmriprep_confounds_dat.global_signal),'VariableNames',{'global_signall'});
            R = [R, Rglobal];
        end
    end

    % save confound regressors as matrix named R for use in
    % SPM/CANlab GLM model tools
    R_hdr=R.Properties.VariableNames;
    R=table2array(R);

end

function table=importBIDSfile(file)
    opts = detectImportOptions(file, 'FileType', 'delimitedtext', 'Delimiter', '\t');
    
    if sum(ismember(opts.VariableNames, 'trial_type')) > 0  % Check if 'trial_type" variable column exists.
        opts = setvartype(opts, 'trial_type', 'char');
    end

    table = readtable(file, opts);
end