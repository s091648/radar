import numpy as np
import wradlib as wrl
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import warnings

#ignore warnings
warnings.filterwarnings('ignore')

#loc is the path where you store your unzipped radar data
#des is the path where you want to store the radar figures you plot
loc=r'C:\Users\wfliu\Downloads\Radar data'
des=r'C:\Users\wfliu\Downloads\Radar data\figs'

for file in [r'\2019080816001800dBZ.vol',r'\2019080816001800V.vol']:
    #decoded data is stored in rbdict
    rbdict = wrl.io.read_rainbow(loc+file)
    #read in basic one-time info
    alt = float(rbdict['volume']['radarinfo']['@alt'])
    lon = float(rbdict['volume']['radarinfo']['@lon'])
    lat = float(rbdict['volume']['radarinfo']['@lat'])
    name = rbdict['volume']['radarinfo']['name']
    #how many elevations
    numele = int(rbdict['volume']['scan']['pargroup']['numele'])
    # where data in different elevations locate
    slices = rbdict['volume']['scan']['slice']
    #Rmax
    stoprange = float(slices[0]['stoprange'])
    #number of radial data gates
    bin0 = float(slices[0]['slicedata']['rawdata']['@bins'])
    #azimuthal resolution
    azires = float(slices[0]['anglestep'])
    site = (lon,lat,alt)
    dx = round(stoprange/100.)
    
    #read data from every elevations
    for numslice in range(numele):
        
        #time information
        time = slices[numslice]['slicedata']['@time'].split(":")
        date = slices[numslice]['slicedata']['@date']
        
        #how many data gates in the radial direction
        bins = float(slices[numslice]['slicedata']['rawdata']['@bins'])
        
        #check bin numbers again for CDX mode in upper level
        if bins != bin0: 
            stoprange = float(slices[numslice]['stoprange'])
            
        #elevation in degrees
        elev = float(slices[numslice]['posangle'])

        #which field
        var = slices[numslice]['slicedata']['rawdata']['@type']
        dmin = float(slices[numslice]['slicedata']['rawdata']['@min'])
        
        #radial space gating
        dr = float(slices[numslice]['rangestep'])
        r = np.arange(0,stoprange,dr)
        
        #azimuthal data
        azirange = float(slices[numslice]['slicedata']['rayinfo']['@rays'])
        azidepth = float(slices[numslice]['slicedata']['rayinfo']['@depth'])
        azi = slices[numslice]['slicedata']['rayinfo']['data']
        azi = (azi*azirange/2**azidepth)*azires
        
        #radar data
        data = slices[numslice]['slicedata']['rawdata']['data']
        datadepth = float(slices[numslice]['slicedata']['rawdata']['@depth'])
        datamin = float(slices[numslice]['slicedata']['rawdata']['@min'])
        datamax = float(slices[numslice]['slicedata']['rawdata']['@max'])
        data = datamin+data*(datamax-datamin)/2**datadepth
        
        print('processing '+str(elev)+' degree elevation of '+name+' radar '+var+' data at '+date+' '+time[0]+':'+time[1])
        
        #colorbar and name settings for different data
        if var == 'dBZ':
            varname = 'Reflectivity'
            unit = 'dBZ'
            radcolors = [(0.70,0.70,0.70),(0.70,0.70,0.70),(0.00,1.00,1.00),(0.00,0.75,1.00),(0.00,0.50,1.00),(0.00,0.70,0.30),(0.00,0.90,0.30),(1.00,1.00,0.00),(1.00,0.70,0.00),(1.00,0.00,0.00),(0.70,0.00,0.00),(0.81,0.34,0.64),(0.85,0.63,0.80)]
            #mask out dBZ<0
            data = np.ma.masked_less(data,0.)
            clv = [0.,5.,10.,15.,20.,25.,30.,35.,40.,45.,50.,55.,60.]
        elif var == 'V':
            varname = 'V$_r$'
            unit = 'm s$^{-1}$'
            radcolors = [(0.50,0.00,1.00),(0.50,0.50,1.00),(0.00,0.70,0.30),(0.00,0.90,0.30),(0.50,1.00,0.50),(0.70,1.00,0.70),(0.90,0.90,0.90),(1.00,1.00,0.00),(1.00,0.70,0.00),(0.75,0.53,0.28),(0.63,0.44,0.35),(0.87,0.37,0.47),(0.94,0.27,0.42)]
            #mask out Vr<=dmin
            data = np.ma.masked_less_equal(data,dmin)
            dmin2 = abs(np.nanmin(data))
            #auto choosing colorbar range
            if round(dmin2/6.) <= 1:
                dc = 1
            elif round(dmin2/6.) > 1:
                dc = round(dmin2/6.)
            clv = np.linspace(-6.,-1.,6)*dc
            if dc <= 1:
                clv = np.append(clv,np.linspace(-0.5,0.5,2))
            elif dc > 1:
                clv = np.append(clv,np.linspace(-1.,1.,2))
            clv = np.append(clv,np.linspace(1.,6.,6)*dc)
            
        #start plot
        fig = plt.figure(figsize=(10,10))
        
        #colormap
        cmap = mpl.colors.ListedColormap(radcolors)
        cmap.set_over(radcolors[-1])
        cmap.set_under(radcolors[0])
        norm = mpl.colors.BoundaryNorm(clv,cmap.N)
        
        #map projection based on cartopy
        map_proj = ccrs.Mercator(central_longitude=round(site[0]))
        
        #ppi plot in wradlib, please check wradlib for more introductions of these parameters
        cgax,pm = wrl.vis.plot_ppi(data, r=r*1000., az=azi, elev=elev, fig=fig, site=site, proj=map_proj, cmap=cmap,norm=norm, vmin=min(clv), vmax=max(clv), extend='both')
        
        #coastlines, gridlines, and domain size
        cgax.coastlines()
        cgax.set_extent([round(site[0])-dx,round(site[0])+dx,round(site[1])-dx,round(site[1])+dx])
        gl = cgax.gridlines(crs=ccrs.PlateCarree(),draw_labels=True,xlocs=(np.linspace(round(site[0])-dx,round(site[0])+dx,2*dx+1)),ylocs=(np.linspace(round(site[1])-dx,round(site[1])+dx,2*dx+1)))
        gl.xlabels_top = False
        gl.ylabels_right = False
        
        #labels
        cgax.set_xlabel('Longitude (degrees)')
        cgax.set_ylabel('Latitude (degrees)')
        
        #titles
        title = '{0} of {1} {2} {3} UTC, elev={4}$^o$'.format(varname,name,date,time,elev)
        plt.title(title,fontsize=12)
        
        #colorbar
        cbar = plt.gcf().colorbar(pm,ticks=clv,pad=0.075)
        cbar.set_label(varname+' ('+unit+')')
        
        #figure save
        #plt.show()
        plt.savefig(des+'\\'+name+'_'+date+'_'+time[0]+time[1]+time[2]+'_'+'elev'+str(elev)+'_'+var+'.png')
        plt.close()
