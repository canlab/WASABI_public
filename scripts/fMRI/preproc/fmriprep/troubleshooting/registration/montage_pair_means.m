function montage_pair_means(dat1, dat2)

% use_generic_labels = false;
% Figure out how to identify if these are runs before deciding what to do
% with use_generic_labels


% if isempty(dat.images_per_session)
%     % They may not really be runs...use generic labels
%     use_generic_labels = true;
% 
%     % 
% 
%     % Replace this label with a way of automatically 
%     if isempty(dat.image_names)
%         dat.images_per_session = size(dat.dat, 2);
%     else
%         for k=1:size(dat.image_names, 1)
%             dat.images_per_session = [dat.images_per_session sum(contains(cellstr(dat.fullpath),strtrim(dat.image_names(k,:))))];
%             disp(['Run ', num2str(k), ': ', dat.image_names(k,:), ' has ', num2str(sum(contains(cellstr(dat.fullpath),strtrim(dat.image_names(k,:))))), ' images.']);
%         end
%     end
% 
% 
% end


% create_figure('Slice_montage', 3, 1);
% figure;


% Set figure position
% set_figure_position(2 / 1, 6)

% Create run means
% ----------------------------------------------------------------------
m = cell(1, 2);
m{1} = mean(dat1);
m{2} = mean(dat2);

% Set color limits for all runs together
% ----------------------------------------------------------------------
% colormap('default'); % Ensure a default colormap

mm = cat(m{:});
alldat = mm.dat(:);

% clim = [mean(alldat) - 3*std(alldat) mean(alldat) + 3*std(alldat)];
% have to omitnan
clim = [mean(alldat, 'omitnan') - 3*std(alldat, 'omitnan') mean(alldat, 'omitnan') + 3*std(alldat, 'omitnan')];

% subplot(3, 1, 1);

nexttile

han = display_slices(m{1}, 'axial', 'slices_per_row', 10, 'spacing', 8, 'startslice', -30, 'endslice', 40, 'clim', clim);
if isempty(dat1.image_names)
    title(sprintf('Image 1'))
else
    t{1}=format_strings_for_legend(dat1.image_names(1,:));
    title(t{1});
end

% subplot(3, 1, 2);

nexttile

han = display_slices(m{2}, 'axial', 'slices_per_row', 10, 'spacing', 8, 'startslice', -30, 'endslice', 40, 'clim', clim);
if isempty(dat1.image_names)
    title(sprintf('Image 2'))
else
    t{2}=format_strings_for_legend(dat2.image_names(1,:));
    title(t{2});
end

drawnow

data=cat(m{:});

% subplot(3,1,3);
nexttile;

% [m1, m2]=padwithnan(m{1}.dat, m{2}.dat, 2)
% [m1, m2]=padwithnan(m{1}.dat, m{2}.dat, 1);

%plot(m1, m2, 'k.'); refline
% figure; corr(m{1}.dat, m{2}.dat, 'k.', 'Rows', 'pairwise'); refline
% corr(m1, m2)
plot(get_wh_image(data, 1).dat, get_wh_image(data, 2).dat, 'k.'); refline

title(sprintf('r = %3.2f',  corr(get_wh_image(data, 1).dat, get_wh_image(data, 2).dat, 'Rows', 'pairwise')))
xlabel(t{1})
ylabel(t{2})
% drawnow



end % montage_pair_means