function DSGN = generate_contrasts(task, DSGN)
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

    DSGN.contrasts = {};
    DSGN.contrastweights = {};
    DSGN.contrastnames = {};
    DSGN.regmatching = 'regexp'; % regular experession mode to match keywords you provide in cell arrays below with beta regressor names stored in the SPM.Vbeta.descrip field of your first level SPM.mat file
    % DSGN.defaultsuffix = '\*bf\(1\)$'; % adds this suffix to each keyword, which is SPM parlance for 'convolved with basis function 1'.
    % DSGN.noscale = true; % default: false; if true, turn off scaling of contrasts to sum up to zero or one, not recommended if you have unequal amounts of run between subjects, unless you concatenate
    
    
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

    
    % CONTRASTS
    
    % OPTIONAL FIELDS
    
    % flexible definition of contrasts - for more info
    % - help canlab_spm_contrast_job_luka
    % - https://github.com/canlab/CanlabCore/blob/master/CanlabCore/GLM_Batch_tools/canlab_glm_example_DSGN_setup.txt
    


    % Example: {{contrast}, 'contrastname', [contrast_matrix]}

%     task_contrasts.lukasStudy={
%             % Unmodulated Contrasts
%             {{'.*sucrose{1}\s[^x]'}, 'sucrose unmodulated', [1]}
%             {{'.*erythritol{1}\s[^x]'}, 'erythritol unmodulated', [1]}
%             {{'.*sucralose{1}\s[^x]'}, 'sucralose unmodulated', [1]}
%             {{'.*water{1}\s[^x]'}, 'water unmodulated', [1]}
%             {{{'.*sucrose{1}\s[^x]'} {'.*water{1}\s[^x]'}}, 'sucrose unmodulated vs water unmodulated', [1 -1]}
%             {{{'.*erythritol{1}\s[^x]'} {'.*water{1}\s[^x]'}}, 'erythritol unmodulated vs water unmodulated', [1 -1]}
%             {{{'.*sucralose{1}\s[^x]'} {'.*water{1}\s[^x]'}}, 'sucralose unmodulated vs water unmodulated', [1 -1]}
%             {{{'.*sucrose{1}\s[^x]'} {'.*sucralose{1}\s[^x]'}}, 'sucrose unmodulated vs sucralose unmodulated', [1 -1]}
%             {{{'.*sucrose{1}\s[^x]'} {'.*erythritol{1}\s[^x]'}}, 'sucrose unmodulated vs erythritol unmodulated', [1 -1]}
%             {{{'.*erythritol{1}\s[^x]'} {'.*sucralose{1}\s[^x]'}}, 'erythritol unmodulated vs sucralose unmodulated', [1 -1]}
%             % Modulated Contrasts
%             {{'.*liking_sucrose'}, 'sucrose modulated', [1]}
%             {{'.*liking_erythritol'}, 'erythritol modulated', [1]}
%             {{'.*liking_sucralose'}, 'sucralose modulated', [1]}
%             {{'.*liking_water'}, 'water modulated', [1]}
%             {{{'.*liking_sucrose'} {'.*liking_water'}}, 'sucrose modulated vs water modulated', [1 -1]}
%             {{{'.*liking_erythritol'} {'.*liking_water'}}, 'erythritol modulated vs water modulated', [1 -1]}
%             {{{'.*liking_sucralose'} {'.*liking_water'}}, 'sucralose modulated vs water modulated', [1 -1]}
%             {{{'.*liking_sucrose'} {'.*liking_sucralose'}}, 'sucrose modulated vs sucralose modulated', [1 -1]}
%             {{{'.*liking_sucrose'} {'.*liking_erythritol'}}, 'sucrose modulated vs erythritol modulated', [1 -1]}
%             {{{'.*liking_erythritol'} {'.*liking_sucralose'}}, 'erythritol modulated vs sucralose modulated', [1 -1]}
%         }


    switch task
        case 'bodymap'
            task_contrasts.bodymap={ 
                {{'.*hot'}, 'Hot', [1]} 
                {{'.*warm'}, 'Warm', [1]} 
                {{'.*imagine'}, 'Imagine', [1]}
                {{'.*imagcue'}, 'Imagine-Cue', [1]}
                {{'.*hot' '.*warm' '.*imagine'}, 'Sensation', [1 1 0]}
                {{'.*hot' '.*warm' '.*imagine'}, 'Aversion', [1 0 1]}
                {{{'.*hot'} {'.*warm'}}, 'HotvsWarm', [1 -1]}
                {{{'.*hot'} {'.*imagine'}}, 'HotvsImagine', [1 -1]}
                {{{'.*imagine'} {'.*warm'}}, 'ImaginevsWarm', [1 -1]}
                {{'.*hot' '.*warm' '.*imagine'}, 'HotU', [2 -1 -1]}
                {{'.*hot' '.*warm' '.*imagine'}, 'WarmU', [-1 2 -1]}
                {{'.*hot' '.*warm' '.*imagine'}, 'ImagineU', [-1 -1 2]}
                {{'.*hot' '.*warm' '.*imagine'}, 'SensationU', [1 1 -2]}
                {{'.*hot' '.*warm' '.*imagine'}, 'AversionU', [1 -2 1]}
            };
        case 'movemap'
            task_contrasts.movemap = { 
                {{'leftface.*'}, 'Leftface', [1]}
                {{'rightface.*'}, 'Rightface', [1]}
                {{'leftarm.*'}, 'Leftarm', [1]}
                {{'rightarm.*'}, 'Rightarm', [1]}
                {{'leftleg.*'}, 'Leftleg', [1]}
                {{'rightleg.*'}, 'Rightleg', [1]}
                {{'chest.*'}, 'Chest', [1]}
                {{'abdomen.*'} 'Abdomen', [1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'leftfaceU', [7 -1 -1 -1 -1 -1 -1 -1]}        
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'rightfaceU', [-1 7 -1 -1 -1 -1 -1 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'leftarmU', [-1 -1 7 -1 -1 -1 -1 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'rightarmU', [-1 -1 -1 7 -1 -1 -1 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'leftlegU', [-1 -1 -1 -1 7 -1 -1 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'rightlegU', [-1 -1 -1 -1 -1 7 -1 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'chestU', [-1 -1 -1 -1 -1 -1 7 -1]}
                {{'leftface.*' 'rightface'.* 'leftarm.*' 'rightarm.*' 'leftleg.*' 'rightleg.*' 'chest.*' 'abdomen.*'}, 'abdomenU', [-1 -1 -1 -1 -1 -1 -1 7]}
                {{{'left.*'} {'right.*'}}, 'L_v_R Move', [1 -1]}
            };
        case 'acceptmap'
            task_contrasts.acceptmap = { 
                {{'.*heat_start'}, 'avgHeat', [1]}
                {{{'(?<!leftface_)heat_start'} {'leftface_heat_start'}}, 'LFvO', [1, -1]}
            };
        case 'distractmap'
            task_contrasts.distractmap = { 
                {{'.*back.*'}, 'avg_'}}
                {{'.*_ttl_1'}, 'avgStim'}}
                {{'.*1back.*'}, 'avg1back'}
                {{'.*2back.*'}, 'avg2back'}
                {{['[Rr]est_[Ss]tim']}, ''}
            

                {{{'.*back_stim_ttl_1'}, {'.*nback_prestim'}}, 'nback_postvprestim', [1]}
                {{'.*nback_prestim'}, 'avg_nback_prestim', [1]}
                % {{'.*_nostim[Bb]lock'}, 'avg_nostimblock', [1]}
                
                {{'.*rightface'}, 'avgRightface', [1]} 
            };


                        % Older versions:
                    contrasts{1} = {{'oneback_noheat'}};      contrastnames{1} = 'avg_1back_noheat';
                    contrasts{2} = {{'twoback_noheat'}};     contrastnames{2} = 'avg_2back_noheat';
                    contrasts{3} = {{'oneback_heat'}};      contrastnames{3} = 'avg_1back_heat';
                    contrasts{4} = {{'twoback_heat'}};     contrastnames{4} = 'avg_2back_heat';
                    
                    contrasts{5} = {{'twoback_noheat'} {'oneback_noheat'}};  contrastnames{5} = '2v1back_noheat';
                    contrasts{6} = {{'twoback_heat'} {'oneback_heat'}};  contrastnames{6} = '2v1back_heat';
            
                    contrasts{7} = {{'twoback_heat'} {'twoback_noheat'}};  contrastnames{7} = '2back_heat_v_noheat';
                    contrasts{8} = {{'oneback_heat'} {'oneback_noheat'}};  contrastnames{8} = '1back_heat_v_noheat';
                    
            %         contrasts{} = {{'oneback_noheat_exp'}{'oneback_noheat_control'}}; contrastnames{}='1back_bodysites';
            %         contrasts{} = {{'twoback_noheat_exp'}{'twoback_noheat_control'}}; contrastnames{}='2back_bodysites';
            % 
            %         contrasts{} = {{'oneback_heat_exp'}{'oneback_noheat_exp'}}; contrastnames{}='1back_bodysites';
            %         contrasts{} = {{'twoback_heat_exp'}{'twoback_noheat_exp'}}; contrastnames{}='2back_bodysites';
            % 
            %         contrasts{} = {{'twoback_noheat_exp'}{'oneback_noheat_exp'}}; contrastnames{}='2v1_exp_nh';
            %         contrasts{} = {{'twoback_heat_exp'}{'oneback_heat_exp'}}; contrastnames{}='2v1_exp_h';
            %         contrasts{} = {{'twoback_noheat_control'}{'oneback_noheat_control'}}; contrastnames{}='2v1_control_nh';
            %         contrasts{} = {{'twoback_heat_control'}{'oneback_heat_control'}}; contrastnames{}='2v1_control_h';

            % v3.0.0
            %         contrasts{1} = {{'rest_noheat'}};      contrastnames{1} = 'avg_rest_noheat';
            %         contrasts{2} = {{'twoback_noheat'}};     contrastnames{2} = 'avg_2back_noheat';
            %         contrasts{3} = {{'rest_heat'}};      contrastnames{3} = 'avg_rest_heat';
            %         contrasts{4} = {{'twoback_heat'}};     contrastnames{4} = 'avg_2back_heat';
            %         
            %         contrasts{5} = {{'twoback_noheat'} {'rest_noheat'}};  contrastnames{5} = '2backvrest_noheat';
            %         contrasts{6} = {{'twoback_heat'} {'rest_heat'}};  contrastnames{6} = '2backvrest_heat';
            % 
            %         contrasts{7} = {{'twoback_heat'} {'twoback_noheat'}};  contrastnames{7} = '2back_heat_v_noheat';
            %         contrasts{8} = {{'rest_heat'} {'rest_noheat'}};  contrastnames{8} = 'rest_heat_v_noheat';

        case 'pinellocalizer'
            task_contrasts.pinellocalizer = { 
                {{'.*leftface'}, 'avgLeftface', [1]} 
                {{'.*rightface'}, 'avgRightface', [1]} 
            };

            contrasts{1} = {{'Check'}};                                                     contrastnames{1} = 'CheckAvg';
            contrasts{2} = {{'HCheck' 'VCheck' 'VRClick' 'VLClick' 'VLang' 'VComp'}};       contrastnames{2} = 'VisAvg';
            contrasts{3} = {{'ARClick' 'ALClick' 'ALang' 'AComp'}};                         contrastnames{3} = 'AudAvg';
            contrasts{4} = {{'RClick'}};                                                    contrastnames{4} = 'RBtnAvg';
            contrasts{5} = {{'LClick'}};                                                    contrastnames{5} = 'LBtnAvg';
            contrasts{6} = {{'Comp'}};                                                      contrastnames{6} = 'CompAvg';
            contrasts{7} = {{'Click'}};                                                     contrastnames{7} = 'MotorAvg';
            contrasts{8} = {{'Lang'}};                                                      contrastnames{8} = 'LangAvg';
            contrasts{9} = {{'HCheck'}};                                                    contrastnames{9} = 'HCheckAvg';
            contrasts{10} = {{'VCheck'}};                                                   contrastnames{10} = 'VCheckAvg';
            % Its quite risky to depend on the contrast shortcuts, so I will specify them deliberately
    %         conditions = {{'HCheck', 'VCheck','VRClick','VLClick','VLang','VComp','ARClick','ALClick','ALang','AComp'}};
            conditions = {{'HCheck'}, {'VCheck'},{'VRClick'},{'VLClick'},{'VLang'},{'VComp'},{'ARClick'},{'ALClick'},{'ALang'},{'AComp'}};
            [contrasts{11:36}]=deal(conditions)
            contrastweights{11} = [0 0 0 0 0 0 1 1 -2 0];                                         contrastnames{11} = 'AMo_v_ALa';
            contrastweights{12} = [0 0 0 0 0 0 -1 -1 2  0];                                       contrastnames{12} = 'ALa_v_AMo';
            contrastweights{13} = [0 0 0 0 0 0 0 0 -1 1];                                         contrastnames{13} = 'ACo_v_ALa';
            contrastweights{14} = [0 0 0 0 0 0 0 0 1 -1];                                         contrastnames{14} = 'ALa_v_ACo';
            contrastweights{15} = [0 0 1 1 -2 0 0 0 0 0];                                         contrastnames{15} = 'VMo_v_VLa';
            contrastweights{16} = [0 0 -1 -1 2 0 0 0 0 0];                                        contrastnames{16} = 'VLa_v_VMo';
            contrastweights{17} = [0 0 0 0 -1 1 0 0 0 0];                                         contrastnames{17} = 'VCo_v_VLa';
            contrastweights{18} = [0 0 0 0 1 -1 0 0 0 0];                                         contrastnames{18} = 'VLa_v_VCo';
            contrastweights{19} = [-1 -1 -1 -1 -1 0 1.25 1.25 1.25 1.25];                         contrastnames{19} = 'Aud_v_Vis';
            contrastweights{20} = [1 1 1 1 1 0 -1.25 -1.25 -1.25 -1.25];                          contrastnames{20} = 'Vis_v_Aud';
            contrastweights{21} = [0 0 1 -1 0 0 1 -1 0 0];                                        contrastnames{21} = 'RvLBtn';
            contrastweights{22} = [0 0 -1 1 0 0 -1 1 0 0];                                        contrastnames{22} = 'LvRBtn';
            contrastweights{23} = [0 0 -1 -1 0 2 -1 -1 0 2];                                      contrastnames{23} = 'Co_v_Mo';
            contrastweights{24} = [0 0 1 1 0 -2 1 1 0 -2];                                        contrastnames{24} = 'Mo_v_Co';
            contrastweights{25} = [0 0 0 0 -1 1 0 0 -1 1];                                        contrastnames{25} = 'Co_v_La';
            contrastweights{26} = [0 0 0 0 2 -1 0 0 0 -1];                                        contrastnames{26} = 'La_v_Co';
            contrastweights{27} = [0 0 1 1 -2 0 1 1 -2 0];                                        contrastnames{27} = 'Mo_v_La';
            contrastweights{28} = [0 0 -1 -1 2 0 -1 -1 2 0];                                      contrastnames{28} = 'La_v_Mo';              
            contrastweights{29} = [1 -1 0 0 0 0 0 0 0 0];                                         contrastnames{29} = 'HvVCheck';
            contrastweights{30} = [-1 1 0 0 0 0 0 0 0 0];                                         contrastnames{30} = 'VvHCheck';
            contrastweights{31} = [-1.5 -1.5 1 1 1 0 0 0 0 0];                                    contrastnames{31} = 'Vis_v_Check';
            contrastweights{32} = [1.5 1.5 -1 -1 -1 0 0 0 0 0];                                   contrastnames{32} = 'Check_v_Vis';
            contrastweights{33} = [1 1 0 0 -2 0 0 0 0 0];                                         contrastnames{33} = 'VLang_v_Check';
            contrastweights{34} = [-1 -1 0 0 2 0 0 0 0 0];                                        contrastnames{34} = 'Check_v_VLang';
            contrastweights{35} = [-1 -1 0 0 0 2 0 0 0 0];                                        contrastnames{35} = 'VCo_v_Check';
            contrastweights{36} = [1 1 0 0 0 -2 0 0 0 0];                                         contrastnames{36} = 'Check_v_VCo';

    end



    if isempty(fieldnames(task_contrasts))
        error('No tasks defined, please define your tasks first to generate contrasts.');
    end


    % Check if the task is defined in the contrast information
    if isfield(task_contrasts, task)
        task_data = task_contrasts.(task);
        num_contrasts = size(task_data, 1);
        
        for i = 1:num_contrasts
            contrast_info = task_data{i};
            DSGN.contrasts{end+1} = contrast_info(1);
            DSGN.contrastnames{end+1} = contrast_info{2};
            if isempty(contrast_info{3})
                DSGN.contrastweights{end+1} = ones(1, length(contrast_info{1}));
            else
                DSGN.contrastweights{end+1} = contrast_info{3};
            end
        end
    else
        warning('Task not recognized: %s', task);
    end
end
