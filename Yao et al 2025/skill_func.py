# import libraries
import numpy as np
import pandas as pd
import xarray as xr
import h5py as h5
import pyxpcm
from pyxpcm.models import pcm
import matplotlib as mpl
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from scipy import ndimage
np.random.seed(256)
import pcm_func as pf

def pcm_pca_pred(modelname, eddyctr_class, eddyprp_lst, th1, depth, N, classnum):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    th1_sam = th1[x_sam,0:-1,z_sam]
    depth = depth[0:-1]
    m_loaded = pyxpcm.load_netcdf(modelname)
    th1_sam = xr.DataArray(th1_sam, dims=('N_PROF','DEPTH'), coords={'N_PROF':np.array(range(N)), 'DEPTH':depth})
    ds = xr.Dataset({'TH1':th1_sam, 'X':x_sam, 'Z':z_sam})
    features_in_ds = {'buoyancy': 'TH1'}
    features_zdim='DEPTH'
    m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    m_loaded.predict_proba(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, np.array(ds['PCM_LABELS']))).T, columns=['N_PROF', 'X', 'Z', 'CLASS'])
    if classnum==3.0:
        df['CLASS'][df['CLASS']==eddyctr_class]=100
        [temp1, temp2] = eddyprp_lst
        df['CLASS'][df['CLASS']==temp1]=200
        df['CLASS'][df['CLASS']==temp2]=200
        df['CLASS'][df['CLASS']<50]=50
    else:
        df['CLASS'][df['CLASS']==eddyctr_class]=150
        [temp1, temp2] = eddyprp_lst
        df['CLASS'][df['CLASS']==temp1]=150
        df['CLASS'][df['CLASS']==temp2]=150
        df['CLASS'][df['CLASS']<50]=50
    return df

def pcm_mld_pred_3(modelname, eddyctr_class, eddyprp_lst, th1, th1_del, num, N):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    th1_sam = th1[x_sam,0:-1,z_sam]
    coord_new = np.linspace(-1,0,num=num)
    th1_mld = np.zeros((N,num))
    for i in range(N):
        prof = th1_sam[i,:]
        surf_val = prof[-1]
        ind = np.where(surf_val-prof<=th1_del)
        prof = prof[ind]
        prof_len = len(prof)
        coord_old = np.linspace(-1,0,num=prof_len) 
        th1_mld[i,:] = np.interp(coord_new, coord_old, prof)
    m_loaded = pyxpcm.load_netcdf(modelname)
    th1_mld = xr.DataArray(th1_mld, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
    ds = xr.Dataset({'TH1':th1_mld, 'X':x_sam, 'Z':z_sam})
    features_in_ds = {'buoyancy': 'TH1'}
    features_zdim='COORD'
    m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    m_loaded.predict_proba(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, np.array(ds['PCM_LABELS']))).T, columns=['N_PROF', 'X', 'Z', 'CLASS'])
    df['CLASS'][df['CLASS']==eddyctr_class]=100
    [temp1, temp2] = eddyprp_lst
    df['CLASS'][df['CLASS']==temp1]=200
    df['CLASS'][df['CLASS']==temp2]=200
    df['CLASS'][df['CLASS']<50]=50
    return df

def pcm_mld_pred_2(modelname, eddy_class, th1, th1_del, num, N):
    x_sam, z_sam = pf.rand_coord(N, 1024)
    th1_sam = th1[x_sam,0:-1,z_sam]
    coord_new = np.linspace(-1,0,num=num)
    th1_mld = np.zeros((N,num))
    for i in range(N):
        prof = th1_sam[i,:]
        surf_val = prof[-1]
        ind = np.where(surf_val-prof<=th1_del)
        prof = prof[ind]
        prof_len = len(prof)
        coord_old = np.linspace(-1,0,num=prof_len) 
        th1_mld[i,:] = np.interp(coord_new, coord_old, prof)
    m_loaded = pyxpcm.load_netcdf(modelname)
    th1_mld = xr.DataArray(th1_mld, dims=('N_PROF','COORD'), coords={'N_PROF':np.array(range(N)), 'COORD':coord_new})
    ds = xr.Dataset({'TH1':th1_mld, 'X':x_sam, 'Z':z_sam})
    features_in_ds = {'buoyancy': 'TH1'}
    features_zdim='COORD'
    m_loaded.predict(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    m_loaded.predict_proba(ds, features=features_in_ds, dim=features_zdim, inplace=True)
    df = pd.DataFrame(np.stack((np.array(ds['N_PROF']), x_sam, z_sam, np.array(ds['PCM_LABELS']))).T, columns=['N_PROF', 'X', 'Z', 'CLASS'])
    for j in range(len(eddy_class)):
        df['CLASS'][df['CLASS']==eddy_class[j]]=150
    df['CLASS'][df['CLASS']<50]=50
    return df

#def moving_average(x):
    return np.convolve(x, np.ones(201), 'valid') / (201)

#def truth_label(vel_x, vel_z, classnum):
    vel_x = vel_x[:,-2,:]
    vel_z = vel_z[:,-2,:]
    n = 1024
    i_smt = np.append(np.append(np.arange(n-100,n), np.arange(n)), np.arange(100))
    vel_x_ext = vel_x[i_smt,:]
    vel_z_ext = vel_z[:,i_smt]
    vel_x_smt = np.apply_along_axis(moving_average,0,vel_x_ext)
    vel_z_smt = np.apply_along_axis(moving_average,1,vel_z_ext)
    h = 4000/(n-1)
    i_p = np.append(np.arange(1,n), 0)
    i_m = np.append(n-1, np.arange(n-1))
    vel_x_p = vel_x_smt[i_p,:]
    vel_x_m = vel_x_smt[i_m,:]
    vel_z_p = vel_z_smt[:,i_p]
    vel_z_m = vel_z_smt[:,i_m]
    vor = (-1/2/h)*(vel_x_p - vel_x_m - vel_z_p + vel_z_m)
    spd = np.sqrt(np.square(vel_x)+np.square(vel_z))
    label = np.zeros((n,n))
    if classnum==2:
        label[vor>=0.0001]=150
        label[vor<0.0001]=50
    else:
        label[np.logical_and(vor>=0.0001, spd>=0.1)]=200
        label[np.logical_and(vor>=0.0001, spd<0.1)]=100
        label[vor<0.0001]=50
    return label

def truth_label_conv(vel_x, vel_z, classnum):
    vel_x = vel_x[:,-2,:]
    vel_z = vel_z[:,-2,:]
    n = 1024
    h = 4000/(n-1)
    knl = np.ones((100,100))/100/100
    vel_x_smt = ndimage.convolve(vel_x, knl, mode='wrap')
    vel_z_smt = ndimage.convolve(vel_z, knl, mode='wrap')
    i_p = np.append(np.arange(1,n), 0)
    i_m = np.append(n-1, np.arange(n-1))
    vel_x_p = vel_x_smt[i_p,:]
    vel_x_m = vel_x_smt[i_m,:]
    vel_z_p = vel_z_smt[:,i_p]
    vel_z_m = vel_z_smt[:,i_m]
    vor = (-1/2/h)*(vel_x_p - vel_x_m - vel_z_p + vel_z_m)
    spd = np.sqrt(np.square(vel_x)+np.square(vel_z))
    label = np.zeros((n,n))
    if classnum==2:
        label[vor>=0.0001]=150
        label[vor<0.0001]=50
    else:
        label[np.logical_and(vor>=0.0001, spd>=0.1)]=200
        label[np.logical_and(vor>=0.0001, spd<0.1)]=100
        label[vor<0.0001]=50
    return label



