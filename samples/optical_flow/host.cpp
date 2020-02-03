
#include <sys/ipc.h>
#include <sys/shm.h>

// standard C/C++ headers
#include <cstdio>
#include <cstdlib>
#include <getopt.h>
#include <string>
#include <time.h>
#include <sys/time.h>

// opencl harness headers
#include "CLWorld.h"
#include "CLKernel.h"
#include "CLMemObj.h"
#include "utils.h"
#include <cmath>

// harness namespace
using namespace rosetta;

int main(int argc, char ** argv) {
  printf("xsxsxsx");
  float* input_image0 = new float[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image0[i1 + i0*1024] = (float)(20);
    }
  }

  float* input_image1 = new float[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image1[i1 + i0*1024] = (float)(21);
    }
  }

  float* input_image2 = new float[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image2[i1 + i0*1024] = (float)(22);
    }
  }

  float* input_image3 = new float[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image3[i1 + i0*1024] = (float)(23);
    }
  }

  float* input_image4 = new float[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image4[i1 + i0*1024] = (float)(24);
    }
  }

  float grad_weight[5];
  for (size_t i0 = 0; i0 < 5; i0++) {
    grad_weight[i0] = (float)(25);
  }

  float grad_filter[7];
  for (size_t i0 = 0; i0 < 7; i0++) {
    grad_filter[i0] = (float)(26);
  }

  float tensor_filter[3];
  for (size_t i0 = 0; i0 < 3; i0++) {
    tensor_filter[i0] = (float)(27);
  }

  float output_image[463 * 1024 * 2];
  for (size_t i0 = 0; i0 < 463; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      for (size_t i2 = 0; i2 < 2; i2++) {
        output_image[i2 + i1*2 + i0*2048] = (float)(28);
      }
    }
  }

  // compute before kernel function
  


  // parse command line arguments for opencl version 
  std::string kernelFile("");
  parse_sdaccel_command_line_args(argc, argv, kernelFile);

  // create OpenCL world
  CLWorld world = CLWorld(TARGET_DEVICE, CL_DEVICE_TYPE_ACCELERATOR);

  // add the bitstream file
  world.addProgram(kernelFile);
 
  // create kernels
  CLKernel App(world.getContext(), world.getProgram(), "top_function_0", world.getDevice());

  // create mem objects
  CLMemObj source_0((void*)input_image0, sizeof(float), 436 * 1024, CL_MEM_READ_WRITE);
  CLMemObj source_1((void*)input_image1, sizeof(float), 436 * 1024, CL_MEM_READ_WRITE);
  CLMemObj source_2((void*)input_image2, sizeof(float), 436 * 1024, CL_MEM_READ_WRITE);
  CLMemObj source_3((void*)input_image3, sizeof(float), 436 * 1024, CL_MEM_READ_WRITE);
  CLMemObj source_4((void*)input_image4, sizeof(float), 436 * 1024, CL_MEM_READ_WRITE);
  CLMemObj source_5((void*)grad_weight, sizeof(float), 5 , CL_MEM_READ_WRITE);
  CLMemObj source_6((void*)grad_filter, sizeof(float), 7 , CL_MEM_READ_WRITE);
  CLMemObj source_7((void*)tensor_filter, sizeof(float), 3 , CL_MEM_READ_WRITE);
  CLMemObj source_8((void*)output_image, sizeof(float), 463 * 1024* 2, CL_MEM_READ_WRITE);

  // add them to the world
  world.addMemObj(source_0);
  world.addMemObj(source_1);
  world.addMemObj(source_2);
  world.addMemObj(source_3);
  world.addMemObj(source_4);
  world.addMemObj(source_5);
  world.addMemObj(source_6);
  world.addMemObj(source_7);
  world.addMemObj(source_8);

  // set work size
  int global_size[3] = {1, 1, 1};
  int local_size[3] = {1, 1, 1};
  App.set_global(global_size);
  App.set_local(local_size);

  // add them to the world
  world.addKernel(App);

  // set kernel arguments
  world.setMemKernelArg(0, 0, 0);
  world.setMemKernelArg(0, 1, 1);
  world.setMemKernelArg(0, 2, 2);
  world.setMemKernelArg(0, 3, 3);
  world.setMemKernelArg(0, 4, 4);
  world.setMemKernelArg(0, 5, 5);
  world.setMemKernelArg(0, 6, 6);
  world.setMemKernelArg(0, 7, 7);
  world.setMemKernelArg(0, 8, 8);

  // run
  world.runKernels();

  // read the data back
    world.readMemObj(0);
  world.readMemObj(1);
  world.readMemObj(2);
  world.readMemObj(3);
  world.readMemObj(4);
  world.readMemObj(5);
  world.readMemObj(6);
  world.readMemObj(7);
  world.readMemObj(8);
  // compute after kernel function


  }
