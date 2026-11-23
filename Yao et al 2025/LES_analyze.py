# Analyze LES dataset and generate plots for buoyancy field and correlation/homogeneity of LES dataset

# import libraries
import numpy as np
import pandas as pd
import xarray as xr
import pyxpcm
import matplotlib as mpl
import matplotlib.pyplot as plt

from scipy import ndimage

mpl.rc('font',family='Times New Roman')
np.random.seed(256)
tnrfont = {'fontname':'Times New Roman'}

# Load data and discard artificial surface value
buo_sam = np.load('paper-data/data_les_buo_sample.npy')
x_sam = np.load('paper-data/data_les_x_sample.npy')
z_sam = np.load('paper-data/data_les_y_sample.npy')
buo_surf = np.load('paper-data/data_les_buo_surf.npy')
vel_x = np.load('paper-data/data_les_velx_surf.npy')
vel_z = np.load('paper-data/data_les_vely_surf.npy')
depth = np.load('paper-data/data_les_depth.npy')

# plot surface buoyancy field

X, Y = np.meshgrid(np.arange(1025)/1023*4000, np.arange(1025)/1023*4000)

fig1, ax1 = plt.subplots(1,1, figsize=(10,8))
scat1 = ax1.pcolormesh(X,Y,buo_surf, cmap=mpl.cm.coolwarm,)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad=35
cbar.ax.set_ylabel('Surface buoyancy (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Calculate surface buoyancy gradient

n = 1024
h = 4000/(n-1)

i_p = np.append(np.arange(1,n), 0)
i_m = np.append(n-1, np.arange(n-1))
buo_surf_x_p = buo_surf[i_p,:]
buo_surf_x_m = buo_surf[i_m,:]
buo_surf_y_p = buo_surf[:,i_p]
buo_surf_y_m = buo_surf[:,i_m]
buo_surf_dx = (buo_surf_x_p - buo_surf_x_m)/2/h
buo_surf_dy = (buo_surf_y_p - buo_surf_y_m)/2/h
buo_surf_grad = np.sqrt(np.square(buo_surf_dx)+np.square(buo_surf_dy))

# plot surface buoyancy gradient

fig1, ax1 = plt.subplots(1,1, figsize=(10,8))
scat1 = ax1.pcolormesh(X,Y,buo_surf_grad, cmap=mpl.cm.coolwarm,)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad=35
cbar.ax.set_ylabel('Surface buoyancy gradient (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Calculate smoothed surface buoyancy gradient
knl50 = np.ones((50,50))/50/50
buo_surf_grad_smt50 = ndimage.convolve(buo_surf_grad, knl50, mode='wrap')
knl100 = np.ones((100,100))/100/100
buo_surf_grad_smt100 = ndimage.convolve(buo_surf_grad, knl100, mode='wrap')

# plot smoothed surface buoyancy field

fig, ax = plt.subplots(1,1, figsize=(10,8))
scat2 = ax.pcolormesh(X,Y,buo_surf_grad_smt50, cmap=mpl.cm.coolwarm,)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad=35
cbar.ax.set_ylabel('Smoothed surface buoyancy gradient (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

fig, ax = plt.subplots(1,1, figsize=(10,8))
scat3 = ax.pcolormesh(X,Y,buo_surf_grad_smt100, cmap=mpl.cm.coolwarm,)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad=35
cbar.ax.set_ylabel('Smoothed surface buoyancy gradient (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# Apply model to sampled data and compare results

# pre-process data
N = 10000
buo_del = 0.0003924
num = 100

coord_new = np.linspace(-1,0,num=num)
buo_mld = np.zeros((N,num))
mld_sam = np.zeros(N)
for i in range(N):
    prof = buo_sam[i,:]
    surf_val = prof[-1]
    ind = np.where(surf_val-prof<=buo_del)
    prof = prof[ind]
    prof_len = len(prof)
    mld_sam[i] = -1*prof_len*(800/256)
    coord_old = np.linspace(-1,0,num=prof_len)
    prof = np.interp(coord_new, coord_old, prof)
    buo_mld[i,:] = prof

buo_mld_nml = np.zeros((N,num))
buo_mean_sam = np.zeros(N)
for j in range(N):
    prof = buo_mld[j,:]
    avg = np.mean(prof)
    buo_mean_sam[j] = avg
    prof = prof - avg
    buo_mld_nml[j,:] = prof

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
surf_vor_sam = vor[x_sam, z_sam]
surf_spd_sam = spd[x_sam, z_sam]

# Load model and apply to pre-processed data
modelname = 'paper-data/model_les_k2_N120_pc7_rep7.nc'
m_loaded = pyxpcm.load_netcdf(modelname)
buo_mld_nml_xr = xr.DataArray(buo_mld_nml, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
ds = xr.Dataset({'TH1':buo_mld_nml_xr, 'X':x_sam, 'Z':z_sam})
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
if class0_mld>=class1_mld:
    df['EDDY'][class1_ind]=-1
    df['EDDY'][class0_ind]=1
else:
    df['EDDY'][class1_ind]=1
    df['EDDY'][class0_ind]=-1

# Plot model prediction and truth labels

fig, ax = plt.subplots(1,1, figsize=(8,8))
plt.scatter(df['X'][df['EDDY']==1]/1023*4000, df['Z'][df['EDDY']==1]/1023*4000, color='orange', label='Eddy')
plt.scatter(df['X'][df['EDDY']==-1]/1023*4000, df['Z'][df['EDDY']==-1]/1023*4000, color='blue', label='Non-eddy')
ax.set_title('PCM prediction',fontsize=30,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
plt.xlabel('x (m)',fontsize=30,**tnrfont)
plt.ylabel('y (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=30, rotation=45, **tnrfont)
plt.yticks(fontsize=30, **tnrfont)

fig, ax = plt.subplots(1,1, figsize=(8,8))
plt.scatter(df['X'][df['TRUTH']==1]/1023*4000, df['Z'][df['TRUTH']==1]/1023*4000, color='orange', label='Eddy')
plt.scatter(df['X'][df['TRUTH']==-1]/1023*4000, df['Z'][df['TRUTH']==-1]/1023*4000, color='blue', label='Non-eddy')
ax.set_title('Truth label',fontsize=30,**tnrfont)
plt.xlim([0,4000])
plt.ylim([0,4000])
plt.xlabel('x (m)',fontsize=30,**tnrfont)
plt.ylabel('y (m)',fontsize=30,**tnrfont)
plt.xticks(fontsize=30, rotation=45, **tnrfont)
plt.yticks(fontsize=30, **tnrfont)

# extract smoothed surface buoyancy gradient at sampled points and scatter plot (smoothed w/ 100x100 window)

buo_surf_grad_smt100_sam = np.transpose(buo_surf_grad_smt100)[x_sam,z_sam]

fig1, ax1 = plt.subplots(1,1, figsize=(10,8))
scat1 = ax1.scatter(x_sam/1023*4000,z_sam/1023*4000,c=buo_surf_grad_smt100_sam,cmap=mpl.cm.coolwarm)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad = 30
cbar.ax.set_ylabel('Smoothed surface buoyancy gradient (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# histogram of smoothed surface buoyancy gradient with fraction of points classified as Eddy

bins=np.linspace(min(buo_surf_grad_smt100_sam),max(buo_surf_grad_smt100_sam),15)
hist_buo_eddy, bin_edges_buo_eddy = np.histogram(buo_surf_grad_smt100_sam[df['CLASS']==1],bins=bins)
hist_buo_noneddy, bin_edges_buo_noneddy = np.histogram(buo_surf_grad_smt100_sam[df['CLASS']==0],bins=bins)
hist_eddy_frac = np.divide(hist_buo_eddy, hist_buo_eddy+hist_buo_noneddy)
bin_centers = np.convolve(bin_edges_buo_eddy, np.ones(2), 'valid') / 2

fig3,ax3=plt.subplots(1,1,figsize=(10,10))
color = 'tab:blue'
ax3.set_ylabel('Number of points', color=color,fontsize=30,**tnrfont)  # we already handled the x-label with ax1
ax3.hist(buo_surf_grad_smt100_sam,bins=bins,rwidth=0.8,color=color)
ax3.tick_params(axis='y', labelcolor=color)
ax3.set_xlabel('Smoothed surface buoyancy gradient (m/s$^2$)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26,rotation=45)
plt.yticks(fontsize=26)

ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'

ax4.plot(bin_centers,hist_eddy_frac,'o-',linewidth=3, markersize=10,color=color)
ax4.set_ylabel('Fraction classifies as Eddy',color=color, fontsize=30,rotation=270,labelpad=30,**tnrfont)
ax4.tick_params(axis='y', labelcolor=color)
ax4.set_ylim([0,1])
plt.xticks(fontsize=26)
plt.yticks(fontsize=26)

fig3.tight_layout() 

# extract smoothed surface buoyancy gradient at sampled points and scatter plot (smoothed w/ 50x50 window)

buo_surf_grad_smt50_sam = np.transpose(buo_surf_grad_smt50)[x_sam,z_sam]

fig1, ax1 = plt.subplots(1,1, figsize=(10,8))
scat1 = ax1.scatter(x_sam/1023*4000,z_sam/1023*4000,c=buo_surf_grad_smt50_sam,cmap=mpl.cm.coolwarm)
plt.xlim([0,4000])
plt.ylim([0,4000])
cbar = plt.colorbar(scat1)
cbar.ax.get_yaxis().labelpad = 30
cbar.ax.set_ylabel('Smoothed surface buoyancy gradient (m/s$^2$)', rotation=270, **tnrfont,fontsize=30)
cbar.ax.tick_params(labelsize=26) 
cbar.ax.set_yticks(**tnrfont)
plt.xlabel('x (m)',fontsize=30, **tnrfont)
plt.ylabel('y (m)',fontsize=30, **tnrfont)
plt.xticks(fontsize=26,rotation=45, **tnrfont)
plt.yticks(fontsize=26, **tnrfont)

# histogram of smoothed surface buoyancy gradient with fraction of points classified as Eddy

bins=np.linspace(min(buo_surf_grad_smt50_sam),max(buo_surf_grad_smt50_sam),15)
hist_buo_eddy, bin_edges_buo_eddy = np.histogram(buo_surf_grad_smt50_sam[df['CLASS']==1],bins=bins)
hist_buo_noneddy, bin_edges_buo_noneddy = np.histogram(buo_surf_grad_smt50_sam[df['CLASS']==0],bins=bins)
hist_eddy_frac = np.divide(hist_buo_eddy, hist_buo_eddy+hist_buo_noneddy)
bin_centers = np.convolve(bin_edges_buo_eddy, np.ones(2), 'valid') / 2

fig3,ax3=plt.subplots(1,1,figsize=(10,10))
color = 'tab:blue'
ax3.set_ylabel('Number of points', color=color,fontsize=30,**tnrfont)  # we already handled the x-label with ax1
ax3.hist(buo_surf_grad_smt50_sam,bins=bins,rwidth=0.8,color=color)
ax3.tick_params(axis='y', labelcolor=color)
ax3.set_xlabel('Smoothed surface buoyancy gradient (m/s$^2$)',fontsize=30,**tnrfont)
plt.xticks(fontsize=26,rotation=45)
plt.yticks(fontsize=26)

ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'

ax4.plot(bin_centers,hist_eddy_frac,'o-',linewidth=3, markersize=10,color=color)
ax4.set_ylabel('Fraction classifies as Eddy',color=color, fontsize=30,rotation=270,labelpad=30,**tnrfont)
ax4.tick_params(axis='y', labelcolor=color)
ax4.set_ylim([0,1])
plt.xticks(fontsize=26)
plt.yticks(fontsize=26)

fig3.tight_layout() 