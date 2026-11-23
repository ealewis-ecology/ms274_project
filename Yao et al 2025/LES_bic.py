# Trains PCM models on LES dataset with MLD rescaling and normalization
# Calculate BIC scores with varying number of classes and varying N
# Sets of parameters: k=2-10; N=1200; PC=7

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
import scipy.io as spio

np.random.seed(257)

import pcm_func as pf
import skill_func as sf

# load data
th1_run20 = np.load('paper-data/les-th1-run20.npy')
th1_run21 = np.load('paper-data/les-th1-run21.npy')
th1_run22 = np.load('paper-data/les-th1-run22.npy')
th1_run23 = np.load('paper-data/les-th1-run23.npy')
th1_run24 = np.load('paper-data/les-th1-run24.npy')
th1_run25 = np.load('paper-data/les-th1-run25.npy')

th1_run20 = th1_run20[:,0:-1,:]
th1_run21 = th1_run21[:,0:-1,:]
th1_run22 = th1_run22[:,0:-1,:]
th1_run23 = th1_run23[:,0:-1,:]
th1_run24 = th1_run24[:,0:-1,:]
th1_run25 = th1_run25[:,0:-1,:]

k_lst = [3,4,5,6,7,8,9,10]
N = 1200
th1_del = 0.0003924
num = 100
pc_num = 7
rep = 10

mld_training = np.zeros((rep,N))

for p in range(rep):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    th1_sam = np.concatenate((th1_run20[x_sam[0:N//6],:,z_sam[0:N//6]], th1_run21[x_sam[N//6:N//3],:,z_sam[N//6:N//3]], th1_run22[x_sam[N//3:N//2],:,z_sam[N//3:N//2]], th1_run23[x_sam[N//2:N//3*2],:,z_sam[N//2:N//3*2]], th1_run24[x_sam[N//3*2:N//6*5],:,z_sam[N//3*2:N//6*5]], th1_run25[x_sam[N//6*5:N],:,z_sam[N//6*5:N]]), axis=0)
    coord_new = np.linspace(-1,0,num=num)
    th1_mld = np.zeros((N,num))
    for i in range(N):
        prof = th1_sam[i,:]
        surf_val = prof[-1]
        ind = np.where(surf_val-prof<=th1_del)
        prof = prof[ind]
        prof_len = len(prof)
        mld_training[p,i] = prof_len*(800/256)
        coord_old = np.linspace(-1,0,num=prof_len)
        prof = np.interp(coord_new, coord_old, prof)
        th1_mld[i,:] = prof

    th1_mld_nml = np.zeros((N,num))
    th1_mean_training = np.zeros(N)
    for j in range(N):
        prof = th1_mld[j,:]
        avg = np.mean(prof)
        th1_mean_training[j] = avg
        prof = prof - avg
        th1_mld_nml[j,:] = prof
            
    th1_mld_nml_xr = xr.DataArray(th1_mld_nml, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
    for k in k_lst:
        ds = xr.Dataset({'TH1':th1_mld_nml_xr, 'X':x_sam, 'Z':z_sam})
        pcm_features = {'buoyancy': coord_new}
        features_in_ds = {'buoyancy': 'TH1'}
        features_zdim='COORD'
        m, ds = pf.training(k, pcm_features, features_in_ds, features_zdim, ds, pc_num=pc_num)
        m.to_netcdf('LES_MLD_NML_k{}_N{}_pc7_rep{}.nc'.format(k,N,p+1))
        print('Model N {} pc{} rep{} training done'.format(N,pc_num,p+1))

for k in [2,3,4,5,6,7,8,9,10]:
    for p in range(rep):
        modelname = 'LES_MLD_NML_k{}_N{}_pc7_rep{}'.format(k,N,p+1)
        filename = 'models/LES_MLD_NML/'+modelname+'.nc'
        m_loaded = pyxpcm.load_netcdf(filename)
        print(modelname)
        print(m_loaded)

# Calculate BIC scores from log-likelihood manually ('bic_calculation.xlsx') and plot BIC vs. k below
tnrfont = {'fontname':'Times New Roman'}
pc_num_lst = np.asarray([2,3,4,5,6,7,8,9,10])
bic_score = np.asarray([36889.96907,36522.69471,36372.45956,36303.09792,36276.10061,36253.70433,36252.23198,36245.12202,36254.95367])
fig, ax = plt.subplots(1,1, figsize=(8,6))
plt.plot(pc_num_lst,bic_score,marker='o')
ax.set_title('BIC Score vs. Number of Classes for LES Dataset (N=1200, PC=7)', fontsize=18, **tnrfont)
plt.xlabel('Number of Classes', fontsize=18, **tnrfont)
plt.xticks(fontsize=14, **tnrfont)
plt.ylabel('BIC Score', fontsize=18, **tnrfont)
plt.yticks(fontsize=14, **tnrfont)