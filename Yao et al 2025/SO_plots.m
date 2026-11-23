clear; clc; 

load('paper-data/data_so_mld_nml.mat');

min_lon=min(LON);
max_lon=max(LON);
min_lat=min(LAT);
max_lat=-50;

lat_training=LAT(LOC(:,2));
lon_training=LON(LOC(:,1));

figure(1);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
title('Locations of points used for training PCM over contours of bottom depth (m)','FontSize',30);
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
m_contour(LON,LAT,Bottom_Depth','linewidth',1);
c = colorbar;
c.FontSize = 24;
%m_coast('patch',[.7 1 .7],'edgecolor','k'); 
m_plot(lon_training,lat_training,'ro','markersize',2,'MarkerFaceColor','r');
hold off

figure(2);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
caxis([-0.0001 0.0001]);
colormap(parula);
m_image(LON,LAT,Vorticity');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
%m_coast('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
title('Surface Vertical Vorticity (s^{-1}) of SO Dataset','fontsize',30);
c=colorbar;
c.FontSize=24;
hold off

surf_spd=sqrt(U.^2+V.^2);
figure(3);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
caxis([min(min(surf_spd)) max(max(surf_spd))]);
colormap(turbo);
m_image(LON,LAT,surf_spd');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
title('Surface Speed (m/s) of SO Dataset','fontsize',30);
c = colorbar;
c.FontSize = 24;
hold off

B=ones(101,101)/101^2; 
vor_avg=conv2(Vorticity,B,'same');
vor_abs_avg=conv2(abs(Vorticity),B,'same');
vor_new=vor_abs_avg-abs(vor_avg);
figure(4);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
caxis([min(min(vor_new)) max(max(vor_new))]);
colormap(turbo);
m_image(LON,LAT,vor_new');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
title('$\hat{\zeta}$ $(s^{-1})$','interpreter', 'latex','fontsize',30);
c = colorbar;
c.FontSize = 24;
hold off

figure(6);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
caxis([min(min(Bottom_Depth)) max(max(Bottom_Depth))]);
colormap(parula);
m_image(LON,LAT,Bottom_Depth');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
m_plot(lon_training,lat_training,'mo','markersize',2.5,'MarkerFaceColor','m');
title('Locations of Training Data over Bottom Depth (m) of SO Dataset','fontsize',30);
c = colorbar;
c.FontSize = 24;
hold off

figure(7);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
%caxis([0 1]);
colormap(parula(2));
m_scatter(lon_training,lat_training,[],CLASS,'filled');
title('PCM Predictions (Blue = Submesoscale Inactive, Yellow = Submesoscale Active)','fontsize',30);
%c = colorbar;
%c.FontSize = 20;
hold off


figure(8);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
caxis([min(MLD) max(MLD)]);
colormap(parula);
m_scatter(lon_training,lat_training,[],MLD,'filled');
title('Mixed Layer Depth (m)','fontsize',30);
c = colorbar;
c.FontSize = 24;
hold off


figure(9);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
%caxis([0 1]);
colormap(parula);
m_scatter(lon_training,lat_training,[],PCM_POST(2,:),'filled');
title('Probability of being classified as Eddy','fontsize',30);
c = colorbar;
c.FontSize = 24;
hold off

figure(10);
scatter(PCM_POST(2,:),Vorticity(LOC(:,1)+1,LOC(:,2)+1));

figure(11);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
%title('Locations of points used for training PCM over contours of bottom depth (m)','FontSize',30);
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
m_scatter(lon_training,lat_training,[],CLASS,'filled');
m_contour(LON,LAT,vor_new','linewidth',1);
c = colorbar;
c.FontSize = 24;
%m_coast('patch',[.7 1 .7],'edgecolor','k'); 
hold off


figure(12);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
%title('Locations of points used for training PCM over contours of bottom depth (m)','FontSize',30);
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
m_scatter(lon_training,lat_training,[],MLD,'filled');
m_contour(LON,LAT,vor_new','linewidth',1);
%c = colorbar;
%c.FontSize = 24;
%m_coast('patch',[.7 1 .7],'edgecolor','k'); 
hold off

CLASS_MLD=MLD(:,:);
CLASS_MLD(MLD>-45)=2;
CLASS_MLD(MLD<=-45)=1;
figure(13);
m_proj('lambert','long',[min_lon max_lon],'lat',[min_lat max_lat]);
hold on
set(gca,'fontname','times')
set(gcf,'color','w');
m_gshhs_i('patch',[1 .85 .7],'edgecolor','k','linewidth',1);
m_grid('box','fancy','tickdir','in','fontsize',24);
%caxis([0 1]);
colormap(parula(2));
m_scatter(lon_training,lat_training,[],CLASS_MLD,'filled');
title('MLD Predictions (Blue = Submesoscale Inactive, Yellow = Submesoscale Active)','fontsize',30);
%c = colorbar;
%c.FontSize = 20;
hold off

