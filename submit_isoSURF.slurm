#!/bin/bash
#SBATCH --job-name=test_paraview
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=10
#SBATCH --hint=nomultithread
#SBATCH --time=02:00:00
#SBATCH --output=out_test_paraview%j.out
#SBATCH --error=eout_test_paraview%j.out
#SBATCH -A avl@gpu
#SBATCH --partition=visu

cd ${SLURM_SUBMIT_DIR}

module purge
module load intel-all/19.0.4
module load paraview/5.8.0-mpi-python3-nek5000
module load python/3.7.6

export PATH=$PATH:$CONDA_PREFIX/bin
export PYTHONPATH=$PYTHONPATH:$CONDA_PREFIX/lib/python3.7/site-packages/
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib

### Command echoes ###
set -x

############################################################
#srun --unbuffered pvbatch --mpi --symmetric --force-offscreen-rendering /linkhome/rech/genlfl01/upa47zs/ParaView_isoSURF/isoSURF.py 2>&1 | tee log.out
############################################################ 
srun --unbuffered pvbatch --mpi --symmetric --force-offscreen-rendering /linkhome/rech/genlfl01/upa47zs/ParaView_isoSURF/isoSURF.py > log.out

