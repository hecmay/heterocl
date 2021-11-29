#include <ap_int.h>
#include <ap_fixed.h>
#include <hls_stream.h>
#include <math.h>

// static void flow_calc(ap_fixed<32, 20>* flow_calc_tensor_0, ap_fixed<32, 20>* flow_calc_tensor_1, ap_fixed<32, 20>* flow_calc_tensor_2, ap_fixed<32, 20>* flow_calc_tensor_3, ap_fixed<32, 20>* flow_calc_tensor_4, ap_fixed<32, 20>* flow_calc_tensor_5, ap_fixed<32, 20>* flow_calc_output_0, ap_fixed<32, 20>* flow_calc_output_1) {
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//         if ((((2 <= y) && (y < 434)) && (2 <= x)) && (x < 1022)) {
//           ap_fixed<32, 20> t0;
//           t0 = flow_calc_tensor_0[(x + (y * 1024))];
//           ap_fixed<32, 20> t1;
//           t1 = flow_calc_tensor_1[(x + (y * 1024))];
//           ap_fixed<32, 20> t2;
//           t2 = flow_calc_tensor_2[(x + (y * 1024))];
//           ap_fixed<32, 20> t3;
//           t3 = flow_calc_tensor_3[(x + (y * 1024))];
//           ap_fixed<32, 20> t4;
//           t4 = flow_calc_tensor_4[(x + (y * 1024))];
//           ap_fixed<32, 20> t5;
//           t5 = flow_calc_tensor_5[(x + (y * 1024))];
//           ap_fixed<32, 20> denom;
//           denom = ((ap_fixed<32, 20>)((((ap_fixed<64, 52>)t1) * ((ap_fixed<64, 52>)t2)) - (((ap_fixed<64, 52>)t4) * ((ap_fixed<64, 52>)t4))));
//           flow_calc_output_0[((x + (y * 1024)) * 2)] = ((ap_fixed<32, 20>)(((ap_fixed<97, 53>)((ap_fixed<65, 41>)((((ap_fixed<64, 52>)t5) * ((ap_fixed<64, 52>)t3)) - (((ap_fixed<64, 52>)t4) * ((ap_fixed<64, 52>)t1))))) / ((ap_fixed<97, 53>)denom)));
//           flow_calc_output_1[(((x + (y * 1024)) * 2) + 1)] = ((ap_fixed<32, 20>)(((ap_fixed<97, 53>)((ap_fixed<65, 41>)((((ap_fixed<64, 52>)t4) * ((ap_fixed<64, 52>)t3)) - (((ap_fixed<64, 52>)t5) * ((ap_fixed<64, 52>)t0))))) / ((ap_fixed<97, 53>)denom)));
//         }
//       }
//     }
//   }
// 
// static void tensor_weight_y_5(ap_fixed<32, 20>* tensor_weight_y_5_out_product_5, ap_fixed<32, 20>* tensor_weight_y_5_tensor_y_5) {
//     ap_fixed<32, 20> tensor_weight_y_5_out_product_5_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_5_out_product_5_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_5_out_product_5_reuse inter false
//         for (ap_int<32> tensor_weight_y_5_out_product_5_1 = 0; tensor_weight_y_5_out_product_5_1 < 2; ++tensor_weight_y_5_out_product_5_1) {
//           tensor_weight_y_5_out_product_5_reuse[tensor_weight_y_5_out_product_5_1][x] = tensor_weight_y_5_out_product_5_reuse[(tensor_weight_y_5_out_product_5_1 + 1)][x];
//         }
//         tensor_weight_y_5_out_product_5_reuse[2][x] = tensor_weight_y_5_out_product_5[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer19;
//         reducer19 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer19 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_5_out_product_5_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer19)));
//         }
//         tensor_weight_y_5_tensor_y_5[((x + (y_reuse * 1024)))] = reducer19;
//       }
//     }
//   }
// 
// static void tensor_weight_y_4(ap_fixed<32, 20>* tensor_weight_y_4_out_product_4, ap_fixed<32, 20>* tensor_weight_y_4_tensor_y_4) {
//     ap_fixed<32, 20> tensor_weight_y_4_out_product_4_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_4_out_product_4_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_4_out_product_4_reuse inter false
//         for (ap_int<32> tensor_weight_y_4_out_product_4_1 = 0; tensor_weight_y_4_out_product_4_1 < 2; ++tensor_weight_y_4_out_product_4_1) {
//           tensor_weight_y_4_out_product_4_reuse[tensor_weight_y_4_out_product_4_1][x] = tensor_weight_y_4_out_product_4_reuse[(tensor_weight_y_4_out_product_4_1 + 1)][x];
//         }
//         tensor_weight_y_4_out_product_4_reuse[2][x] = tensor_weight_y_4_out_product_4[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer18;
//         reducer18 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer18 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_4_out_product_4_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer18)));
//         }
//         tensor_weight_y_4_tensor_y_4[((x + (y_reuse * 1024)))] = reducer18;
//       }
//     }
//   }
// 
// static void tensor_weight_y_3(ap_fixed<32, 20>* tensor_weight_y_3_out_product_3, ap_fixed<32, 20>* tensor_weight_y_3_tensor_y_3) {
//     ap_fixed<32, 20> tensor_weight_y_3_out_product_3_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_3_out_product_3_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_3_out_product_3_reuse inter false
//         for (ap_int<32> tensor_weight_y_3_out_product_3_1 = 0; tensor_weight_y_3_out_product_3_1 < 2; ++tensor_weight_y_3_out_product_3_1) {
//           tensor_weight_y_3_out_product_3_reuse[tensor_weight_y_3_out_product_3_1][x] = tensor_weight_y_3_out_product_3_reuse[(tensor_weight_y_3_out_product_3_1 + 1)][x];
//         }
//         tensor_weight_y_3_out_product_3_reuse[2][x] = tensor_weight_y_3_out_product_3[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer17;
//         reducer17 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer17 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_3_out_product_3_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer17)));
//         }
//         tensor_weight_y_3_tensor_y_3[((x + (y_reuse * 1024)))] = reducer17;
//       }
//     }
//   }
// 
// static void tensor_weight_y_2(ap_fixed<32, 20>* tensor_weight_y_2_out_product_2, ap_fixed<32, 20>* tensor_weight_y_2_tensor_y_2) {
//     ap_fixed<32, 20> tensor_weight_y_2_out_product_2_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_2_out_product_2_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_2_out_product_2_reuse inter false
//         for (ap_int<32> tensor_weight_y_2_out_product_2_1 = 0; tensor_weight_y_2_out_product_2_1 < 2; ++tensor_weight_y_2_out_product_2_1) {
//           tensor_weight_y_2_out_product_2_reuse[tensor_weight_y_2_out_product_2_1][x] = tensor_weight_y_2_out_product_2_reuse[(tensor_weight_y_2_out_product_2_1 + 1)][x];
//         }
//         tensor_weight_y_2_out_product_2_reuse[2][x] = tensor_weight_y_2_out_product_2[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer16;
//         reducer16 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer16 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_2_out_product_2_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer16)));
//         }
//         tensor_weight_y_2_tensor_y_2[((x + (y_reuse * 1024)))] = reducer16;
//       }
//     }
//   }
// 
// static void tensor_weight_y_1(ap_fixed<32, 20>* tensor_weight_y_1_out_product_1, ap_fixed<32, 20>* tensor_weight_y_1_tensor_y_1) {
//     ap_fixed<32, 20> tensor_weight_y_1_out_product_1_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_1_out_product_1_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_1_out_product_1_reuse inter false
//         for (ap_int<32> tensor_weight_y_1_out_product_1_1 = 0; tensor_weight_y_1_out_product_1_1 < 2; ++tensor_weight_y_1_out_product_1_1) {
//           tensor_weight_y_1_out_product_1_reuse[tensor_weight_y_1_out_product_1_1][x] = tensor_weight_y_1_out_product_1_reuse[(tensor_weight_y_1_out_product_1_1 + 1)][x];
//         }
//         tensor_weight_y_1_out_product_1_reuse[2][x] = tensor_weight_y_1_out_product_1[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer15;
//         reducer15 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer15 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_1_out_product_1_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer15)));
//         }
//         tensor_weight_y_1_tensor_y_1[((x + (y_reuse * 1024)))] = reducer15;
//       }
//     }
//   }
// 
// static void tensor_weight_y_0(ap_fixed<32, 20>* tensor_weight_y_0_out_product_0, ap_fixed<32, 20>* tensor_weight_y_0_tensor_y_0) {
//     ap_fixed<32, 20> tensor_weight_y_0_out_product_0_reuse[3][1024];
//     #pragma HLS array_partition variable=tensor_weight_y_0_out_product_0_reuse complete dim=1
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=tensor_weight_y_0_out_product_0_reuse inter false
//         for (ap_int<32> tensor_weight_y_0_out_product_0_1 = 0; tensor_weight_y_0_out_product_0_1 < 2; ++tensor_weight_y_0_out_product_0_1) {
//           tensor_weight_y_0_out_product_0_reuse[tensor_weight_y_0_out_product_0_1][x] = tensor_weight_y_0_out_product_0_reuse[(tensor_weight_y_0_out_product_0_1 + 1)][x];
//         }
//         tensor_weight_y_0_out_product_0_reuse[2][x] = tensor_weight_y_0_out_product_0[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer14;
//         reducer14 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_y = 0; rdx_y < 3; ++rdx_y) {
//           reducer14 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_y_0_out_product_0_reuse[(rdx_y)][x]) * t_w[rdx_y]) + ((ap_fixed<32, 20>)reducer14)));
//         }
//         tensor_weight_y_0_tensor_y_0[((x + (y_reuse * 1024)))] = reducer14;
//       }
//     }
//   }
// 
// static void tensor_weight_x_5(ap_fixed<32, 20>* tensor_weight_x_5_tensor_y_5, ap_fixed<32, 20>* tensor_weight_x_5_tensor_5) {
//     ap_fixed<32, 20> tensor_weight_x_5_tensor_y_5_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_5_tensor_y_5_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_5_tensor_y_5_0 = 0; tensor_weight_x_5_tensor_y_5_0 < 2; ++tensor_weight_x_5_tensor_y_5_0) {
//           tensor_weight_x_5_tensor_y_5_reuse[0][tensor_weight_x_5_tensor_y_5_0] = tensor_weight_x_5_tensor_y_5_reuse[0][(tensor_weight_x_5_tensor_y_5_0 + 1)];
//         }
//         tensor_weight_x_5_tensor_y_5_reuse[0][2] = tensor_weight_x_5_tensor_y_5[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer13;
//         reducer13 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer13 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_5_tensor_y_5_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer13)));
//         }
//         tensor_weight_x_5_tensor_5[((x_reuse + (y * 1024)))] = reducer13;
//       }
//     }
//   }
// 
// static void tensor_weight_x_4(ap_fixed<32, 20>* tensor_weight_x_4_tensor_y_4, ap_fixed<32, 20>* tensor_weight_x_4_tensor_4) {
//     ap_fixed<32, 20> tensor_weight_x_4_tensor_y_4_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_4_tensor_y_4_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_4_tensor_y_4_0 = 0; tensor_weight_x_4_tensor_y_4_0 < 2; ++tensor_weight_x_4_tensor_y_4_0) {
//           tensor_weight_x_4_tensor_y_4_reuse[0][tensor_weight_x_4_tensor_y_4_0] = tensor_weight_x_4_tensor_y_4_reuse[0][(tensor_weight_x_4_tensor_y_4_0 + 1)];
//         }
//         tensor_weight_x_4_tensor_y_4_reuse[0][2] = tensor_weight_x_4_tensor_y_4[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer12;
//         reducer12 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer12 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_4_tensor_y_4_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer12)));
//         }
//         tensor_weight_x_4_tensor_4[((x_reuse + (y * 1024)))] = reducer12;
//       }
//     }
//   }
// 
// static void tensor_weight_x_3(ap_fixed<32, 20>* tensor_weight_x_3_tensor_y_3, ap_fixed<32, 20>* tensor_weight_x_3_tensor_3) {
//     ap_fixed<32, 20> tensor_weight_x_3_tensor_y_3_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_3_tensor_y_3_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_3_tensor_y_3_0 = 0; tensor_weight_x_3_tensor_y_3_0 < 2; ++tensor_weight_x_3_tensor_y_3_0) {
//           tensor_weight_x_3_tensor_y_3_reuse[0][tensor_weight_x_3_tensor_y_3_0] = tensor_weight_x_3_tensor_y_3_reuse[0][(tensor_weight_x_3_tensor_y_3_0 + 1)];
//         }
//         tensor_weight_x_3_tensor_y_3_reuse[0][2] = tensor_weight_x_3_tensor_y_3[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer11;
//         reducer11 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer11 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_3_tensor_y_3_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer11)));
//         }
//         tensor_weight_x_3_tensor_3[((x_reuse + (y * 1024)))] = reducer11;
//       }
//     }
//   }
// 
// static void tensor_weight_x_2(ap_fixed<32, 20>* tensor_weight_x_2_tensor_y_2, ap_fixed<32, 20>* tensor_weight_x_2_tensor_2) {
//     ap_fixed<32, 20> tensor_weight_x_2_tensor_y_2_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_2_tensor_y_2_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_2_tensor_y_2_0 = 0; tensor_weight_x_2_tensor_y_2_0 < 2; ++tensor_weight_x_2_tensor_y_2_0) {
//           tensor_weight_x_2_tensor_y_2_reuse[0][tensor_weight_x_2_tensor_y_2_0] = tensor_weight_x_2_tensor_y_2_reuse[0][(tensor_weight_x_2_tensor_y_2_0 + 1)];
//         }
//         tensor_weight_x_2_tensor_y_2_reuse[0][2] = tensor_weight_x_2_tensor_y_2[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer10;
//         reducer10 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer10 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_2_tensor_y_2_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer10)));
//         }
//         tensor_weight_x_2_tensor_2[((x_reuse + (y * 1024)))] = reducer10;
//       }
//     }
//   }
// 
// static void tensor_weight_x_1(ap_fixed<32, 20>* tensor_weight_x_1_tensor_y_1, ap_fixed<32, 20>* tensor_weight_x_1_tensor_1) {
//     ap_fixed<32, 20> tensor_weight_x_1_tensor_y_1_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_1_tensor_y_1_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_1_tensor_y_1_0 = 0; tensor_weight_x_1_tensor_y_1_0 < 2; ++tensor_weight_x_1_tensor_y_1_0) {
//           tensor_weight_x_1_tensor_y_1_reuse[0][tensor_weight_x_1_tensor_y_1_0] = tensor_weight_x_1_tensor_y_1_reuse[0][(tensor_weight_x_1_tensor_y_1_0 + 1)];
//         }
//         tensor_weight_x_1_tensor_y_1_reuse[0][2] = tensor_weight_x_1_tensor_y_1[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer9;
//         reducer9 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer9 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_1_tensor_y_1_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer9)));
//         }
//         tensor_weight_x_1_tensor_1[((x_reuse + (y * 1024)))] = reducer9;
//       }
//     }
//   }
// 
// static void tensor_weight_x_0(ap_fixed<32, 20>* tensor_weight_x_0_tensor_y_0, ap_fixed<32, 20>* tensor_weight_x_0_tensor_0) {
//     ap_fixed<32, 20> tensor_weight_x_0_tensor_y_0_reuse[1][3];
//     #pragma HLS array_partition variable=tensor_weight_x_0_tensor_y_0_reuse complete dim=2
//     ap_fixed<32, 20> t_w[3];
//     t_w[0] = 3.243000e-01f;
//     t_w[1] = 3.513000e-01f;
//     t_w[2] = 3.243000e-01f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//         for (ap_int<32> tensor_weight_x_0_tensor_y_0_0 = 0; tensor_weight_x_0_tensor_y_0_0 < 2; ++tensor_weight_x_0_tensor_y_0_0) {
//           tensor_weight_x_0_tensor_y_0_reuse[0][tensor_weight_x_0_tensor_y_0_0] = tensor_weight_x_0_tensor_y_0_reuse[0][(tensor_weight_x_0_tensor_y_0_0 + 1)];
//         }
//         tensor_weight_x_0_tensor_y_0_reuse[0][2] = tensor_weight_x_0_tensor_y_0[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer8;
//         reducer8 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx_x = 0; rdx_x < 3; ++rdx_x) {
//           reducer8 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)tensor_weight_x_0_tensor_y_0_reuse[0][(rdx_x)]) * t_w[rdx_x]) + ((ap_fixed<32, 20>)reducer8)));
//         }
//         tensor_weight_x_0_tensor_0[((x_reuse + (y * 1024)))] = reducer8;
//       }
//     }
//   }
// 
// static void outer_product(ap_fixed<32, 20>* outer_product_filt_grad_0, ap_fixed<32, 20>* outer_product_filt_grad_1, ap_fixed<32, 20>* outer_product_filt_grad_2, ap_fixed<32, 20>* outer_product_out_product_0, ap_fixed<32, 20>* outer_product_out_product_1, ap_fixed<32, 20>* outer_product_out_product_2, ap_fixed<32, 20>* outer_product_out_product_3, ap_fixed<32, 20>* outer_product_out_product_4, ap_fixed<32, 20>* outer_product_out_product_5) {
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//         ap_fixed<32, 20> a;
//         a = outer_product_filt_grad_0[(x + (y * 1024))];
//         ap_fixed<32, 20> b;
//         b = outer_product_filt_grad_1[(x + (y * 1024))];
//         ap_fixed<32, 20> c;
//         c = outer_product_filt_grad_2[(x + (y * 1024))];
//         outer_product_out_product_0[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)a) * ((ap_fixed<64, 52>)a)));
//         outer_product_out_product_1[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)b) * ((ap_fixed<64, 52>)b)));
//         outer_product_out_product_2[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)c) * ((ap_fixed<64, 52>)c)));
//         outer_product_out_product_3[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)a) * ((ap_fixed<64, 52>)b)));
//         outer_product_out_product_4[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)a) * ((ap_fixed<64, 52>)c)));
//         outer_product_out_product_5[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<64, 52>)b) * ((ap_fixed<64, 52>)c)));
//       }
//     }
//   }
// 
// static void grad_weight_x_2(ap_fixed<32, 20>* grad_weight_x_2_y_filt_2, ap_fixed<32, 20>* grad_weight_x_2_filt_grad_2) {
//     ap_fixed<32, 20> grad_weight_x_2_y_filt_2_reuse[1][7];
//     #pragma HLS array_partition variable=grad_weight_x_2_y_filt_2_reuse complete dim=2
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//       #pragma HLS pipeline
//         for (ap_int<32> grad_weight_x_2_y_filt_2_0 = 0; grad_weight_x_2_y_filt_2_0 < 6; ++grad_weight_x_2_y_filt_2_0) {
//           grad_weight_x_2_y_filt_2_reuse[0][grad_weight_x_2_y_filt_2_0] = grad_weight_x_2_y_filt_2_reuse[0][(grad_weight_x_2_y_filt_2_0 + 1)];
//         }
//         grad_weight_x_2_y_filt_2_reuse[0][6] = grad_weight_x_2_y_filt_2[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer7;
//         reducer7 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer7 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_x_2_y_filt_2_reuse[0][(rdx)]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer7)));
//         }
//         grad_weight_x_2_filt_grad_2[((x_reuse + (y * 1024)))] = reducer7;
//       }
//     }
//   }
// 
// static void grad_weight_x_1(ap_fixed<32, 20>* grad_weight_x_1_y_filt_1, ap_fixed<32, 20>* grad_weight_x_1_filt_grad_1) {
//     ap_fixed<32, 20> grad_weight_x_1_y_filt_1_reuse[1][7];
//     #pragma HLS array_partition variable=grad_weight_x_1_y_filt_1_reuse complete dim=2
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//       #pragma HLS pipeline
//         for (ap_int<32> grad_weight_x_1_y_filt_1_0 = 0; grad_weight_x_1_y_filt_1_0 < 6; ++grad_weight_x_1_y_filt_1_0) {
//           grad_weight_x_1_y_filt_1_reuse[0][grad_weight_x_1_y_filt_1_0] = grad_weight_x_1_y_filt_1_reuse[0][(grad_weight_x_1_y_filt_1_0 + 1)];
//         }
//         grad_weight_x_1_y_filt_1_reuse[0][6] = grad_weight_x_1_y_filt_1[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer6;
//         reducer6 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer6 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_x_1_y_filt_1_reuse[0][(rdx)]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer6)));
//         }
//         grad_weight_x_1_filt_grad_1[((x_reuse + (y * 1024)))] = reducer6;
//       }
//     }
//   }
// 
// static void grad_weight_x_0(ap_fixed<32, 20>* grad_weight_x_0_y_filt_0, ap_fixed<32, 20>* grad_weight_x_0_filt_grad_0) {
//     ap_fixed<32, 20> grad_weight_x_0_y_filt_0_reuse[1][7];
//     #pragma HLS array_partition variable=grad_weight_x_0_y_filt_0_reuse complete dim=2
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
//       #pragma HLS pipeline
//         for (ap_int<32> grad_weight_x_0_y_filt_0_0 = 0; grad_weight_x_0_y_filt_0_0 < 6; ++grad_weight_x_0_y_filt_0_0) {
//           grad_weight_x_0_y_filt_0_reuse[0][grad_weight_x_0_y_filt_0_0] = grad_weight_x_0_y_filt_0_reuse[0][(grad_weight_x_0_y_filt_0_0 + 1)];
//         }
//         grad_weight_x_0_y_filt_0_reuse[0][6] = grad_weight_x_0_y_filt_0[(x_reuse + (y * 1024))];
//         ap_fixed<32, 20> reducer5;
//         reducer5 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer5 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_x_0_y_filt_0_reuse[0][(rdx)]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer5)));
//         }
//         grad_weight_x_0_filt_grad_0[((x_reuse + (y * 1024)))] = reducer5;
//       }
//     }
//   }
// 
// static void grad_weight_y_2(ap_fixed<32, 20>* grad_weight_y_2_grad_z, ap_fixed<32, 20>* grad_weight_y_2_y_filt_2) {
//     ap_fixed<32, 20> grad_weight_y_2_grad_z_reuse[7][1024];
//     #pragma HLS array_partition variable=grad_weight_y_2_grad_z_reuse complete dim=1
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=grad_weight_y_2_grad_z_reuse inter false
//         for (ap_int<32> grad_weight_y_2_grad_z_1 = 0; grad_weight_y_2_grad_z_1 < 6; ++grad_weight_y_2_grad_z_1) {
//           grad_weight_y_2_grad_z_reuse[grad_weight_y_2_grad_z_1][x] = grad_weight_y_2_grad_z_reuse[(grad_weight_y_2_grad_z_1 + 1)][x];
//         }
//         grad_weight_y_2_grad_z_reuse[6][x] = grad_weight_y_2_grad_z[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer4;
//         reducer4 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer4 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_y_2_grad_z_reuse[(rdx)][x]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer4)));
//         }
//         grad_weight_y_2_y_filt_2[((x + (y_reuse * 1024)))] = reducer4;
//       }
//     }
//   }
// 
// static void grad_weight_y_1(ap_fixed<32, 20>* grad_weight_y_1_grad_y, ap_fixed<32, 20>* grad_weight_y_1_y_filt_1) {
//     ap_fixed<32, 20> grad_weight_y_1_grad_y_reuse[7][1024];
//     #pragma HLS array_partition variable=grad_weight_y_1_grad_y_reuse complete dim=1
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=grad_weight_y_1_grad_y_reuse inter false
//         for (ap_int<32> grad_weight_y_1_grad_y_1 = 0; grad_weight_y_1_grad_y_1 < 6; ++grad_weight_y_1_grad_y_1) {
//           grad_weight_y_1_grad_y_reuse[grad_weight_y_1_grad_y_1][x] = grad_weight_y_1_grad_y_reuse[(grad_weight_y_1_grad_y_1 + 1)][x];
//         }
//         grad_weight_y_1_grad_y_reuse[6][x] = grad_weight_y_1_grad_y[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer3;
//         reducer3 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer3 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_y_1_grad_y_reuse[(rdx)][x]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer3)));
//         }
//         grad_weight_y_1_y_filt_1[((x + (y_reuse * 1024)))] = reducer3;
//       }
//     }
//   }
// 
// static void grad_weight_y_0(ap_fixed<32, 20>* grad_weight_y_0_grad_x, ap_fixed<32, 20>* grad_weight_y_0_y_filt_0) {
//     ap_fixed<32, 20> grad_weight_y_0_grad_x_reuse[7][1024];
//     #pragma HLS array_partition variable=grad_weight_y_0_grad_x_reuse complete dim=1
//     ap_fixed<32, 20> g_f[7];
//     g_f[0] = 7.550000e-02f;
//     g_f[1] = 1.330000e-01f;
//     g_f[2] = 1.869000e-01f;
//     g_f[3] = 2.903000e-01f;
//     g_f[4] = 1.869000e-01f;
//     g_f[5] = 1.330000e-01f;
//     g_f[6] = 7.550000e-02f;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=grad_weight_y_0_grad_x_reuse inter false
//         for (ap_int<32> grad_weight_y_0_grad_x_1 = 0; grad_weight_y_0_grad_x_1 < 6; ++grad_weight_y_0_grad_x_1) {
//           grad_weight_y_0_grad_x_reuse[grad_weight_y_0_grad_x_1][x] = grad_weight_y_0_grad_x_reuse[(grad_weight_y_0_grad_x_1 + 1)][x];
//         }
//         grad_weight_y_0_grad_x_reuse[6][x] = grad_weight_y_0_grad_x[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer2;
//         reducer2 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdx = 0; rdx < 7; ++rdx) {
//           reducer2 = ((ap_fixed<32, 20>)((((ap_fixed<32, 20>)grad_weight_y_0_grad_x_reuse[(rdx)][x]) * g_f[rdx]) + ((ap_fixed<32, 20>)reducer2)));
//         }
//         grad_weight_y_0_y_filt_0[((x + (y_reuse * 1024)))] = reducer2;
//       }
//     }
//   }
// 
// static void calc_z_gradient(ap_fixed<32, 20>* calc_z_gradient_img0, ap_fixed<32, 20>* calc_z_gradient_img1, ap_fixed<32, 20>* calc_z_gradient_img2_0, ap_fixed<32, 20>* calc_z_gradient_img3, ap_fixed<32, 20>* calc_z_gradient_img4, ap_fixed<32, 20>* calc_z_gradient_grad_z) {
//     ap_int<32> g_w[5];
//     g_w[0] = 1;
//     g_w[1] = -8;
//     g_w[2] = 0;
//     g_w[3] = 8;
//     g_w[4] = 1;
//     for (ap_int<32> y = 0; y < 436; ++y) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//         calc_z_gradient_grad_z[(x + (y * 1024))] = ((ap_fixed<32, 20>)(((ap_fixed<32, 20>)(((ap_fixed<68, 56>)(((ap_fixed<67, 55>)(((ap_fixed<66, 54>)(((ap_fixed<65, 53>)(((ap_fixed<64, 52>)calc_z_gradient_img0[(x + (y * 1024))]) * ((ap_int<64>)g_w[0]))) + ((ap_fixed<65, 53>)(((ap_fixed<64, 52>)calc_z_gradient_img1[(x + (y * 1024))]) * ((ap_int<64>)g_w[1]))))) + ((ap_fixed<66, 54>)(((ap_fixed<64, 52>)calc_z_gradient_img2_0[(x + (y * 1024))]) * ((ap_int<64>)g_w[2]))))) + ((ap_fixed<67, 55>)(((ap_fixed<64, 52>)calc_z_gradient_img3[(x + (y * 1024))]) * ((ap_int<64>)g_w[3]))))) + ((ap_fixed<68, 56>)(((ap_fixed<64, 52>)calc_z_gradient_img4[(x + (y * 1024))]) * ((ap_int<64>)g_w[4]))))) / 12));
//       }
//     }
//   }
// 
// static void calc_y_gradient(ap_fixed<32, 20>* calc_y_gradient_input_image_1, ap_fixed<32, 20>* calc_y_gradient_grad_y) {
//     ap_fixed<32, 20> calc_y_gradient_input_image_1_reuse[5][1024];
//     #pragma HLS array_partition variable=calc_y_gradient_input_image_1_reuse complete dim=1
//     ap_int<32> g_w[5];
//     g_w[0] = 1;
//     g_w[1] = -8;
//     g_w[2] = 0;
//     g_w[3] = 8;
//     g_w[4] = 1;
//     for (ap_int<32> y_reuse = 0; y_reuse < 436; ++y_reuse) {
//       for (ap_int<32> x = 0; x < 1024; ++x) {
//       #pragma HLS pipeline
//       #pragma HLS dependence variable=calc_y_gradient_input_image_1_reuse inter false
//         for (ap_int<32> calc_y_gradient_input_image_1_1 = 0; calc_y_gradient_input_image_1_1 < 4; ++calc_y_gradient_input_image_1_1) {
//           calc_y_gradient_input_image_1_reuse[calc_y_gradient_input_image_1_1][x] = calc_y_gradient_input_image_1_reuse[(calc_y_gradient_input_image_1_1 + 1)][x];
//         }
//         calc_y_gradient_input_image_1_reuse[4][x] = calc_y_gradient_input_image_1[(x + (y_reuse * 1024))];
//         ap_fixed<32, 20> reducer1;
//         reducer1 = ((ap_fixed<32, 20>)0);
//         for (ap_int<32> rdy = 0; rdy < 5; ++rdy) {
//           reducer1 = ((ap_fixed<32, 20>)(((ap_fixed<65, 53>)(((ap_fixed<64, 52>)calc_y_gradient_input_image_1_reuse[(rdy)][x]) * ((ap_int<64>)g_w[rdy]))) + ((ap_fixed<65, 53>)reducer1)));
//         }
//         calc_y_gradient_grad_y[((x + (y_reuse * 1024)))] = reducer1;
//       }
//     }
//   }

static void calc_x_gradient(ap_fixed<32, 20>* calc_x_gradient_input_image_0, ap_fixed<32, 20>* calc_x_gradient_grad_x) {
    ap_fixed<32, 20> calc_x_gradient_input_image_0_reuse[1][5];
    #pragma HLS array_partition variable=calc_x_gradient_input_image_0_reuse complete dim=2
    ap_int<32> g_w[5];
    g_w[0] = 1;
    g_w[1] = -8;
    g_w[2] = 0;
    g_w[3] = 8;
    g_w[4] = 1;
    for (ap_int<32> y = 0; y < 436; ++y) {
      for (ap_int<32> x_reuse = 0; x_reuse < 1024; ++x_reuse) {
      #pragma HLS pipeline
        for (ap_int<32> calc_x_gradient_input_image_0_0 = 0; calc_x_gradient_input_image_0_0 < 4; ++calc_x_gradient_input_image_0_0) {
          calc_x_gradient_input_image_0_reuse[0][calc_x_gradient_input_image_0_0] = calc_x_gradient_input_image_0_reuse[0][(calc_x_gradient_input_image_0_0 + 1)];
        }
        calc_x_gradient_input_image_0_reuse[0][4] = calc_x_gradient_input_image_0[(x_reuse + (y * 1024))];
        ap_fixed<32, 20> reducer0;
        reducer0 = ((ap_fixed<32, 20>)0);
        for (ap_int<32> rdx = 0; rdx < 5; ++rdx) {
          reducer0 = ((ap_fixed<32, 20>)(((ap_fixed<65, 53>)(((ap_fixed<64, 52>)calc_x_gradient_input_image_0_reuse[0][(rdx)]) * ((ap_int<64>)g_w[rdx]))) + ((ap_fixed<65, 53>)reducer0)));
        }
        calc_x_gradient_grad_x[((x_reuse + (y * 1024)))] = reducer0;
      }
    }
  }

extern "C" {
    void top_function_0(ap_fixed<32, 20>* input_image0, ap_fixed<32, 20>* input_image1, ap_fixed<32, 20>* input_image2_0, ap_fixed<32, 20>* input_image2_1, ap_fixed<32, 20>* input_image2, ap_fixed<32, 20>* input_image3, ap_fixed<32, 20>* input_image4, ap_fixed<32, 20>* output_image_0, ap_fixed<32, 20>* output_image_1) {
    #pragma HLS INTERFACE m_axi port=input_image0 offset=slave bundle=gmem0
    #pragma HLS INTERFACE m_axi port=input_image1 offset=slave bundle=gmem1
    #pragma HLS INTERFACE m_axi port=input_image2_0 offset=slave bundle=gmem2
    #pragma HLS INTERFACE m_axi port=input_image2_1 offset=slave bundle=gmem3
    #pragma HLS INTERFACE m_axi port=input_image2 offset=slave bundle=gmem4
    #pragma HLS INTERFACE m_axi port=input_image3 offset=slave bundle=gmem5
    #pragma HLS INTERFACE m_axi port=input_image4 offset=slave bundle=gmem6
    #pragma HLS INTERFACE m_axi port=output_image_0 offset=slave bundle=gmem7
    #pragma HLS INTERFACE m_axi port=output_image_1 offset=slave bundle=gmem8
    #pragma HLS INTERFACE s_axilite port=input_image0 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image1 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image2_0 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image2_1 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image2 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image3 bundle=control
    #pragma HLS INTERFACE s_axilite port=input_image4 bundle=control
    #pragma HLS INTERFACE s_axilite port=output_image_0 bundle=control
    #pragma HLS INTERFACE s_axilite port=output_image_1 bundle=control
    #pragma HLS INTERFACE s_axilite port=return bundle=control

    // #pragma HLS dataflow
      ap_fixed<32, 20> grad_x[446464];
      // #pragma HLS stream variable=grad_x depth=1024
      calc_x_gradient(input_image2_0, grad_x);
      // ap_fixed<32, 20> grad_y[446464];
      // #pragma HLS stream variable=grad_y depth=1024
      // calc_y_gradient(input_image2_1, grad_y);
      // ap_fixed<32, 20> grad_z[446464];
      // #pragma HLS stream variable=grad_z depth=1024
      // calc_z_gradient(input_image0, input_image1, input_image2, input_image3, input_image4, grad_z);
      // ap_fixed<32, 20> y_filt_0[446464];
      // #pragma HLS stream variable=y_filt_0 depth=1024
      // grad_weight_y_0(grad_x, y_filt_0);
      // ap_fixed<32, 20> y_filt_1[446464];
      // #pragma HLS stream variable=y_filt_1 depth=1024
      // grad_weight_y_1(grad_y, y_filt_1);
      // ap_fixed<32, 20> y_filt_2[446464];
      // #pragma HLS stream variable=y_filt_2 depth=1024
      // grad_weight_y_2(grad_z, y_filt_2);
      // ap_fixed<32, 20> filt_grad_0[446464];
      // #pragma HLS stream variable=filt_grad_0 depth=1024
      // grad_weight_x_0(y_filt_0, filt_grad_0);
      // ap_fixed<32, 20> filt_grad_1[446464];
      // #pragma HLS stream variable=filt_grad_1 depth=1024
      // grad_weight_x_1(y_filt_1, filt_grad_1);
      // ap_fixed<32, 20> filt_grad_2[446464];
      // #pragma HLS stream variable=filt_grad_2 depth=1024
      // grad_weight_x_2(y_filt_2, filt_grad_2);
      // ap_fixed<32, 20> out_product_1[446464];
      // #pragma HLS stream variable=out_product_1 depth=1024
      // ap_fixed<32, 20> out_product_4[446464];
      // #pragma HLS stream variable=out_product_4 depth=1024
      // ap_fixed<32, 20> out_product_3[446464];
      // #pragma HLS stream variable=out_product_3 depth=1024
      // ap_fixed<32, 20> out_product_2[446464];
      // #pragma HLS stream variable=out_product_2 depth=1024
      // ap_fixed<32, 20> out_product_5[446464];
      // #pragma HLS stream variable=out_product_5 depth=1024
      // ap_fixed<32, 20> out_product_0[446464];
      // #pragma HLS stream variable=out_product_0 depth=1024
      // outer_product(filt_grad_0, filt_grad_1, filt_grad_2, out_product_0, out_product_1, out_product_2, out_product_3, out_product_4, out_product_5);
      // ap_fixed<32, 20> tensor_y_0[446464];
      // #pragma HLS stream variable=tensor_y_0 depth=1024
      // tensor_weight_y_0(out_product_0, tensor_y_0);
      // ap_fixed<32, 20> tensor_y_1[446464];
      // #pragma HLS stream variable=tensor_y_1 depth=1024
      // tensor_weight_y_1(out_product_1, tensor_y_1);
      // ap_fixed<32, 20> tensor_y_2[446464];
      // #pragma HLS stream variable=tensor_y_2 depth=1024
      // tensor_weight_y_2(out_product_2, tensor_y_2);
      // ap_fixed<32, 20> tensor_y_3[446464];
      // #pragma HLS stream variable=tensor_y_3 depth=1024
      // tensor_weight_y_3(out_product_3, tensor_y_3);
      // ap_fixed<32, 20> tensor_y_4[446464];
      // #pragma HLS stream variable=tensor_y_4 depth=1024
      // tensor_weight_y_4(out_product_4, tensor_y_4);
      // ap_fixed<32, 20> tensor_y_5[446464];
      // #pragma HLS stream variable=tensor_y_5 depth=1024
      // tensor_weight_y_5(out_product_5, tensor_y_5);
      // ap_fixed<32, 20> tensor_0[446464];
      // #pragma HLS stream variable=tensor_0 depth=1024
      // tensor_weight_x_0(tensor_y_0, tensor_0);
      // ap_fixed<32, 20> tensor_1[446464];
      // #pragma HLS stream variable=tensor_1 depth=1024
      // tensor_weight_x_1(tensor_y_1, tensor_1);
      // ap_fixed<32, 20> tensor_2[446464];
      // #pragma HLS stream variable=tensor_2 depth=1024
      // tensor_weight_x_2(tensor_y_2, tensor_2);
      // ap_fixed<32, 20> tensor_3[446464];
      // #pragma HLS stream variable=tensor_3 depth=1024
      // tensor_weight_x_3(tensor_y_3, tensor_3);
      // ap_fixed<32, 20> tensor_4[446464];
      // #pragma HLS stream variable=tensor_4 depth=1024
      // tensor_weight_x_4(tensor_y_4, tensor_4);
      // ap_fixed<32, 20> tensor_5[446464];
      // #pragma HLS stream variable=tensor_5 depth=1024
      // tensor_weight_x_5(tensor_y_5, tensor_5);
      // flow_calc(tensor_0, tensor_1, tensor_2, tensor_3, tensor_4, tensor_5, output_image_0, output_image_1);
    }
}

