# MLML MS 274 Class Project

## Abstract
    This project seeks to validate a ROMS model for biological use in my thesis, testing the relationship between DO (and spice) by species in sebastes larvae. In order to validate the ROMS model, I will compare CTD casts to the the ROMS modeled Spice and DO at a depth band of aproximately 50m. However, CTD casts can be influenced by local conditions that a ROMS modeled coarse resolution may not show, like submesoscale eddies. This project seeks to validate that these local factors are or are not affecting an individual CTD cast, and also compare the ROMS modeled SST and SSS.
### Objectives
1.	Identify submesoscale eddies based on satellite-derived data wind, temperature and salinity data
2.	Identify CTD casts that may be influenced by these submesoscale eddies, and discard them from comparison of the ROMS model
3.	Compare accepted CTD casts with the ROMS model to establish DO/spice modeling quality
4.  Compare SSS and SST with the ROMS model to see how close/far they match up.

## Project Outline
### Datasets
- CalCOFI CTD casts with temperature, salinity and dissolved oxygen, 1998-2016
- Vokhshoori et al 2024 ROMS model outputs for DO, and spice
- Satellite Data:
    - SST: NASA MUR
    - SSS: SMOS (2009-2016)
    - Wind: SSM/I    
### Figures
1. Model Data Difference: Time series of Standard Error of SST and SSS over study area over time
### Overall Approach