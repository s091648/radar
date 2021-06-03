import pyart
import matplotlib as mpl
import matplotlib.pyplot as plt

#loc is the path where you store your unzipped radar data
#des is the path where you want to store the radar figures you plot
loc=r'C:\Users\wfliu\Downloads\Radar data'
des=r'C:\Users\wfliu\Downloads\Radar data\figs'

angle = [0,90,180,270]
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
    xsect = pyart.util.cross_section_ppi(radar,angle)
    display = pyart.graph.RadarDisplay(xsect)
    
    #colormap
    radcolors = [(0.70,0.70,0.70),(0.00,1.00,1.00),(0.00,0.75,1.00),(0.00,0.50,1.00),(0.00,0.70,0.30),(0.00,0.90,0.30),(1.00,1.00,0.00),(1.00,0.70,0.00),(1.00,0.00,0.00),(0.70,0.00,0.00),(0.81,0.34,0.64),(0.85,0.63,0.80)]
    clv = [0.,5.,10.,15.,20.,25.,30.,35.,40.,45.,50.,55.,60.]
    cmap = mpl.colors.ListedColormap(radcolors)
    cmap.set_over(radcolors[-1])
    cmap.set_under(radcolors[0])
    norm = mpl.colors.BoundaryNorm(clv,cmap.N)
    
    for ang in range(len(angle)):
        
        #start plot
        fig = plt.figure(figsize=(10,10))

        #plot cross section
        display.plot('reflectivity', ang, fig=fig, cmap=cmap, norm=norm, vmin=min(clv), vmax=max(clv), ticks=clv, colorbar_label='reflectivity (dBZ)', axislabels=('Distance (km)','Altitude (km)'), title=name+' reflectivity cross section at '+str(angle[ang])+'degrees')
        display.set_limits(xlim=(0,50),ylim=(0,10))

        #plt.show()
        plt.savefig(des+'\\'+name+str(angle[ang])+'_dBZ_cross_section.png')
        plt.close()