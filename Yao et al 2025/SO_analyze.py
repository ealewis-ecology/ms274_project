# Analyze SO dataset and generate plots

# import libraries
import numpy as np
import pandas as pd
import xarray as xr
import pyxpcm
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import scipy.io as spio

mpl.rc('font',family='Times New Roman')
np.random.seed(257)
tnrfont = {'fontname':'Times New Roman'}

mat_contents = spio.loadmat('paper-data/data_so_profiles.mat',squeeze_me=True)
depth = np.flip(np.copy(mat_contents['Depth']))
lat = np.copy(mat_contents['LAT'])
lon = np.copy(mat_contents['LON'])
temperature = np.flip(np.vstack(mat_contents['T']),1)
salinity = np.flip(np.vstack(mat_contents['S']),1)
bottom_depth = np.copy(mat_contents['bottom_depth'])
buoyancy = np.flip(np.vstack(mat_contents['buoy']),1)
loc = np.vstack(mat_contents['loc'])
vel_x = np.copy(mat_contents['u'])
vel_y = np.copy(mat_contents['v'])
vorticity = np.copy(mat_contents['vorticity'])
loc = loc-1

# exclude points north of 50S latitude
prof1 = (loc[:,1]<=1919)
loc = loc[prof1,:]
temperature = temperature[prof1,:]
salinity = salinity[prof1,:]
buoyancy = buoyancy[prof1,:]

# exclude points w/ bottom depth <= 500m
prof2 = []
for i in range(np.sum(prof1)):
    lo = loc[i,0]
    la = loc[i,1]
    if bottom_depth[lo,la]<-500:
        prof2.append(True)
    else:
        prof2.append(False)
loc = loc[prof2,:]
temperature = temperature[prof2,:]
salinity = salinity[prof2,:]
buoyancy = buoyancy[prof2,:]

pc_num = 4
k = 2
N = np.sum(prof2)
th1_del = 0.0003924
num = 100

coord_new = np.linspace(-1,0,num=num)
buoy_mld = np.zeros((N,num))
len_sam = np.zeros(N)
mld_sam = np.zeros(N)
for i in range(N):
    prof = buoyancy[i,:]
    surf_val = prof[-1]
    ind_plus = np.where(surf_val-prof>th1_del)
    ind = np.arange(ind_plus[0][-1]+1,len(prof))
    prof = prof[ind]
    prof_len = len(prof)
    len_sam[i] = prof_len
    coord_depth = depth[ind_plus[0][-1]+1:]
    mld_sam[i] = coord_depth[0]
    coord_old = (coord_depth-coord_depth[-1])/np.abs(coord_depth[0])
    prof = np.interp(coord_new, coord_old, prof)
    buoy_mld[i,:] = prof

buoy_mld_nml = np.zeros((N,num))
buoy_mean_sam = np.zeros(N)
for j in range(N):
    prof = buoy_mld[j,:]
    avg = np.mean(prof)
    buoy_mean_sam[j] = avg
    prof = prof - avg
    buoy_mld_nml[j,:] = prof

modelname = 'paper-data/model_so_k2_pc4.nc'
m_loaded = pyxpcm.load_netcdf(modelname)
buoy_mld_nml_xr = xr.DataArray(buoy_mld_nml, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new}) 
ds = xr.Dataset({'TH1':buoy_mld_nml_xr, 'X':loc[:,0], 'Z':loc[:,1]})
pcm_features = {'buoyancy': coord_new}
features_in_ds = {'buoyancy': 'TH1'}
features_zdim='COORD'
m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), loc[:,0], loc[:,1], mld_sam, np.array(ds['PCM_LABELS']))).T, columns=['N_PROF', 'X', 'Z', 'MLD', 'CLASS'])
df['CLASS'] = df['CLASS']+1

noneddy_mean_mld_nml = np.mean(buoy_mld_nml[df['CLASS']==1],axis=0)
noneddy_std_mld_nml = np.std(buoy_mld_nml[df['CLASS']==1],axis=0)
eddy_mean_mld_nml = np.mean(buoy_mld_nml[df['CLASS']==2],axis=0)
eddy_std_mld_nml = np.std(buoy_mld_nml[df['CLASS']==2],axis=0)

fig6, ax6 = plt.subplots(1,1,figsize=(10,10))
ax6.plot(noneddy_mean_mld_nml, coord_new, linewidth=2.5, label='Non-eddy', color='blue')
ax6.plot(eddy_mean_mld_nml, coord_new, linewidth=2.5, label='Eddy', color='orange')
ax6.fill_betweenx(coord_new, noneddy_mean_mld_nml+noneddy_std_mld_nml, noneddy_mean_mld_nml-noneddy_std_mld_nml, facecolor='blue', alpha=0.3)
ax6.fill_betweenx(coord_new, eddy_mean_mld_nml+eddy_std_mld_nml, eddy_mean_mld_nml-eddy_std_mld_nml, facecolor='orange', alpha=0.3)
ax6.legend(fontsize=30)
ax6.set_title('Rescaled and normalized profiles',fontsize=30, **tnrfont)
plt.xlim([-0.0004,0.0002])
plt.ylim([-1,0])
plt.xlabel('Buoyancy (m/s$^2$)',fontsize=30,**tnrfont)
plt.ylabel('Depth (rescaled)',fontsize=30,**tnrfont)
plt.xticks(fontsize=30,rotation=45, **tnrfont)
plt.yticks(fontsize=30, **tnrfont)

class ScalarFormatterClass(ScalarFormatter):
   def _set_format(self):
      self.format = "%1.1f"

bins=np.linspace(-200,0,15)
hist_mld_1, bin_edges_mld_1 = np.histogram(mld_sam[df['CLASS']==1],bins=bins)
hist_mld_2, bin_edges_mld_2 = np.histogram(mld_sam[df['CLASS']==2],bins=bins)
hist_eddy_frac = np.divide(hist_mld_2, hist_mld_2+hist_mld_1)
bin_centers = np.convolve(bin_edges_mld_1, np.ones(2), 'valid') / 2

fig3,ax3=plt.subplots(1,1,figsize=(10,10))
color = 'tab:blue'
ax3.set_ylabel('Number of points', color=color,fontsize=50,**tnrfont)  # we already handled the x-label with ax1
ax3.hist(mld_sam,bins=bins,rwidth=0.8,color=color)
ax3.tick_params(axis='y', labelcolor=color)
ax3.set_xlabel('MLD (m)',fontsize=50,**tnrfont)
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)

ax4 = ax3.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'

ax4.plot(bin_centers,hist_eddy_frac,'o-',linewidth=3, markersize=10,color=color)
#ax4.set_title('Histogram of mixed layer depth with fractions of submesoscale active points in each bin',fontsize=18,**tnrfont)
ax4.set_ylabel('Fraction classifies as Eddy',color=color, fontsize=50,rotation=270,labelpad=50,**tnrfont)
ax4.tick_params(axis='y', labelcolor=color)
ax4.set_ylim([0,1])
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)
xScalarFormatter = ScalarFormatterClass(useMathText=True)
xScalarFormatter.set_powerlimits((0,0))
ax4.xaxis.set_major_formatter(xScalarFormatter)

fig3.tight_layout() 


bins=np.linspace(-0.0002,0.00015,20)
hist_vor_1, bin_edges_vor_1 = np.histogram(vorticity[loc[:,0],loc[:,1]][df['CLASS']==1],bins=bins)
hist_vor_2, bin_edges_vor_2 = np.histogram(vorticity[loc[:,0],loc[:,1]][df['CLASS']==2],bins=bins)
hist_eddy_frac = np.divide(hist_vor_2, hist_vor_2+hist_vor_1)
bin_centers = np.convolve(bin_edges_vor_1, np.ones(2), 'valid') / 2

fig5,ax5=plt.subplots(1,1,figsize=(10,10))
color = 'tab:blue'
ax5.set_ylabel('Number of points', color=color,fontsize=50,**tnrfont)  # we already handled the x-label with ax1
ax5.hist(vorticity[loc[:,0],loc[:,1]],bins=bins,rwidth=0.8,color=color)
ax5.tick_params(axis='y', labelcolor=color)
ax5.set_xlabel('$\zeta$ (s$^{-1}$)',fontsize=50,**tnrfont)
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)

ax6 = ax5.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax6.plot(bin_centers,hist_eddy_frac,'o-',linewidth=3, markersize=10,color=color)
#ax6.set_title('Histogram of surface vertical vorticity $\zeta$ with fractions of points in Class 2 in each bin',fontsize=18,**tnrfont)
ax6.set_ylabel('Fraction classified as Eddy',color=color, fontsize=50,rotation=270,labelpad=50,**tnrfont)
ax6.tick_params(axis='y', labelcolor=color)
ax6.set_ylim([0,1])
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)
xScalarFormatter = ScalarFormatterClass(useMathText=True)
xScalarFormatter.set_powerlimits((0,0))
ax6.xaxis.set_major_formatter(xScalarFormatter)

fig5.tight_layout() 

mat_new = spio.loadmat('paper-data/data_so_vor-hat.mat',squeeze_me=True)
vor_hat = np.copy(mat_new['vor_new'])

bins=np.linspace(0,0.000075,20)
hist_vor_hat_1, bin_edges_vor_hat_1 = np.histogram(vor_hat[loc[:,0],loc[:,1]][df['CLASS']==1],bins=bins)
hist_vor_hat_2, bin_edges_vor_hat_2 = np.histogram(vor_hat[loc[:,0],loc[:,1]][df['CLASS']==2],bins=bins)
hist_eddy_frac = np.divide(hist_vor_hat_2, hist_vor_hat_2+hist_vor_hat_1)
bin_centers = np.convolve(bin_edges_vor_hat_1, np.ones(2), 'valid') / 2

fig9,ax9=plt.subplots(1,1,figsize=(10,10))
color = 'tab:blue'
ax9.set_ylabel('Number of points', color=color,fontsize=50,**tnrfont)  # we already handled the x-label with ax1
ax9.hist(vor_hat[loc[:,0],loc[:,1]],bins=bins,rwidth=0.8,color=color)
ax9.tick_params(axis='y', labelcolor=color)
ax9.set_xlabel('$\hat{\zeta}$ (s$^{-1}$)',fontsize=50,**tnrfont)
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)

ax10 = ax9.twinx()  # instantiate a second axes that shares the same x-axis
color = 'tab:red'
ax10.plot(bin_centers,hist_eddy_frac,'o-',linewidth=3, markersize=10,color=color)
#ax10.set_title('Histogram of $\hat{\zeta}$ with fractions of Class 2 in each bin',fontsize=18,**tnrfont)
ax10.set_ylabel('Fraction classified as Eddy',color=color, fontsize=50,rotation=270,labelpad=50,**tnrfont)
ax10.tick_params(axis='y', labelcolor=color)
ax10.set_ylim([0,1])
plt.xticks(fontsize=40,rotation=45)
plt.yticks(fontsize=40)
xScalarFormatter = ScalarFormatterClass(useMathText=True)
xScalarFormatter.set_powerlimits((0,0))
ax10.xaxis.set_major_formatter(xScalarFormatter)

fig9.tight_layout() 