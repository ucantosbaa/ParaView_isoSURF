# %%===========================================================================
# Import Libraries
# =============================================================================

import vtk
from paraview.simple import *
from vtk.numpy_interface import dataset_adapter as dsa
from netCDF4 import Dataset
from main_functions import *

# %%===========================================================================
# User Settings
# =============================================================================

# Plugins Directory
plugin_dir = f'/linkhome/rech/genlfl01/username/path/to/folder/ParaView_isoSURF'

# Data and Grids Directory
data_dir = f'/gpfsscratch/rech/avl/username/path/to/data/folder'
grid_dir = f'/gpfsscratch/rech/avl/username/path/to/grid/folder'

# Data and Grids file names
data_fname = f're550_016000vel_der_eps.nc'
grid_fname = f'grid.nc'

# Image directory and name
imag_dir = f'/gpfsscratch/rech/avl/username/path/to/image/folder'
imag_name = f'test_image.png'

# Fields to Load from netcdf as they appear in the netcdf file
# If we want a grid coordinate to load as a scalar variable add to the list
# 'x','y', or 'z'
fields = 'Q,y'

# Grids variables names as they appear in the netcdf file
grid_var_names = 'gridx,gridy,gridz'

# Size of fields to load (nx,ny,nz)
nx = 800
ny = 193
nz = 700


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
nt = 1          # number of saved timesteps
istart = 2200   # Iteration number of first saved time step
istep = 50      # Number of iterations per saved time step

# Isosurface Settings.
# For multiple isosurfaces just add entries to all the  corresponding arrays.
isosurface_fields = ['Q']
isovalue = [0.05]
scalar_to_color = ['y'] # Scalar field to color the isosurface, if we want solid color put ''


# Colormap
cmap = ['Blues']
cmap_min = [y[0]]  # min value color
cmap_max = [y[-1]] # max value color

solid_color = [[68/255.,107/255.,242/255.],[0,0,0]] # Solid color in RGB

# Create a plane for bottom wall(0: False, 1: True)
wall = 1

# Camera Settings
resolution = [1280,720] # Image resolution

# Adjust Camera position with respect to grid coordinates
# CameraPosition = (x[0]*cx, y[-1]*cy, z[-1]*cz)
cx = 1
cy = 2
cz = 2

# Camera Parallel Scale - Zoom in/out
# Distance from focal point to edge of viewport(?)
cps = 2.4 * y[-1] # smaller values -> zoom in !! bigger -> zoom out

# Enable raytracing, change value to 1 for raytracing rendering
raytracing = 1


# %%===========================================================================
# Main Program
# =============================================================================
if __name__ == '__main__':

    # Load Plugins
    LoadPlugin(f'{plugin_dir}/netcdfSource.py', ns=globals())

    for it in range(nt):

        # If multiple time steps change the name of netcdf file to open
        # and the name of image to be saved
        if (nt > 1):
            int2char = str(it*istep+istart).zfill(6) # Timestep of file to open
            data_fname = f're550_{int2char}vel_der_eps.nc'
            imag_name = f'test_image_{it}.png'

        # Compute Bounds of Grid
        startx,starty,startz,midx,midy,midz,endx,endy,endz = compute_bounds(x,y,z)

        renderView1 = setup_render_view(startx,midx,midy,endy,midz,endz,
                                        cx,cy,cz,cps,resolution,raytracing)



        # create a new 'netcdf Source'
        netcdfSource1 = netcdfSource(DataFileName=f'{data_dir}/{data_fname}',
                                    GridFileName=f'{grid_dir}/{grid_fname}')

        netcdfSource1.FieldsToLoad = fields
        netcdfSource1.VariableNameOfGridsInNetcdfFile = grid_var_names
        netcdfSource1.nx = nx
        netcdfSource1.ny = ny
        netcdfSource1.nz = nz

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
