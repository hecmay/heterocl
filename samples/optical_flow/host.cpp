
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
#include "ap_fixed.h"
#include <cmath>

// harness namespace
using namespace rosetta;

int main(int argc, char ** argv) {
  int32_t* arg_0 = (int32_t*)shmat(1008140288, nullptr, 0);
  int32_t* input_image0 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image0[i1 + i0*1024] = (int32_t)(arg_0[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_1 = (int32_t*)shmat(1008173058, nullptr, 0);
  int32_t* input_image1 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image1[i1 + i0*1024] = (int32_t)(arg_1[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_2 = (int32_t*)shmat(1008205827, nullptr, 0);
  int32_t* input_image2 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image2[i1 + i0*1024] = (int32_t)(arg_2[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_3 = (int32_t*)shmat(1008238596, nullptr, 0);
  int32_t* input_image2_0 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image2_0[i1 + i0*1024] = (int32_t)(arg_3[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_4 = (int32_t*)shmat(1008271365, nullptr, 0);
  int32_t* input_image2_1 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image2_1[i1 + i0*1024] = (int32_t)(arg_4[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_5 = (int32_t*)shmat(1008304134, nullptr, 0);
  int32_t* input_image3 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image3[i1 + i0*1024] = (int32_t)(arg_5[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_6 = (int32_t*)shmat(1008336903, nullptr, 0);
  int32_t* input_image4 = new int32_t[436 * 1024];
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      input_image4[i1 + i0*1024] = (int32_t)(arg_6[i1 + i0*1024]) >> 12;
    }
  }

  int32_t* arg_7 = (int32_t*)shmat(1008369672, nullptr, 0);
  int32_t* output_image_0 = new int32_t[463 * 1024 * 2];
  for (size_t i0 = 0; i0 < 463; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      for (size_t i2 = 0; i2 < 2; i2++) {
        output_image_0[i2 + i1*2 + i0*2048] = (int32_t)(arg_7[i2 + i1*2 + i0*2048]) >> 12;
      }
    }
  }

  int32_t* arg_8 = (int32_t*)shmat(1008369472, nullptr, 0);
  int32_t* output_image_1 = new int32_t[463 * 1024 * 2];
  for (size_t i0 = 0; i0 < 463; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      for (size_t i2 = 0; i2 < 2; i2++) {
        output_image_1[i2 + i1*2 + i0*2048] = (int32_t)(arg_8[i2 + i1*2 + i0*2048]) >> 12;
      }
    }
  }

  // parse command line arguments for opencl version 
  std::string kernelFile("");
  parse_sdaccel_command_line_args(argc, argv, kernelFile);
 
  // create OpenCL world
  CLWorld world = CLWorld(TARGET_DEVICE, CL_DEVICE_TYPE_ACCELERATOR);
  world.addProgram(kernelFile);

  // compute and kernel call from host
  ap_fixed<32, 20> tensor_weight_y_5;
  ap_fixed<32, 20> tensor_weight_y_4;
  ap_fixed<32, 20> tensor_weight_y_3;
  ap_fixed<32, 20> tensor_weight_y_2;
  ap_fixed<32, 20> tensor_weight_y_1;
  ap_fixed<32, 20> tensor_weight_y_0;
  ap_fixed<32, 20> tensor_weight_x_5;
  ap_fixed<32, 20> tensor_weight_x_4;
  ap_fixed<32, 20> tensor_weight_x_3;
  ap_fixed<32, 20> tensor_weight_x_2;
  ap_fixed<32, 20> tensor_weight_x_1;
  ap_fixed<32, 20> tensor_weight_x_0;
  ap_fixed<32, 20> outer_product;
  ap_fixed<32, 20> grad_weight_x_2;
  ap_fixed<32, 20> grad_weight_x_1;
  ap_fixed<32, 20> grad_weight_x_0;
  ap_fixed<32, 20> grad_weight_y_2;
  ap_fixed<32, 20> grad_weight_y_1;
  ap_fixed<32, 20> grad_weight_y_0;
  ap_fixed<32, 20> calc_z_gradient;
  ap_fixed<32, 20> calc_y_gradient;
  ap_fixed<32, 20> calc_x_gradient;
                
  CLKernel top_function_0(world.getContext(), world.getProgram(), "top_function_0", world.getDevice());
  CLMemObj source_0((void*)input_image0, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_1((void*)input_image1, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_2((void*)input_image2_0, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_3((void*)input_image2_1, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_4((void*)input_image2, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_5((void*)input_image3, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_6((void*)input_image4, sizeof(ap_fixed<32, 20>), 436 *1024, CL_MEM_READ_WRITE);
  CLMemObj source_7((void*)output_image_0, sizeof(ap_fixed<32, 20>), 436 *1024 *2, CL_MEM_READ_WRITE);
  CLMemObj source_8((void*)output_image_1, sizeof(ap_fixed<32, 20>), 436 *1024 *2, CL_MEM_READ_WRITE);
  world.addMemObj(source_0);
  world.addMemObj(source_1);
  world.addMemObj(source_2);
  world.addMemObj(source_3);
  world.addMemObj(source_4);
  world.addMemObj(source_5);
  world.addMemObj(source_6);
  world.addMemObj(source_7);
  world.addMemObj(source_8);

  int global_size[3] = {1, 1, 1};
  int local_size[3]  = {1, 1, 1};
  top_function_0.set_global(global_size);
  top_function_0.set_local(local_size);
  world.addKernel(top_function_0);

  world.setMemKernelArg(0, 0, 0);
  world.setMemKernelArg(0, 1, 1);
  world.setMemKernelArg(0, 2, 2);
  world.setMemKernelArg(0, 3, 3);
  world.setMemKernelArg(0, 4, 4);
  world.setMemKernelArg(0, 5, 5);
  world.setMemKernelArg(0, 6, 6);
  world.setMemKernelArg(0, 7, 7);
  world.setMemKernelArg(0, 8, 8);

  world.runKernels();
  world.readMemObj(0);
  world.readMemObj(1);
  world.readMemObj(2);
  world.readMemObj(3);
  world.readMemObj(4);
  world.readMemObj(5);
  world.readMemObj(6);
  world.readMemObj(7);
  world.readMemObj(8);
  
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_0[i1 + i0*1024] = (int32_t)(input_image0[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_0);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_1[i1 + i0*1024] = (int32_t)(input_image1[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_1);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_2[i1 + i0*1024] = (int32_t)(input_image2[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_2);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_3[i1 + i0*1024] = (int32_t)(input_image2_0[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_3);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_4[i1 + i0*1024] = (int32_t)(input_image2_1[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_4);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_5[i1 + i0*1024] = (int32_t)(input_image3[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_5);
  for (size_t i0 = 0; i0 < 436; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      arg_6[i1 + i0*1024] = (int32_t)(input_image4[i1 + i0*1024]) << 12;
    }
  }
  shmdt(arg_6);
  for (size_t i0 = 0; i0 < 463; i0++) {
    for (size_t i1 = 0; i1 < 1024; i1++) {
      for (size_t i2 = 0; i2 < 2; i2++) {
        arg_7[i2 + i1*2 + i0*2048] = (int32_t)(output_image_0[i2 + i1*2 + i0*2048]) << 12;
      }
    }
  }
  shmdt(arg_7);


  }
