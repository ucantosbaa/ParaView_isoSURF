import vtk
from paraview.simple import *

def compute_bounds(x,y,z):

    startx = x[0]
    endx = x[-1]
    midx = (startx+endx)/2.

    starty = y[0]
    endy = y[-1]
    midy = (starty+endy)/2.

    startz = z[0]
    endz = z[-1]
    midz = (startz+endz)/2.

    return startx,starty,startz,midx,midy,midz,endx,endy,endz


def setup_render_view(startx,midx,midy,endy,midz,endz,cx,cy,cz,cps,
                      resolution, raytracing):
    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # Create a new 'Render View'
    renderView1 = CreateView('RenderView')
    renderView1.ViewSize = [resolution[0], resolution[1]]
    renderView1.AxesGrid = 'GridAxes3DActor'
    renderView1.CenterOfRotation = [midx,midy,midz]
    renderView1.StereoType = 'Crystal Eyes'
    renderView1.CameraPosition = [startx*cx, endy*cy, endz*cz]
    renderView1.CameraFocalPoint = [midx,midy,midz]
    renderView1.CameraViewUp = [0,1,0]
    renderView1.CameraFocalDisk = 1.
    renderView1.CameraParallelScale = cps
    renderView1.CameraParallelProjection = 1
    renderView1.BackEnd = 'OSPRay raycaster'
    renderView1.KeyLightIntensity = 1.0
    renderView1.FillLightKFRatio = 3
    renderView1.BackLightKBRatio = 3
    renderView1.HeadLightKHRatio = 2.5
    renderView1.OSPRayMaterialLibrary = materialLibrary1
    if raytracing:
        renderView1.EnableRayTracing = 1
        renderView1.Shadows = 0
        renderView1.BackEnd = 'OSPRay pathtracer'
        renderView1.SamplesPerPixel = 50
        renderView1.ProgressivePasses = 18000

    # create new layout object 'Layout #1'
    layout1 = CreateLayout(name='Layout #1')
    layout1.AssignView(0, renderView1)

    SetActiveView(renderView1)

    return renderView1


def isosurface_settings(contour1, contour1Display, renderView1, isosurface_field,
                        scalar_to_color, cmap, cmap_min, cmap_max, raytracing):

    # get color transfer function/color map for scalar
    LUT = GetColorTransferFunction(scalar_to_color)
    LUT.ApplyPreset(cmap, True)
    LUT.RescaleTransferFunction(cmap_min, cmap_max)

    # trace defaults for the display properties.
    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = ['POINTS', scalar_to_color]
    contour1Display.LookupTable = LUT
    contour1Display.OSPRayScaleArray = isosurface_field
    contour1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    contour1Display.SelectOrientationVectors = 'None'
    contour1Display.ScaleFactor = 3.7375000000000003
    contour1Display.SelectScaleArray = isosurface_field
    contour1Display.GlyphType = 'Arrow'
    contour1Display.GlyphTableIndexArray = isosurface_field
    contour1Display.GaussianRadius = 0.186875
    contour1Display.SetScaleArray = ['POINTS', isosurface_field]
    contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display.OpacityArray = ['POINTS', isosurface_field]
    contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
    contour1Display.DataAxesGrid = 'GridAxesRepresentation'
    contour1Display.PolarAxes = 'PolarAxesRepresentation'
    if raytracing:
        contour1Display.Interpolation = 'PBR'
        contour1Display.Roughness = 0.24
        contour1Display.Metallic = 0.1

    # get color legend/bar for yLUT in view renderView1
    LUTColorBar = GetScalarBar(LUT, renderView1)
    LUTColorBar.Title = scalar_to_color
    LUTColorBar.ComponentTitle = ''

    # set color bar visibility
    LUTColorBar.Visibility = 0

    # show color legend
    contour1Display.SetScalarBarVisibility(renderView1, False)

def plane_settings(plane1, renderView1):

    # show data from plane1
    plane1Display = Show(plane1, renderView1, 'GeometryRepresentation')

    # trace defaults for the display properties.
    plane1Display.Representation = 'Surface'
    plane1Display.ColorArrayName = [None, '']
    plane1Display.OSPRayScaleArray = 'Normals'
    plane1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    plane1Display.SelectOrientationVectors = 'None'
    plane1Display.ScaleFactor = 11.23499755859375
    plane1Display.SelectScaleArray = 'None'
    plane1Display.GlyphType = 'Arrow'
    plane1Display.GlyphTableIndexArray = 'None'
    plane1Display.GaussianRadius = 0.5617498779296876
    plane1Display.SetScaleArray = ['POINTS', 'Normals']
    plane1Display.ScaleTransferFunction = 'PiecewiseFunction'
    plane1Display.OpacityArray = ['POINTS', 'Normals']
    plane1Display.OpacityTransferFunction = 'PiecewiseFunction'
    plane1Display.DataAxesGrid = 'GridAxesRepresentation'
    plane1Display.PolarAxes = 'PolarAxesRepresentation'

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    plane1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    plane1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]
