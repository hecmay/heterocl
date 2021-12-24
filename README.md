---
title: FPGA'22 Artifact Evaluation
---

## Before Getting Started
This README provides the instructions to reproduce the results shown in our paper (HeteroFlow: An Accelerator Programming Model with Decoupled Data Placement for Software-Defined FPGAs).

We provided the following two ways for AE reviewers to reproduce the results. Please let us know which one works better for you.

### Local servers
If you have Vitis and Alveo FPGAs installed in your local server, you can directly go to the "installation" section and execute the commands to re-produce the results. Otherwise, please check the following subsection "Azure cloud FPGA server".

### Azure cloud FPGA server

In case that reviewers do not have the FPGA devices to run the experiments, we have created an Azure FPGA virtual machine equipped with 8 CPU cores, 168 GB memory and an Xilinx U250 FPGA for reviewers to run the experiments and evaluations.

To make the evaluation process easier, we provide reviewers with SSH private keys to login into the instance during the evaluation. Please contact us by email directly (sx233@cornell.edu) and we will share the SSH private key. Please also let us know whenever you are done with the evaluation, so that we can shutdown the instance in time and minimize the cost.

Here is the instructions to connect to the Azure cloud FPGA server. We recommend you to check the devices and runtime environment before proceeding to the evaluation.

```shell
# (optional) change permission of the key if there is bad permission errors
chmod 400 eval.pem

# ssh to Azure FPGA server with private key
ssh -i eval.pem azureuser@20.115.27.186
# ensure that Xilinx vitis and XRT are loaded
v++ --version
# make sure the FPGA device is present 
lspci | grep "accelerators"
```

## Installation
Please make sure the server has the following softwares installed before start building HeteroFlow. For llvm and cmake (marked with asterisk symbols), our build script will automatically install the correct versions if no installations are detected in the system. 

```shell
Xilinx Vitis v2019.2.1 (64-bit) SW Build 2729669
g++ version >= 4.8.5
llvm* version >= 6.0.0
cmake* version >= 3.12.0
```

If you are using the Azure FPGA cloud server for evaluation, we will create an OS image that has these dependencies pre-installed, and you do not have to worry about it. 

After making sure these dependencies are satisfied, please proceed to clone and compile from the source code. To make sure HeteroFlow is correctly installed, please also check the test cases and ensure there is no error (sometimes there will be errors if the compiler is not properly installed)

```shell
# install and initiate conda environment 
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
bash ~/miniconda.sh -b -p $HOME/miniconda
eval "$(~/miniconda/bin/conda shell.bash hook)"
conda create --name hcl python=3.7 -y
conda activate hcl

# clone the and compile HeteroFlow code from github
git clone https://github.com/Hecmay/heterocl.git -b eval
cd heterocl; export HCL_HOME=$(pwd)
make -j`nproc`

# ensure HeteroFlow is installed
python -c "import heterocl"
```

## Code evaluation
Once you successfully build and install HeteroFlow compiler from source, you can use HeteroFlow to our DSL programs into optimized HLS code, and eventually bitstreams for FPGA execution. 

Since the bitstream compilation can be time-consuming, we also provide you with the pre-compiled bitstream and host program to reproduce the numbers directly (please follow the instructions in the later sections)
 
### Optical Flow
This application is the first benchmark evaluated in the our paper. Since Azure cloud only provides Xilinx Alveo FPGAs to public, so in this evaluation, we only target the U250 FPGA available on the Azure cloud FPGA server. 

```shell
# 1. go to the work directory
cd $HCL_HOME/samples/optical_flow

# 2. setup execution environment
source /opt/xilinx/xrt/setup.sh
export XDEVICE=/opt/xilinx/platforms/xilinx_u250_gen3x16_xdma_2_1_202010_1/xilinx_u250_gen3x16_xdma_2_1_202010_1.xpfm

# 3. run the HLS code generation and hardware synthesis (a few mins)
#    after hardware synthesis, you will see the synthesis report
#    Example:
#       INFO: [v++ 204-61] Pipelining loop 'VITIS_LOOP_30_1_VITIS_LOOP_31_2'.
#       INFO: [v++ 200-1470] Pipelining result : Target II = 1, Final II = 1, Depth = 153, loop
#       INFO: [v++ 200-790] **** Loop Constraint Status: All loop constraints were satisfied.
#       INFO: [v++ 200-789] **** Estimated Fmax: 411.00 MHz
#
python case_study_optical_flow.py

# 4. check the generated HLS code, host (OpenCL) cod, and HLS report.
#    the source code and utility files are generated under "project" folder.
vi project/kernel.cpp
vi project/host.cpp
vi project/_x.hw.xilinx_u250_gen3x16_xdma_2_1_202010_1/reports/kernel/hls_reports/test_csynth.rpt

# 5. compile the HLS code into bitstream (this takes hours to finish)
cd project; make all TARGET=hw DEVICE=$XDEVICE

# 6. validate and register the xclbin on Azure for FPGA execution
source validate.sh

# 7. execute the bitstream on U250 FPGA
./host kernel.xclbin
```
