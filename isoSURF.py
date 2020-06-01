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
plugin_dir = f'/linkhome/rech/genlfl01/username/path/to/folder/Paraview_isoSURF'

# Data and Grids Directory
data_dir = f'/gpfsscratch/rech/avl/username/path/to/data/folder'
grid_dir = f'/gpfsscratch/rech/avl/username/path/to/grid/folder'

# Data and Grids file names
data_fname = f'Q_small_field.nc'
grid_fname = f'grid.nc'

# Image directory and name
imag_dir = f'/gpfsscratch/rech/avl/username/path/to/image/folder'
imag_name = 'test_imamge.png'

# Fields to Load from netcdf as they appear in the netcdf file
# If we want a grid coordinate to load as a scalar variable add to the list
# 'x','y', or 'z'
fields = 'Q,x'

# Grids variables names as they appear in the netcdf file
grid_var_names = 'gridx,gridy,gridz'

# Size of fields to load (nx,ny,nz)
nx = 500
ny = 500
nz = 500


# Read Grid file - no changes needed
# ------------
f = Dataset(f'{grid_dir}/{grid_fname}', 'r')
x = f.variables[grid_var_names.split(',')[0]][:nx]
y = f.variables[grid_var_names.split(',')[1]][:ny]
z = f.variables[grid_var_names.split(',')[2]][:nz]
f.close()
del f
# ------------


# Isosurface Settings
isosurface_field = 'Q'
isovalue = 0.04
scalar_to_color = 'x' # Scalar field to color the isosurface

# Colormap
cmap = 'Blues'
cmap_min = x[0]  # min value color
cmap_max = x[-1] # max value color

# Create a plane for bottom wall(0: False, 1: True)
wall = 1

# Camera Settings
resolution = [1280,720] # Image resolution

# Adjust Camera position with respect to grid coordinates
# CameraPosition = (x[0]*cx, y[-1]*cy, z[-1]*cz)
cx = 1
cy = 1.8
cz = 1.9

# Camera Parallel Scale - Zoom in/out
# Distance from focal point to edge of viewport(?)
cps = 1.5 * y[-1] # smaller values -> zoom in !! bigger -> zoom out

# Enable raytracing, change value to 1 for raytracing rendering
raytracing = 1


# %%===========================================================================
# Main Program
# =============================================================================
if __name__ == '__main__':

    # Compute Bounds of Grid
    startx,starty,startz,midx,midy,midz,endx,endy,endz = compute_bounds(x,y,z)

    renderView1 = setup_render_view(startx,midx,midy,endy,midz,endz,
                                    cx,cy,cz,cps,resolution,raytracing)

    # Load Plugins
    LoadPlugin(f'{plugin_dir}/netcdfSource.py', ns=globals())


    # create a new 'netcdf Source'
    netcdfSource1 = netcdfSource(DataFileName=f'{data_dir}/{data_fname}',
                                GridFileName=f'{grid_dir}/{grid_fname}')

    netcdfSource1.FieldsToLoad = fields
    netcdfSource1.VariableNameOfGridsInNetcdfFile = grid_var_names
    netcdfSource1.nx = nx
    netcdfSource1.ny = ny
    netcdfSource1.nz = nz

    # Create Isosurface
    contour1 = Contour(Input=netcdfSource1)
    contour1.ContourBy = ['POINTS', isosurface_field]
    contour1.Isosurfaces = [isovalue]
    contour1.PointMergeMethod = 'Uniform Binning'

    # Settings for Isosurface
    isosurface_settings(contour1, renderView1, isosurface_field,
                        scalar_to_color, cmap, cmap_min, cmap_max, raytracing)

    # create a new 'Plane'
    if wall:
        plane1 = Plane()
        plane1.Origin = [x[0], y[0], z[0]]
        plane1.Point1 = [x[0], y[0], z[-1]]
        plane1.Point2 = [x[-1], y[0], z[0]]

        plane_settings(plane1, renderView1)


    SetActiveSource(contour1)

    # Save Screenshot
    SaveScreenshot(f'{imag_dir}/{imag_name}', ImageResolution=(resolution[0],
                                                               resolution[1]),
                TransparentBackground = 1,
                CompressionLevel = 0)
