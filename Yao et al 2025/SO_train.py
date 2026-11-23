# import libraries
import numpy as np
import pandas as pd
import xarray as xr
from pyxpcm.models import pcm
import pyxpcm
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import scipy.io as spio

np.random.seed(257)

import pcm_func as pf
import skill_func as sf

mat_contents = spio.loadmat('data/May13_profiles.mat',squeeze_me=True)

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

k = 2
N = np.sum(prof2)
th1_del = 0.0003924
num = 50
coord_new = np.linspace(-1,0,num=num)
buoy_mld = np.zeros((N,num))
len_training = np.zeros(N)
mld_training = np.zeros(N)
for i in range(N):
    prof = buoyancy[i,:]
    surf_val = prof[-1]
    ind_plus = np.where(surf_val-prof>th1_del)
    ind = np.arange(ind_plus[0][-1]+1,len(prof))
    prof = prof[ind]
    prof_len = len(prof)
    len_training[i] = prof_len
    coord_depth = depth[ind_plus[0][-1]+1:]
    mld_training[i] = coord_depth[0]
    coord_old = (coord_depth-coord_depth[-1])/np.abs(coord_depth[0])
    prof = np.interp(coord_new, coord_old, prof)
    buoy_mld[i,:] = prof

buoy_mld = xr.DataArray(buoy_mld, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
ds = xr.Dataset({'TH1':buoy_mld, 'X':loc[:,0], 'Z':loc[:,1]})
pc_num = 10
pcm_features = {'buoyancy': coord_new}
features_in_ds = {'buoyancy': 'TH1'}
features_zdim='COORD'
m, ds = pf.training(k, pcm_features, features_in_ds, features_zdim, ds, pc_num=pc_num)
m.to_netcdf('May13_pc{}_num{}.nc'.format(pc_num,num))
fig1, ax1, fig2, ax2 = pf.plots(m, ds, k, loc[:,0], loc[:,1])

data_dic = {"Depth": depth, "LAT": lat, "LON": lon, "Temperature": temperature, "Salinity": salinity, "Bottom_Depth": bottom_depth, "Buoyancy": buoyancy, "LOC": loc, "U": vel_x, "V": vel_y, "Vorticity": vorticity,\
    "Coord_New": coord_new, "Buoy_MLD": buoy_mld, "MLD": mld_training, "CLASS": np.asarray(ds['PCM_LABELS']), "X":np.asarray(ds['X']), "Z":np.asarray(ds['Z']), "PCM_POST":np.asarray(ds['PCM_POST'])}

spio.savemat("so-data.mat", data_dic)