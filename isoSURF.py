# %%===========================================================================
# Import Libraries
# =============================================================================

import vtk
from paraview.simple import *
from vtk.numpy_interface import dataset_adapter as dsa
from netCDF4 import Dataset
from main_functions import *
import numpy as np
import time
import os.path
#from mpi4python import MPI

# %%===========================================================================
# User Settings
# =============================================================================

# Init MPI
#comm = MPI.COMM_WORLD
#rank = comm.Get_rank()
#size = comm.Get_size()

# Plugins Directory
plugin_dir = f'/linkhome/rech/genlfl01/upa47zs/ParaView_isoSURF'

# Data and Grids Directory
data_dir = f'/gpfswork/rech/avl/upa47zs/enstrophy_data'
grid_dir = f'/gpfswork/rech/avl/upa47zs/enstrophy_data'

casenm  = data_dir.split('/')[-1]
print('\n Case name:',casenm)

# Data and Grids file names
data_fname = f'ENSTROPHY_FIELD-030.nc'
grid_fname = f'GRID.nc'

# Image directory and name
imag_dir = f'/gpfsscratch/rech/avl/upa47zs/figs'
imag_name = f'test_image.png'

# Fields to Load from netcdf as they appear in the netcdf file
# If we want a grid coordinate to load as a scalar variable add to the list
# 'x','y', or 'z'
fields = 'enstrophy,y'

# Grids variables names as they appear in the netcdf file
grid_var_names = 'gridx,gridy,gridz'

# Size of fields to load (nx,ny,nz)
nx = 1024
ny = 1024
nz = 1024


# Read Grid file - no changes needed
# ------------
f = Dataset(f'{grid_dir}/{grid_fname}', 'r')
x = f.variables[grid_var_names.split(',')[0]][:nx]
y = f.variables[grid_var_names.split(',')[1]][:ny]
z = f.variables[grid_var_names.split(',')[2]][:nz]
f.close()
del f
# ------------

# Time evolution settings
nt = 13        # number of saved timesteps
istart = 24   # Iteration number of first saved time step
istep = 2     # Number of iterations per saved time step

# Isosurface Settings.
# For multiple isosurfaces just add entries to all the  corresponding arrays.
isosurface_fields = ['enstrophy']

variable_isovalue = True  # True: time varying isovalue False: constant isovalue given below  
isovalue=[0.001*100.] 
# fraction of the max value of variable at a given instant to calcul isovalue
frac_th  = 0.0001 

scalar_to_color = ['y'] # Scalar field to color the isosurface, if we want solid color put ''

# Colormap
cmap = ['seismic']
cmap_min = [y[0]/2.]  # min value color
cmap_max = [y[-1]/2.] # max value color

solid_color = [[68/255.,107/255.,242/255.],[0,0,0]] # Solid color in RGB

# Create a plane for bottom wall(0: False, 1: True)
wall = 0

# Camera Settings
resolution = [1280,720] # Image resolution

# Adjust Camera position with respect to grid coordinates
# CameraPosition = (x[0]*cx, y[-1]*cy, z[-1]*cz)
cx = 2
cy = 1
cz = 1

# Camera Parallel Scale - Zoom in/out
# Distance from focal point to edge of viewport(?)
cps = 1.1* y[-1] # smaller values -> zoom in !! bigger -> zoom out

# Enable raytracing, change value to 1 for raytracing rendering
raytracing = 1


# %%===========================================================================
# Main Program
# =============================================================================
if __name__ == '__main__':

    total_time_start = time.process_time() # Total program exec time start
    missingfl = [] # list for missing file names
    # Load Plugins
    LoadPlugin(f'{plugin_dir}/netcdfSource.py', ns=globals())

    for it in range(nt):

        iter_time_start = time.process_time() # Total program exec time start
        print('\n Iteration =',it)
        # If multiple time steps change the name of netcdf file to open
        # and the name of image to be saved
        if (nt > 1):
            int2char = str(it*istep+istart).zfill(3) # ID of file to open
            data_fname = f'ENSTROPHY_FIELD-{int2char}.nc'
            print('\n Data name: '+data_fname)
            imag_name = f'{casenm}_{int2char}.png'

        # Compute Bounds of Grid
        startx,starty,startz,midx,midy,midz,endx,endy,endz = compute_bounds(x,y,z)

        renderView1 = setup_render_view(startx,midx,midy,endy,midz,endz,
                                        cx,cy,cz,cps,resolution,raytracing)

        print('\n Opening '+data_dir+'/'+data_fname)
        if os.path.isfile(f'{data_dir}/{data_fname}') == False:
            print('\n File does not exist!')
            missingfl.append(data_fname)
            continue
        # create a new 'netcdf Source'
        netcdfSource1 = netcdfSource(DataFileName=f'{data_dir}/{data_fname}',
                                    GridFileName=f'{grid_dir}/{grid_fname}')

        netcdfSource1.FieldsToLoad = fields
        netcdfSource1.VariableNameOfGridsInNetcdfFile = grid_var_names
        netcdfSource1.nx = nx
        netcdfSource1.ny = ny
        netcdfSource1.nz = nz
        if variable_isovalue == True:
            # Get local min / max for time dependent isosurface value
            type(netcdfSource1.PointData.GetArray(isosurface_fields[0]))
            data_min,data_max = netcdfSource1.PointData.GetArray(isosurface_fields[0]).GetRange()
            global_max = data_max #0.
            #print('RANK:',rank,'Field min=',data_min,'Field max=',data_max,'Global_max=',global_max)
            #cg = vtk.vtkMultiProcessController.GetGlobalController()
            #rank = cg.GetLocalProcessId()
            #cg.AllGatherV(data_max,global_max)
            #comm.Allreduce(data_max,op=MPI.MAX) # mpi4python
            print('\n Field min=',data_min,'Field max=',data_max)#,'Global_max=',global_max)
            print('\n Global max=', global_max)
            print('\n Isovalue taken as the %7.4f the global maximum value.'%(frac_th))
            isovalue = [frac_th*global_max]

        # Create Isosurfaces
        contour=[]
        contourDisplay=[]
        for iS in range(len(isosurface_fields)):
            contour.append(Contour(Input=netcdfSource1))
            contourDisplay.append(Show(contour[iS], renderView1,
                                       'GeometryRepresentation'))
            contourDisplay[iS].UseSeparateColorMap = True
            contour[iS].ContourBy = ['POINTS', isosurface_fields[iS]]
            contour[iS].Isosurfaces = [isovalue[iS]]
            contour[iS].PointMergeMethod = 'Uniform Binning'

            # Settings for Isosurface
            isosurface_settings(contour[iS], contourDisplay[iS],
                                renderView1, isosurface_fields[iS],
                                scalar_to_color[iS], cmap[iS], cmap_min[iS],
                                cmap_max[iS], solid_color[iS], raytracing)

            contour[iS].UpdatePipeline()

        # create a new 'Plane'
        if wall:
            plane1 = Plane()
            plane1.Origin = [x[0], y[0], z[0]]
            plane1.Point1 = [x[0], y[0], z[-1]]
            plane1.Point2 = [x[-1], y[0], z[0]]

            plane_settings(plane1, renderView1)


        SetActiveSource(contour[0])

        # Save Screenshot
        SaveScreenshot(f'{imag_dir}/{imag_name}',ImageResolution=(resolution[0],
                                                                resolution[1]),
                        TransparentBackground = 1,
                        CompressionLevel = 0)

        # If multiple time steps need to be opened
        # reset session to open new files
        if nt>1:
            Disconnect()
            Connect()
        iter_time_end = time.process_time()
        iter_time = iter_time_end - iter_time_start
        print('\n Iteration time = %6.2f seconds (%4.1f minutes).' %(iter_time,(iter_time/60.)))

    if len(missingfl) != 0:
        print('There are missing files, so the corresponding figures are not drawn;')
        for i in range(len(missingfl)):
            print(missingfl[i])
    print('\nPROGRAM FINISHED!')
    total_time_end = time.process_time()
    total_time = total_time_end - total_time_start
    print('\n Total runtime time = %6.2f seconds (%4.1f minutes).' %(total_time,(total_time/60.)))

