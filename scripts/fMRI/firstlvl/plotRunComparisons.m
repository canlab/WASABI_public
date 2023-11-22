function plotRunComparisons(firstlvl_derivdir, subs)
    for sub = 1:numel(subs)
        sessions=canlab_list_subjects(fullfile(firstlvl_derivdir, subs{sub}), 'ses-*');
   
        for ses=1:numel(sessions)
            disp(['Processing images for ', subs{sub}, ' ', sessions{ses}]);

            % For each subject: All funcs in the session:
            % ses_funcs = filenames(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, '**', ['*' space, '*desc-preproc_bold.nii.gz']));
            ses_funcs = dir(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, '**', ['*' space, '*desc-preproc_bold.nii.gz']));
            % ses_funcs = fullfile({ses_funcs(:).folder}', {ses_funcs(:).name}');
            
            % Plot Session-Montage Comparison
            % For sessions involving multiple runs, Use plot montage to compare the runs for any potential troubleshooting
            if(size(ses_funcs, 1) > 1 && ~exist([subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig'], 'file'))
%                     % ses_objs=create_fmridat_fromdir(ses_funcs); % This command takes a long time remotely. Best to run this directly on the cluster.
%                     try
%                         ses_objs=fmri_data(ses_funcs);
%                     catch
%                         error(['Unable to generate fmri_data objects from ' ses_funcs '. Perhaps they are symlinks generated from a different operating system.'])
%                     end
                % Hopefully this is now implemented into fmri_data/plot()
                ses_objs=create_fmridat_fromdir(ses_funcs);
                
                if size(ses_objs.image_names, 1) > 1
                    ses_objs=id_images_per_session(ses_objs);
                    plot(ses_objs, 'montages', 'noorthviews', 'nooutliers')
                    fig = gcf;
                    exportgraphics(fig, fullfile(firstlvl_derivdir, subs{sub}, sessions{ses},[subs{sub}, '_', sessions{ses}, '_run-comparison-plot.png']));
                    savefig(fullfile(firstlvl_derivdir, subs{sub}, sessions{ses}, [subs{sub}, '_', sessions{ses}, '_run-comparison-plot.fig']));
                end
            end
            close all
        end

    end