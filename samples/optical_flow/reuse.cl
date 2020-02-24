
__kernel void tensor_weight_x() {
    float tensor_weight_x_tensor_y_reuse[3][1024];
    float t_w[3];
    t_w[0] = 3.243000e-01f;
    t_w[1] = 3.513000e-01f;
    t_w[2] = 3.243000e-01f;
    for (int32_t y_reuse = 0; y_reuse < 438; ++y_reuse) {
      for (int32_t x = 0; x < 1024; ++x) {
        for (int32_t tensor_weight_x_tensor_y_1 = 0; tensor_weight_x_tensor_y_1 < 2; ++tensor_weight_x_tensor_y_1) {
          tensor_weight_x_tensor_y_reuse[(x + (tensor_weight_x_tensor_y_1 * 1024))] = tensor_weight_x_tensor_y_reuse[((x + (tensor_weight_x_tensor_y_1 * 1024)) + 1024)];
        }
        tensor_weight_x_tensor_y_reuse[(x + 2048)] = read_channel_intel(c_buf_6);
        if (2 <= y_reuse) {
          float reducer5;
          reducer5 = 0.000000e+00f;
          for (int32_t rdx_x = 0; rdx_x < 3; ++rdx_x) {
            reducer5 = ((tensor_weight_x_tensor_y_reuse[((x + (rdx_x * 1024)) + -1024)] * t_w[rdx_x]) + reducer5);
          }
          write_channel_intel(c_buf_7, (float)((x < 1) ? 0.000000e+00f : reducer5));
        }
      }
    }
}

__kernel void tensor_weight_y(__global float* restrict tensor_weight_y_out_product, __global float* restrict tensor_weight_y_tensor_y) {
    float tensor_weight_y_out_product_reuse[3][1024];
    float t_w[3];
    t_w[0] = 3.243000e-01f;
    t_w[1] = 3.513000e-01f;
    t_w[2] = 3.243000e-01f;
    for (int32_t y_reuse = 0; y_reuse < 438; ++y_reuse) {
      for (int32_t x = 0; x < 1024; ++x) {
        for (int32_t tensor_weight_y_out_product_1 = 0; tensor_weight_y_out_product_1 < 2; ++tensor_weight_y_out_product_1) {
          tensor_weight_y_out_product_reuse[(x + (tensor_weight_y_out_product_1 * 1024))] = tensor_weight_y_out_product_reuse[((x + (tensor_weight_y_out_product_1 * 1024)) + 1024)];
        }
        tensor_weight_y_out_product_reuse[(x + 2048)] = read_channel_intel(c_buf_8);
        if (2 <= y_reuse) {
          float reducer4;
          reducer4 = 0.000000e+00f;
          for (int32_t rdx_y = 0; rdx_y < 3; ++rdx_y) {
            reducer4 = ((tensor_weight_y_out_product_reuse[((x + (rdx_y * 1024)) + -1024)] * t_w[rdx_y]) + reducer4);
          }
          write_channel_intel(c_buf_8, (float)(((3 <= y_reuse) && (y_reuse < 437)) ? reducer4 : 0.000000e+00f));
        }
      }
    }
}
