#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 19:59:40 2023

@author: douglas
"""
import netCDF4 as nc
from wrf import getvar, to_np, get_cartopy, latlon_coords,interplevel
import matplotlib.pyplot as plt
import cartopy, cartopy.crs as ccrs        # Plot maps
import cartopy.io.shapereader as shpreader # Import shapefiles
import numpy as np
import cartopy.crs as crs
import bokeh
from bokeh.palettes import Spectral
import matplotlib

file = 'wrf_output'

# Open the WRF output file using netCDF4
wrf_file = nc.Dataset(file, 'r')

# Extract the variables
precipitable_water = getvar(wrf_file, "pw")
temp = getvar(wrf_file, "T2")
temperatura=getvar(wrf_file,"tc")
p = getvar(wrf_file, "pressure")
gpt = getvar(wrf_file, "z")
ua = getvar(wrf_file, "ua", units="m s-1")
va = getvar(wrf_file, "va", units="m s-1")

T_700 = interplevel(temperatura, p, 700)

u_700 = interplevel(ua, p, 700)
v_700 = interplevel(va, p, 700)

geopt_500 = interplevel(gpt , p, 500)

# Get the latitude and longitude coordinates
lats, lons = latlon_coords(precipitable_water)

plt.figure(figsize=(20,15))
ax = plt.axes(projection=ccrs.PlateCarree())

# Define de contour interval
data_min = 30
data_max = 65
interval = 5
levels = np.arange(data_min,data_max + interval,interval)

# Using Spectral 07 (Bokeh library)

colors = ['#3288bd', '#99d594', '#e6f598', '#ffffbf', '#fee08b', '#fc8d59', '#d53e4f']
cmap = matplotlib.colors.ListedColormap(colors)
cmap.set_over('#000000')
cmap.set_under('#ffffff')

# Plot the precipitable water variable
cs = ax.contourf(to_np(lons), to_np(lats), to_np(precipitable_water),levels=levels, cmap=cmap)

# Add a shapefile
# https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
shapefile = list(shpreader.Reader('shapefile/BRMUE250GC_SIR.shp').geometries())
ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='black',facecolor='none', linewidth=0.5)
        
# Add coastlines, borders and gridlines
#ax.coastlines(resolution='10m', color='black', linewidth=0.8)
#ax.add_feature(cartopy.feature.BORDERS, edgecolor='black', linewidth=0.5)
gl = ax.gridlines(crs=ccrs.PlateCarree(), color='black', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
gl.top_labels = False
gl.right_labels = False

# Add a colorbar
cbar = plt.colorbar(cs,label='Água Precipitável (mm)',pad=0.045, fraction=0.045,extend='max',orientation='horizontal')

# Define de contour interval
data_min = 4900
data_max = 5900
interval = 20
levels = np.arange(data_min,data_max + interval,interval)

# Add the 500 hPa geopotential height contours
contours = plt.contour(to_np(lons), to_np(lats), to_np(geopt_500), colors="black",
                       levels=levels,transform=crs.PlateCarree())
ax.clabel(contours, inline=1, inline_spacing=0, fontsize='10',fmt = '%1.0f')

# Plot the temperature variable
cs = ax.contour(to_np(lons), to_np(lats), to_np(T_700), cmap='Reds', linestyles='dashed')
ax.clabel(cs, inline=1, inline_spacing=0, fontsize='10',fmt = '%1.0f')

# Add the 500 hPa wind barbs, only plotting every 125th data point.
plt.barbs(to_np(lons[::6,::6]), to_np(lats[::6,::6]),
          to_np(u_700[::6,::6]), to_np(v_700[::6,::6]),
          transform=crs.PlateCarree(), length=6)

plt.title(' Água Precipitável (mm, sombreado) \n Temperatura em 700 hPa (°C, vermelho) \n Altura geopotencial 500 hPa (dam,preto) \n vento em 700 hPa (m/s, barbela)' , fontsize=12, loc='left')
plt.title('' + ((file.split('/')[-1]).split('_')[2])+' '+((file.split('/')[-1]).split('_')[-1]), fontsize=12, loc='right')
plt.savefig('figure1.png',bbox_inches='tight', pad_inches=0, dpi=300)
plt.show()


