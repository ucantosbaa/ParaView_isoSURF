import vtk
import numpy as np
from netCDF4 import Dataset
from vtk.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtk.numpy_interface import dataset_adapter as dsa
from paraview.util.vtkAlgorithm import *

@smproxy.source(name="netcdfSource", label="netcdf Source")
class netcdfSource(VTKPythonAlgorithmBase):
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self,
            nInputPorts=0,
            nOutputPorts=1, outputType='vtkRectilinearGrid')

        self.__DFileName = ""
        self.__GFileName = ""

        self.nx = 1
        self.ny = 1
        self.nz = 1

        self.it = 1

        self.nvar = 1
        self.ngvar = 0

        self._fields=[]


    def RequestData(self, request, inInfo, outInfo):

        output = dsa.WrapDataObject(vtk.vtkRectilinearGrid.GetData(outInfo))
        info = outInfo.GetInformationObject(0)
        exts = info.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_EXTENT())
        whole = info.Get(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT())

        # Dimensions for each processor
        nx = exts[1]-exts[0]+1
        ny = exts[3]-exts[2]+1
        nz = exts[5]-exts[4]+1

        # Read Data file
        f = Dataset(self.__DFileName, 'r')

        data = np.zeros([nz,ny,nx,3,self.nvar])
        for i,field in enumerate(self._fields):
            for ir in [1,10,30]:
                data[:,:,:,ir,i] = f.variables[field][self.it, ir,
                                                      exts[4]:exts[5]+1,
                                                      exts[2]:exts[3]+1,
                                                      exts[0]:exts[1]+1]
        f.close()
        del f


        # Read Grid file
        f = Dataset(self.__GFileName, 'r')
        x = f.variables[self._grid_var_names[0]][exts[0]:exts[1]+1]
        y = f.variables[self._grid_var_names[1]][exts[2]:exts[3]+1]
        z = f.variables[self._grid_var_names[2]][exts[4]:exts[5]+1]
        f.close()
        del f


        # output.SetDimensions([self.nx,self.ny,self.nz])
        output.SetExtent(exts)
        output.SetXCoordinates(dsa.numpyTovtkDataArray(x,"X"))
        output.SetYCoordinates(dsa.numpyTovtkDataArray(y,"Y"))
        output.SetZCoordinates(dsa.numpyTovtkDataArray(z,"Z"))

        for i,field in enumerate(self._fields):
            for ir in [1,10,30]:
                output.PointData.append(data[:,:,:,ir,i].ravel(), field+str(ir))

        if self._grids:
            Z, Y, X = np.meshgrid(z,y,x,indexing='ij')

        if 'x' in self._grids:
            output.PointData.append(X.ravel(), 'x')
            del X
        if 'y' in self._grids:
            output.PointData.append(Y.ravel(), 'y')
            del Y
        if 'z' in self._grids:
            output.PointData.append(Z.ravel(), 'z')
            del Z

        output.PointData.SetActiveScalars(self._fields[0])

        del data,x,y,z
        return 1

    def RequestInformation(self, request, inInfo, outInfo):
        dims = (self.nx,self.ny,self.nz)
        info = outInfo.GetInformationObject(0)
        info.Set(vtk.vtkStreamingDemandDrivenPipeline.WHOLE_EXTENT(),
            (0, dims[0]-1, 0, dims[1]-1, 0, dims[2]-1), 6)
        info.Set(vtk.vtkAlgorithm.CAN_PRODUCE_SUB_EXTENT(),1)
        return 1

    @smproperty.stringvector(name="DataFileName")
    @smdomain.filelist()
    @smhint.filechooser(extensions="nc", file_description="netCDF File")
    def SetDFileName(self, fname):
        if fname != self.__DFileName:
            self.Modified()
            self.__DFileName = fname

    @smproperty.stringvector(name="GridFileName")
    @smdomain.filelist()
    @smhint.filechooser(extensions="nc", file_description="netCDF File")
    def SetGFileName(self, fname):
        if fname != self.__GFileName:
            self.Modified()
            self.__GFileName = fname

    @smproperty.intvector(name="nx", default_values=10)
    def SetNx(self, nx):
        self.nx = nx
        self.Modified()

    @smproperty.intvector(name="ny", default_values=10)
    def SetNy(self, ny):
        self.ny = ny
        self.Modified()

    @smproperty.intvector(name="nz", default_values=10)
    def SetNz(self, nz):
        self.nz = nz
        self.Modified()

    @smproperty.intvector(name="it", default_values=1)
    def SetIt(self, it):
        self.it = it
        self.Modified()

    @smproperty.stringvector(name="FieldsToLoad")
    def SetFields(self, fields):
        self._fields = fields.split(',')
        init_fields = np.copy(self._fields)

        self._grids =[]
        for f in init_fields:
            if f.lower()=='x':
                self._fields.remove(f)
                self._grids.append(f)
            if f.lower()=='y':
                self._fields.remove(f)
                self._grids.append(f)
            if f.lower()=='z':
                self._fields.remove(f)
                self._grids.append(f)
        self.nvar = len(self._fields)
        self.ngvar = len(self._grids)
        self.Modified()

    @smproperty.stringvector(name="VariableNameOfGridsInNetcdfFile")
    def SetGridVarNames(self, grid_var_names):
        self._grid_var_names = grid_var_names.split(',')
        self.Modified()

    def GetDFileName(self):
        return self.__DFileName

    def GetGFileName(self):
        return self.__GFileName
