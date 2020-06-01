## Installation

Clone the repository in your home directory

```console
cd $HOME
git clone https://github.com/argapost/Paraview_isoSURF.git
cd Paraview_isoSURF
```

## User Settings

The only changes needed to be made are in the script: isoSURF.py, under the section **User Settings**.

Comments provide the necessary assist to change the settings.

## Submission in _Jean-Zay_

Go to your `$SCRATCH` dir, create a dirctory and put tha data and the grid files.

Make a submission file like below:

```bash
#!/bin/bash
#SBATCH --job-name=test_paraview
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=10
#SBATCH --hint=nomultithread
#SBATCH --time=00:10:00
#SBATCH --output=out_test_paraview%j.out
#SBATCH --error=eout_test_paraview%j.out
#SBATCH -A avl@gpu
#SBATCH --partition=visu


cd ${SLURM_SUBMIT_DIR}

module purge
module load intel-all/19.0.4
module load paraview/5.8.0-mpi-python3-nek5000

### Command echoes ###
set -x

###########################################################  

############################################################
srun pvbatch --mpi --symmetric --force-offscreen-rendering /linkhome/rech/genlfl01/ulj39ir/scripts/post_process/Paraview_isoSURF/isoSURF.py
############################################################ 

```
Change the directory of the python script to match your home directory.

When you ssh to idris, remember to ```ssh -X idris``` to enable X forwarding.

Sometimes when I submit the script, it runs smoothly until the last command where I save a screenshot in Paraview, where it procudes the following error:

And other times it runs ok until the end. I will have to investigate further with assist@idris.fr



