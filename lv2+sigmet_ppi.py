import math
import pyart
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import warnings

print('1:Reflectivity, 2:Radial Velocity')
var = input('please input the variable you want to plot:')

#ignore warning
warnings.filterwarnings('ignore')

#loc is the path where you store your unzipped radar data
#des is the path where you want to store the radar figures you plot
loc=r'C:\Users\wfliu\Downloads\Radar data'
des=r'C:\Users\wfliu\Downloads\Radar data\figs'

for file in [r'\RCWF\20190809_0101_RCWF_VOL.239',r'\RCTP\TIA180710190009.RAW48V7']:
    #judge Level II or SIGMET
    if file.split('\\')[1] == 'RCWF':
        #decode data stored in radar object
        radar = pyart.io.read_nexrad_archive(loc+file)
        name = radar.metadata['instrument_name']
    elif file.split('\\')[1] == 'RCTP':
        #decode data stored in radar object
        radar = pyart.io.read_sigmet(loc+file)
        name = 'RCTP'
    display = pyart.graph.RadarMapDisplay(radar)

    #basic radar information
    lon = radar.longitude['data'][0]
    lat = radar.latitude['data'][0]

    for swp in range(radar.nsweeps):

        #Rmax
        stoprange = radar.instrument_parameters['unambiguous_range']['data'][0]/1000.
        dx = math.ceil(stoprange/100.)
        
        #first ray and its time and elevation in every sweep
        ray0 = radar.sweep_start_ray_index['data'][swp]
        time = str(pyart.util.datetimes_from_radar(radar)[ray0]).split(':')
        elev = radar.elevation['data'][ray0]
        
		#colorbar
        if var == '1':
            dataname = 'reflectivity'
            varname = 'Reflectivity'
            savename = 'dBZ'
            unit = 'dBZ'
            radcolors = [(0.70,0.70,0.70),(0.00,1.00,1.00),(0.00,0.75,1.00),(0.00,0.50,1.00),(0.00,0.70,0.30),(0.00,0.90,0.30),(1.00,1.00,0.00),(1.00,0.70,0.00),(1.00,0.00,0.00),(0.70,0.00,0.00),(0.81,0.34,0.64),(0.85,0.63,0.80)]
            clv = [0.,5.,10.,15.,20.,25.,30.,35.,40.,45.,50.,55.,60.]
        elif var == '2':
            dataname = 'velocity'
            varname = 'V$_r$'
            savename = 'V'
            unit = 'm s$^{-1}$'
            radcolors = [(0.50,0.00,1.00),(0.50,0.50,1.00),(0.00,0.70,0.30),(0.00,0.90,0.30),(0.50,1.00,0.50),(0.70,1.00,0.70),(0.90,0.90,0.90),(1.00,1.00,0.00),(1.00,0.70,0.00),(0.75,0.53,0.28),(0.63,0.44,0.35),(0.87,0.37,0.47),(0.94,0.27,0.42)]
            nyq_vel = radar.instrument_parameters['nyquist_velocity']['data'][ray0]
			#auto choosing colorbar range
            if round(nyq_vel/6.) <= 1:
                dc = 1
            elif round(nyq_vel/6.) > 1:
                dc = round(nyq_vel/6.)
            clv = np.linspace(-6.,-1.,6)*dc
            if dc <= 1:
                clv = np.append(clv,np.linspace(-0.5,0.5,2))
            elif dc > 1:
                clv = np.append(clv,np.linspace(-1.,1.,2))
            clv = np.append(clv,np.linspace(1.,6.,6)*dc)
            
        print('processing sweep '+str(swp+1)+' '+dataname+' data')    
            
        #start plot
        fig = plt.figure(figsize=(10,10))
        
        #colormap
        cmap = mpl.colors.ListedColormap(radcolors)
        cmap.set_over(radcolors[-1])
        cmap.set_under(radcolors[0])
        norm = mpl.colors.BoundaryNorm(clv,cmap.N)

		#map projection based on cartopy
        map_proj = ccrs.PlateCarree()

        #ppi plot in pyart, please check pyart for more introductions of these parameter
        display.plot_ppi_map(dataname, swp, fig=fig, ax=111, projection=map_proj, resolution='10m',
                             min_lon=round(lon)-dx, max_lon=round(lon)+dx, lon_lines=np.linspace(round(lon)-dx,round(lon)+dx,2*dx+1),
                             min_lat=round(lat)-dx, max_lat=round(lat)+dx,lat_lines=np.linspace(round(lat)-dx,round(lat)+dx,2*dx+1),
                             cmap=cmap, norm=norm, vmin=min(clv), vmax=min(clv), ticks=clv, colorbar_label=varname+' ('+unit+')',
                             title='{0} of {1} {2}:{3}:{4} UTC, elev={5:4.1f}$^o$'.format(varname,name,time[0],time[1],time[2],elev))

        #plt.show()
        plt.savefig(des+'\\'+name+'_'+time[0]+time[1]+time[2]+'_'+savename+'_'+str(swp+1)+'.png')