# Train PCMs on LES dataset with varying parameters (k, N_train, N_pc)
# Calculate and save skill scores (accuracy, precision, recall, F-1) for trained PCMs

# import libraries
import numpy as np
import pandas as pd
import xarray as xr
from pyxpcm.models import pcm
import pyxpcm
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib import colors
from sklearn.decomposition import PCA
import scipy.io as spio
from scipy import ndimage
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import h5py as h5

mpl.rc('font',family='Times New Roman')
np.random.seed(257)

import pcm_func as pf
import skill_func as sf

tnrfont = {'fontname':'Times New Roman'}

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

k = 2
N = 1200
th1_del = 0.0003924
num = 100
PC_lst=np.asarray([1,2,3,4,5,6,7,8,9,10])
rep = 10

x_sam_training = np.zeros((rep,N))
z_sam_training = np.zeros((rep,N))
mld_training = np.zeros((rep,N))
class_training = np.zeros((rep*len(PC_lst),N))

pc_num = 10
expl_var = np.zeros(10)
for p in range(rep):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    x_sam_training[p,:] = x_sam
    z_sam_training[p,:] = z_sam
    th1_sam = np.concatenate((th1_run20[x_sam[0:N//6],:,z_sam[0:N//6]], th1_run21[x_sam[N//6:N//3],:,z_sam[N//6:N//3]], th1_run22[x_sam[N//3:N//2],:,z_sam[N//3:N//2]], th1_run23[x_sam[N//2:N//3*2],:,z_sam[N//2:N//3*2]], th1_run24[x_sam[N//3*2:N//6*5],:,z_sam[N//3*2:N//6*5]], th1_run25[x_sam[N//6*5:N],:,z_sam[N//6*5:N]]), axis=0)
    pca = PCA(n_components=pc_num)
    pcs = pca.fit_transform(th1_sam)
    expl_var += pca.explained_variance_ratio_

for p in range(rep):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    x_sam_training[p,:] = x_sam
    z_sam_training[p,:] = z_sam
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
        th1_mld = xr.DataArray(th1_mld, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
    for r in range(len(PC_lst)):
        ds = xr.Dataset({'TH1':th1_mld, 'X':x_sam, 'Z':z_sam})
        pc_num = PC_lst[r]
        pcm_features = {'buoyancy': coord_new}
        features_in_ds = {'buoyancy': 'TH1'}
        features_zdim='COORD'
        m, ds = pf.training(k, pcm_features, features_in_ds, features_zdim, ds, pc_num=pc_num)
        m.to_netcdf('k2_N120_pc{}_rep{}.nc'.format(pc_num,p+1))
        class_training[p*len(PC_lst)+r,:]=np.asarray(ds['PCM_LABELS'])
        print('Model pc{} rep{} training done'.format(pc_num,p))

df = pd.DataFrame(np.concatenate((x_sam_training, np.zeros((1,N)), z_sam_training, np.zeros((1,N)), mld_training, np.zeros((1,N)), class_training),axis=0))
writer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='sheet1')
writer.save()

eddy_class_training = np.zeros((rep*len(PC_lst),N))
for p in range(rep):
    for r in range(len(PC_lst)):
        classes = class_training[p*len(PC_lst)+r,:]
        class0_ind = (classes==0)
        class1_ind = (classes==1)
        class0_mld = np.mean(mld_training[p,class0_ind])
        class1_mld = np.mean(mld_training[p,class1_ind])
        if class0_mld<=class1_mld:
            eddy_class_training[p*len(PC_lst)+r,class0_ind]=1
            eddy_class_training[p*len(PC_lst)+r,class1_ind]=0
        else:
            eddy_class_training[p*len(PC_lst)+r,class0_ind]=0
            eddy_class_training[p*len(PC_lst)+r,class1_ind]=1

df = pd.DataFrame(eddy_class_training)
writer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='sheet1')
writer.save()

skill_stat = np.zeros((rep*len(PC_lst),4))

for p in range(rep):
    for r in range(len(PC_lst)):
        pc_num = PC_lst[r]
        modelname = 'k2_N120_pc{}_rep{}'.format(pc_num,p+1)
        classnum = 2
        data_lst = ['run20','run21','run22','run23','run24','run25']
        filename = 'k2_N1200_models/'+modelname+'.nc'
        N = 10000
        precision = 0
        recall = 0
        f1 = 0
        accuracy = 0

        for i in list(range(len(data_lst))):
            mld_testing = np.zeros(N)
            dataname = data_lst[i]
            print('Running model {} on {}...'.format(modelname, dataname))
            [th1, vel_x, vel_z] = pf.h5_to_nparray('data/end_{}.h5'.format(dataname), ['Timestep/TH1','Timestep/U','Timestep/W'])
            x_sam, z_sam = pf.rand_coord(N, 1024)
            th1_sam = th1[x_sam,0:-1,z_sam]
            coord_new = np.linspace(-1,0,num=num)
            th1_mld = np.zeros((N,num))
            for g in range(N):
                prof = th1_sam[g,:]
                surf_val = prof[-1]
                ind = np.where(surf_val-prof<=th1_del)
                prof = prof[ind]
                prof_len = len(prof)
                mld_testing[g] = prof_len*(800/256)
                coord_old = np.linspace(-1,0,num=prof_len) 
                th1_mld[g,:] = np.interp(coord_new, coord_old, prof)
            m_loaded = pyxpcm.load_netcdf(filename)
            th1_mld = xr.DataArray(th1_mld, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
            ds = xr.Dataset({'TH1':th1_mld, 'X':x_sam, 'Z':z_sam})
            features_in_ds = {'buoyancy': 'TH1'}
            features_zdim='COORD'
            m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
            df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, mld_testing, np.array(ds['PCM_LABELS']), np.zeros(N))).T, columns=['N_PROF', 'X', 'Z', 'MLD', 'CLASS', 'EDDY'])
            class0_ind = (df['CLASS']==0)
            class1_ind = (df['CLASS']==1)
            class0_mld = np.mean(df['MLD'][class0_ind])
            class1_mld = np.mean(df['MLD'][class1_ind])
            if class0_mld<=class1_mld:
                df['EDDY'][class0_ind]=150
                df['EDDY'][class1_ind]=50
            else:
                df['EDDY'][class0_ind]=50
                df['EDDY'][class1_ind]=150

            truth_label = sf.truth_label(vel_x, vel_z, classnum)
            pred = df['EDDY']
            truth = truth_label[x_sam, z_sam]
            accuracy += accuracy_score(truth, pred)
            f1 += f1_score(truth, pred, average='weighted')
            precision += precision_score(truth, pred, average='weighted')
            recall += recall_score(truth, pred, average='weighted')
        skill_stat[p*len(PC_lst)+r,0] = precision/len(data_lst)
        skill_stat[p*len(PC_lst)+r,1] = recall/len(data_lst)
        skill_stat[p*len(PC_lst)+r,2] = f1/len(data_lst)
        skill_stat[p*len(PC_lst)+r,3] = accuracy/len(data_lst)

df = pd.DataFrame(skill_stat, columns=['Precision', 'Recall', 'F1-score', 'Accuracy'])
writer = pd.ExcelWriter('temp.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='sheet1')
writer.save()