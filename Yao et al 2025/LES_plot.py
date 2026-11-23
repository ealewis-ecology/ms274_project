# Generates plots for paper on LES dataset

# import libraries
import numpy as np
import pandas as pd
import xarray as xr
import pyxpcm
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import colors
from scipy import ndimage

mpl.rc('font',family='Times New Roman')
np.random.seed(256)
tnrfont = {'fontname':'Times New Roman'}

# Load data and discard artificial surface value
th1_sam = np.load('paper-data/data_les_buo_sample.npy')
vel_x = np.load('paper-data/data_les_velx_surf.npy')
vel_z = np.load('paper-data/data_les_vely_surf.npy')
depth = np.load('paper-data/data_les_depth.npy')
x_sam = np.load('paper-data/data_les_x_sample.npy')
z_sam = np.load('paper-data/data_les_y_sample.npy')

# Pre-process data: rescale according to MLD + normalize according to vertical mean buoyancy
N = 10000
th1_del = 0.0003924
num = 100

coord_new = np.linspace(-1,0,num=num)
th1_mld = np.zeros((N,num))
mld_sam = np.zeros(N)
for i in range(N):
    prof = th1_sam[i,:]
    surf_val = prof[-1]
    ind = np.where(surf_val-prof<=th1_del)
    prof = prof[ind]
    prof_len = len(prof)
    mld_sam[i] = prof_len*(800/256)
    coord_old = np.linspace(-1,0,num=prof_len)
    prof = np.interp(coord_new, coord_old, prof)
    th1_mld[i,:] = prof

th1_mld_nml = np.zeros((N,num))
th1_mean_sam = np.zeros(N)
for j in range(N):
    prof = th1_mld[j,:]
    avg = np.mean(prof)
    th1_mean_sam[j] = avg
    prof = prof - avg
    th1_mld_nml[j,:] = prof

# Calculate surface smoothed vorticity and surface speed

vel_x_surf = vel_x[:,-1,:]
vel_z_surf = vel_z[:,-1,:]
n = 1024
h = 4000/(n-1)
knl = np.ones((100,100))/100/100
vel_x_smt = ndimage.convolve(vel_x_surf, knl, mode='wrap')
vel_z_smt = ndimage.convolve(vel_z_surf, knl, mode='wrap')
i_p = np.append(np.arange(1,n), 0)
i_m = np.append(n-1, np.arange(n-1))
vel_x_p = vel_x_smt[i_p,:]
vel_x_m = vel_x_smt[i_m,:]
vel_z_p = vel_z_smt[:,i_p]
vel_z_m = vel_z_smt[:,i_m]
vor = (-1/2/h)*(vel_x_p - vel_x_m - vel_z_p + vel_z_m)
spd = np.sqrt(np.square(vel_x_surf)+np.square(vel_z_surf))

# plot surface vorticity and speed 

surf_vor_sam = vor[x_sam, z_sam]
surf_spd_sam = spd[x_sam, z_sam]

fig1, ax1 = plt.subplots(1,1, figsize=(9,6))
scat1 = ax1.scatter(x_sam/1023*4000,z_sam/1023*4000,c=surf_spd_sam,cmap=mpl.cm.coolwarm)
#ax1.set_title('Surface speed (m/s)',fontsize=18, **tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad = 20
cbar.ax.set_ylabel('Surface speed (m/s)', rotation=270, **tnrfont,fontsize=20)
cbar.ax.tick_params(labelsize=20) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=20, **tnrfont)
plt.ylabel('y (m)',fontsize=20, **tnrfont)
plt.xticks(fontsize=20, **tnrfont)
plt.yticks(fontsize=20, **tnrfont)

fig2, ax2 = plt.subplots(1,1, figsize=(9,6))
vmin = min(surf_vor_sam)
vmax = max(surf_vor_sam)
norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=0.0001, vmax=vmax)
scat2 = ax2.scatter(x_sam/1023*4000,z_sam/1023*4000,c=surf_vor_sam,cmap=mpl.cm.coolwarm,norm=norm)
#ax2.set_title('Surface vertical vorticity $(s^{-1})$ for Run22',fontsize=18,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat2)
cbar.ax.get_yaxis().labelpad = 20
cbar.ax.set_ylabel('Surface vertical vorticity (s$^{-1}$)', rotation=270,**tnrfont,fontsize=20)
cbar.ax.tick_params(labelsize=20) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=20,**tnrfont)
plt.ylabel('y (m)',fontsize=20,**tnrfont)
plt.xticks(fontsize=20, **tnrfont)
plt.yticks(fontsize=20, **tnrfont)

fig3, ax3 = plt.subplots(1,1, figsize=(9,6))
scat3 = ax3.scatter(x_sam/1023*4000,z_sam/1023*4000,c=mld_sam,cmap=mpl.cm.coolwarm)
#ax3.set_title('Mixed layer depth (m) for Run22',fontsize=18,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat3)
cbar.ax.get_yaxis().labelpad = 20
cbar.ax.set_ylabel('Mixed layer depth (m)', rotation=270,**tnrfont,fontsize=20)
cbar.ax.tick_params(labelsize=20) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=20,**tnrfont)
plt.ylabel('y (m)',fontsize=20,**tnrfont)
plt.xticks(fontsize=20, **tnrfont)
plt.yticks(fontsize=20, **tnrfont)

# Load model and apply to pre-processed data

modelname = 'paper-data/model_les_k2_N120_pc7_rep7.nc'
m_loaded = pyxpcm.load_netcdf(modelname)
th1_mld_nml_xr = xr.DataArray(th1_mld_nml, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
ds = xr.Dataset({'TH1':th1_mld_nml_xr, 'X':x_sam, 'Z':z_sam})
features_in_ds = {'buoyancy': 'TH1'}
features_zdim='COORD'
m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
truth_sam = np.zeros(N)
truth_sam[surf_vor_sam>=0.0001]=1
truth_sam[surf_vor_sam<0.0001]=-1
df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, mld_sam, np.array(ds['PCM_LABELS']), np.zeros(N), truth_sam)).T, columns=['N_PROF', 'X', 'Z', 'MLD', 'CLASS', 'EDDY', 'TRUTH'])
class0_ind = (df['CLASS']==0)
class1_ind = (df['CLASS']==1)
class0_mld = np.mean(df['MLD'][class0_ind])
class1_mld = np.mean(df['MLD'][class1_ind])
if class0_mld<=class1_mld:
    df['EDDY'][class1_ind]=-1
    df['EDDY'][class0_ind]=1
else:
    df['EDDY'][class1_ind]=1
    df['EDDY'][class0_ind]=-1

# Plot model prediction and truth labels

fig4, ax4 = plt.subplots(1,1, figsize=(8,8))
plt.scatter(df['X'][df['EDDY']==1]/1023*4000, df['Z'][df['EDDY']==1]/1023*4000, color='orange', label='Eddy')
plt.scatter(df['X'][df['EDDY']==-1]/1023*4000, df['Z'][df['EDDY']==-1]/1023*4000, color='blue', label='Non-eddy')
#ax4.legend(fontsize=30)
ax4.set_title('PCM prediction',fontsize=30,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
plt.xlabel('x (m)',fontsize=30,**tnrfont)
plt.ylabel('y (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=30, rotation=45, **tnrfont)
plt.yticks(fontsize=30, **tnrfont)

fig5, ax5 = plt.subplots(1,1, figsize=(8,8))
plt.scatter(df['X'][df['TRUTH']==1]/1023*4000, df['Z'][df['TRUTH']==1]/1023*4000, color='orange', label='Eddy')
plt.scatter(df['X'][df['TRUTH']==-1]/1023*4000, df['Z'][df['TRUTH']==-1]/1023*4000, color='blue', label='Non-eddy')
#ax5.legend(fontsize=30)
ax5.set_title('Truth label',fontsize=30,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
plt.xlabel('x (m)',fontsize=30,**tnrfont)
plt.ylabel('y (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=30, rotation=45, **tnrfont)
plt.yticks(fontsize=30, **tnrfont)

# Plot rescaled and normalized profiles according to classes

noneddy_50th_mld = np.percentile(th1_mld_nml[df['EDDY']==-1],50,axis=0)
noneddy_25th_mld = np.percentile(th1_mld_nml[df['EDDY']==-1],25,axis=0)
noneddy_75th_mld = np.percentile(th1_mld_nml[df['EDDY']==-1],75,axis=0)
eddy_50th_mld = np.percentile(th1_mld_nml[df['EDDY']==1],50,axis=0)
eddy_25th_mld = np.percentile(th1_mld_nml[df['EDDY']==1],25,axis=0)
eddy_75th_mld = np.percentile(th1_mld_nml[df['EDDY']==1],75,axis=0)

fig6, ax6 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['EDDY'][i]==-1:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(noneddy_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(noneddy_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(noneddy_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax6.legend(fontsize=30)
#ax6.set_title('Non-eddy',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

fig7, ax7 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['EDDY'][i]==1:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(eddy_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(eddy_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(eddy_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax7.legend(fontsize=30)
#ax7.set_title('Eddy',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Plot original profiles according to classes

noneddy_50th_orig = np.percentile(th1_sam[df['EDDY']==-1],50,axis=0)
noneddy_25th_orig = np.percentile(th1_sam[df['EDDY']==-1],25,axis=0)
noneddy_75th_orig = np.percentile(th1_sam[df['EDDY']==-1],75,axis=0)
eddy_50th_orig = np.percentile(th1_sam[df['EDDY']==1],50,axis=0)
eddy_25th_orig = np.percentile(th1_sam[df['EDDY']==1],25,axis=0)
eddy_75th_orig = np.percentile(th1_sam[df['EDDY']==1],75,axis=0)

fig8, ax8 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['EDDY'][i]==-1:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(noneddy_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(noneddy_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(noneddy_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax8.legend(fontsize=30)
#ax8.set_title('Non-eddy',fontsize=22, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

fig9, ax9 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['EDDY'][i]==1:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(eddy_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(eddy_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(eddy_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax9.legend(fontsize=30)
#ax9.set_title('Eddy',fontsize=22, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Load model for k=5 and apply to pre-processed data

modelname = 'paper-data/model_les_k5_N1200_pc7_rep2.nc'
m_loaded = pyxpcm.load_netcdf(modelname)
th1_mld_nml_xr = xr.DataArray(th1_mld_nml, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
ds = xr.Dataset({'TH1':th1_mld_nml_xr, 'X':x_sam, 'Z':z_sam})
features_in_ds = {'buoyancy': 'TH1'}
features_zdim='COORD'
m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, mld_sam, np.array(ds['PCM_LABELS']))).T, columns=['N_PROF', 'X', 'Z', 'MLD', 'CLASS'])
df['CLASS'] = df['CLASS']+1

# Plot model prediction

fig10, ax10 = plt.subplots(1,1, figsize=(9,6))
cmap = plt.cm.jet
norm = colors.BoundaryNorm(np.arange(0.5, 6.5, 1), cmap.N)
plt.scatter(df['X']/1023*4000, df['Z']/1023*4000, c=df['CLASS'], cmap=cmap,norm=norm)
cbar = plt.colorbar(ticks=np.linspace(1, 5, 5))
cbar.ax.get_yaxis().labelpad = 30
cbar.ax.set_ylabel('Classes', rotation=270,**tnrfont,fontsize=30)
ax10.set_title('PCM prediction (5 classes)',fontsize=30,**tnrfont)
cbar.ax.tick_params(labelsize=26)
cbar.ax.set_yticks(**tnrfont) 
plt.xlim([0,4000])
plt.ylim([0,4000])
plt.xlabel('x (m)',fontsize=30,**tnrfont)
plt.ylabel('y (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Plot rescaled and normalized profiles according to classes

class1_50th_mld = np.percentile(th1_mld_nml[df['CLASS']==1],50,axis=0)
class1_25th_mld = np.percentile(th1_mld_nml[df['CLASS']==1],25,axis=0)
class1_75th_mld = np.percentile(th1_mld_nml[df['CLASS']==1],75,axis=0)
fig11, ax11 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==1:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(class1_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class1_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class1_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax11.legend(fontsize=30)
ax11.set_title('Class 1',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class2_50th_mld = np.percentile(th1_mld_nml[df['CLASS']==2],50,axis=0)
class2_25th_mld = np.percentile(th1_mld_nml[df['CLASS']==2],25,axis=0)
class2_75th_mld = np.percentile(th1_mld_nml[df['CLASS']==2],75,axis=0)
fig12, ax12 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==2:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(class2_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class2_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class2_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax12.legend(fontsize=30)
ax12.set_title('Class 2',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class3_50th_mld = np.percentile(th1_mld_nml[df['CLASS']==3],50,axis=0)
class3_25th_mld = np.percentile(th1_mld_nml[df['CLASS']==3],25,axis=0)
class3_75th_mld = np.percentile(th1_mld_nml[df['CLASS']==3],75,axis=0)
fig13, ax13 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==3:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(class3_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class3_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class3_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax13.legend(fontsize=30)
ax13.set_title('Class 3',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class4_50th_mld = np.percentile(th1_mld_nml[df['CLASS']==4],50,axis=0)
class4_25th_mld = np.percentile(th1_mld_nml[df['CLASS']==4],25,axis=0)
class4_75th_mld = np.percentile(th1_mld_nml[df['CLASS']==4],75,axis=0)
fig14, ax14 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==4:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(class4_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class4_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class4_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax14.legend(fontsize=30)
ax14.set_title('Class 4',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class5_50th_mld = np.percentile(th1_mld_nml[df['CLASS']==5],50,axis=0)
class5_25th_mld = np.percentile(th1_mld_nml[df['CLASS']==5],25,axis=0)
class5_75th_mld = np.percentile(th1_mld_nml[df['CLASS']==5],75,axis=0)
fig15, ax15 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==5:
        plt.plot(th1_mld_nml[i], coord_new, alpha=0.2)
plt.plot(class5_50th_mld,coord_new,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class5_25th_mld,coord_new,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class5_75th_mld,coord_new,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax15.legend(fontsize=30)
ax15.set_title('Class 5',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.00015])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Plot original profiles according to classes

class1_50th_orig = np.percentile(th1_sam[df['CLASS']==1],50,axis=0)
class1_25th_orig = np.percentile(th1_sam[df['CLASS']==1],25,axis=0)
class1_75th_orig = np.percentile(th1_sam[df['CLASS']==1],75,axis=0)
fig16, ax16 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==1:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(class1_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class1_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class1_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax16.legend(fontsize=30)
ax16.set_title('Class 1',fontsize=30, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class2_50th_orig = np.percentile(th1_sam[df['CLASS']==2],50,axis=0)
class2_25th_orig = np.percentile(th1_sam[df['CLASS']==2],25,axis=0)
class2_75th_orig = np.percentile(th1_sam[df['CLASS']==2],75,axis=0) 
fig17, ax17 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==2:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(class2_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class2_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class2_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax17.legend(fontsize=30)
ax17.set_title('Class 2',fontsize=30, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class3_50th_orig = np.percentile(th1_sam[df['CLASS']==3],50,axis=0)
class3_25th_orig = np.percentile(th1_sam[df['CLASS']==3],25,axis=0)
class3_75th_orig = np.percentile(th1_sam[df['CLASS']==3],75,axis=0) 
fig18, ax18 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==3:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(class3_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class3_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class3_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax18.legend(fontsize=30)
ax18.set_title('Class 3',fontsize=30, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class4_50th_orig = np.percentile(th1_sam[df['CLASS']==4],50,axis=0)
class4_25th_orig = np.percentile(th1_sam[df['CLASS']==4],25,axis=0)
class4_75th_orig = np.percentile(th1_sam[df['CLASS']==4],75,axis=0) 
fig19, ax19 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==4:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(class4_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class4_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class4_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax19.legend(fontsize=30)
ax19.set_title('Class 4',fontsize=30, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

class5_50th_orig = np.percentile(th1_sam[df['CLASS']==5],50,axis=0)
class5_25th_orig = np.percentile(th1_sam[df['CLASS']==5],25,axis=0)
class5_75th_orig = np.percentile(th1_sam[df['CLASS']==5],75,axis=0) 
fig20, ax20 = plt.subplots(1,1,figsize=(10,10))
for i in range(len(df['N_PROF'])):
    if df['CLASS'][i]==5:
        plt.plot(th1_sam[i], depth, alpha=0.2)
plt.plot(class5_50th_orig,depth,'k',linestyle='solid',linewidth=1.5,label='50th percentile')
plt.plot(class5_25th_orig,depth,'b',linestyle='dashed',linewidth=1.5,label='25th percentile')
plt.plot(class5_75th_orig,depth,'b',linestyle='dashdot',linewidth=1.5,label='75th percentile')
ax20.legend(fontsize=30)
ax20.set_title('Class 5',fontsize=30, **tnrfont)
plt.xlim([0,0.0028])
plt.ylim([-800,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

plt.show()