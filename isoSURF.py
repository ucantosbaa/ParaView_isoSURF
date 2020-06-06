# %%===========================================================================
# Import Libraries
# =============================================================================

import vtk
from paraview.simple import *
from vtk.numpy_interface import dataset_adapter as dsa
from netCDF4 import Dataset
import sys
sys.path.insert(1, '/home/argyris/PhD/scripts/post_process/modules')
sys.path.insert(1, 'modules')
from case_mod import *
sys.path.insert(1, '.')
from main_functions import *
import numpy as np

# Init re550 Case parameters

re550   = Case(550, nu=1./(0.1118e5),
                nx=2048, ny=301, nz=2048, nt=300,
                dx=0.01227, dz=0.006136, dt_s=0.0037, iout=50,
                case='')
# %%===========================================================================
# User Settings
# =============================================================================

# Plugins Directory
plugin_dir = f'/home/argyris/PhD/scripts/post_process/ParaView_isoSURF'

# Data and Grids Directory
data_dir = f'/home/argyris/PhD/TCF/Re550/data'
grid_dir = data_dir

# Data and Grids file names
data_fname = f're550_Tr_Ty_ISF_Dis_duidui_rxryrz.nc'
grid_fname = data_fname

# Image directory and name
imag_dir = f'/home/argyris/PhD/TCF/Re550/figures/KHMH_rxryrz/Tr_rxryrz_iso'

# Fields to Load from netcdf as they appear in the netcdf file
# If we want a grid coordinate to load as a scalar variable add to the list
# 'x','y', or 'z'
fields = 'Tr'

# Grids variables names as they appear in the netcdf file
grid_var_names = 'grid_rx,grid_ry,grid_rz'

# Size of fields to load (nx,ny,nz)
nx = 51
ny = 101
nz = 101

nyp = 301

# Read Grid file - no changes needed
# ------------
f = Dataset(f'{grid_dir}/{grid_fname}', 'r')
x = f.variables[grid_var_names.split(',')[0]][:nx]/re550.delta_nu
y = f.variables[grid_var_names.split(',')[1]][:ny]/re550.delta_nu
z = f.variables[grid_var_names.split(',')[2]][:nz]/re550.delta_nu
yp = f.variables['grid_y'][:nyp]/re550.delta_nu
f.close()
del f
# ------------

# Time evolution settings
nt = 300          # number of saved timesteps
istart = 2200   # Iteration number of first saved time step
istep = 50      # Number of iterations per saved time step


# Isosurface Settings.
# For multiple isosurfaces just add entries to all the  corresponding arrays.
isosurface_fields = ['Tr']*15
isovalue = np.linspace(-0.2,0.1,15).tolist()
# isovalue_2 = np.linspace(-0.05,0.05,15).tolist()
# isovalue_3 = np.linspace(-0.02,0.01,15).tolist()
scalar_to_color = ['Tr']*15 # Scalar field to color the isosurface, if we want solid color put ''

# Colormap
cmap = ['BuRd']*15
cmap_min = [-0.03]*15  # min value color
cmap_max = [0.03]*15 # max value color

solid_color = [[68/255.,107/255.,242/255.]]*15# Solid color in RGB

# Create a plane for bottom wall(0: False, 1: True)
wall = 1

# Camera Settings
resolution = [1280,720] # Image resolution

# Adjust Camera position with respect to grid coordinates
# CameraPosition = (x[0]*cx, y[-1]*cy, z[-1]*cz)
cx = -1
cy = 0.7
cz = -0.5

# Camera Parallel Scale - Zoom in/out
# Distance from focal point to edge of viewport(?)
cps = 0.6 * y[-1] # smaller values -> zoom in !! bigger -> zoom out

# Enable raytracing, change value to 1 for raytracing rendering
raytracing = 0


# %%===========================================================================
# Main Program
# =============================================================================
if __name__ == '__main__':

    # Load Plugins
    LoadPlugin(f'{plugin_dir}/netcdfSource.py', ns=globals())

    for iy in range(1,90):

        if ( iy % 30 == 0 ):
            isovalue[:] = [x / 2 for x in isovalue]

        imag_name = f'Tr_rxryrz_{iy}.png'

        # Compute Bounds of Grid
        startx,starty,startz,midx,midy,midz,endx,endy,endz = compute_bounds(x,y,z)

        renderView1 = setup_render_view(endx,midx,midy,endy,midz,endz,
                                        cx,cy,cz,cps,resolution,raytracing)



        # create a new 'netcdf Source'
        netcdfSource1 = netcdfSource(DataFileName=f'{data_dir}/{data_fname}',
                                     GridFileName=f'{grid_dir}/{grid_fname}')

        netcdfSource1.FieldsToLoad = fields
        netcdfSource1.VariableNameOfGridsInNetcdfFile = grid_var_names
        netcdfSource1.nx = nx
        netcdfSource1.ny = ny
        netcdfSource1.nz = nz
        netcdfSource1.iy = iy

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
        if nyp>1:
            Disconnect()
            Connect()
