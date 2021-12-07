# install conda environment
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda

# initialization + env
eval "$(~/miniconda/bin/conda shell.bash hook)"
conda create --name hcl python=3.7 -y
conda activate hcl

# set up the default target device
export XDEVICE=/opt/xilinx/platforms/xilinx_u280_xdma_201920_3/xilinx_u280_xdma_201920_3.xpfm

# download and install heterocl 
git checkout eval
make -j`nproc`
