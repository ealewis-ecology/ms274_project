# import libraries
import numpy as np
import pandas as pd
import xarray as xr
import h5py as h5
from pyxpcm.models import pcm
import matplotlib as mpl
import matplotlib.pyplot as plt

def h5_to_nparray(filename, keyname):
    ''' 
        Extract data from hdf5 files and convert to numpy arrays:
            filename (string): name of hdf5 file
            keyname (list of strings): list of directories of datasets

        Return: list of numpy arrays corresponding to data in keyname
    '''
    hf = h5.File(filename,'r')
    nparray_lst = []
    for i in range(len(keyname)):
        temp = hf[keyname[i]]
        nparray_lst.append(np.array(temp))
    hf.close()
    return nparray_lst

def rand_coord(N, coord_range):
    '''
        Generate 2D coordinates:
            N (integer): number of coordinate pairs to generate
            coord_range (integer): range of possible coordinates

        Return: tuple containing two numpy arrays
    '''
    s = np.random.randint(coord_range, size=(2,N))
    xs = s[0,:]
    zs = s[1,:]
    return (xs, zs)

def training(k, pcm_features, features_in_ds, features_zdim, dataset, pc_num=0):
    '''
        Create, fit, and predict PCM model:
            k (integer): number of classes
            pcm_features: dictionary defining features and corresponding dimensions
            features_in_ds: dictionary defining features and corresponding data in dataset
            featues_zdim: dictionary defining z dimension
            dataset: xarray dataset containing training data and output results
            pc_num: number of principle components to use in PCA (do not use PCA if 0)

        Return: tuple containing trained model and original dataset with prediction results
    '''
    if pc_num == 0:
        m = pcm(K=k, features=pcm_features)
    else: 
        m = pcm(K=k, features=pcm_features, maxvar=pc_num)
    m.fit(dataset, features=features_in_ds, dim=features_zdim)
    m.predict(dataset, features=features_in_ds, dim=features_zdim, inplace=True)
    m.predict_proba(dataset, features=features_in_ds, dim=features_zdim, inplace=True)
    return (m, dataset)

def plots(m, ds, k, x_sam, z_sam):
    '''
        Generate plots for trained PCM model:
            m: trained PCM model
            ds: dataset containing training data and prediction results
            k: number of classes
            x_sam: x coordinates for randomly selected points
            z_sam: z coordinates for randomly selected points

        Return: tuple containing handles for two plots: (1) mean/std for classes (2) clustering
    '''
    for vname in ['TH1']:
        ds = ds.pyxpcm.quantile(m, q=[0.05, 0.5, 0.95], of=vname, outname=vname + '_Q', keep_attrs=True, inplace=True)
    fig1, ax1 = m.plot.quantile(ds['TH1_Q'], maxcols=4, figsize=(10, 8), sharey=True)
    fig2, ax2 = plt.subplots(1,1, figsize=(8,6))
    tag = ds['PCM_LABELS'] # Tag each point with a corresponding label    
    cmap = plt.cm.jet
    cmaplist = [cmap(i) for i in range(cmap.N)]
    cmap = cmap.from_list('Custom cmap', cmaplist, cmap.N)
    bounds = np.linspace(0,k,k+1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    scat1 = ax2.scatter(x_sam,z_sam,c=tag,cmap=cmap, norm=norm)
    cb = plt.colorbar(scat1, spacing='proportional',ticks=bounds)
    return (fig1, ax1, fig2, ax2)

