import heterocl as hcl
import hlib
import numpy as np
import os, sys
from PIL import Image
# np.set_printoptions(threshold=sys.maxsize)

# height x width
size = (436, 1024)
height, width = size
hcl.init(hcl.Float(32))
dtype = hcl.Float(32)

# setup target using vivado 
tool = hcl.tool.sdaccel
tool.mode = "hw_emu"
os.environ["AWS_PLATFORM"] = "xilinx_vcu1525_dynamic_5_1"
target = hcl.platform.aws_f1(tool)
target.xcel.lang = "vhls"
# target = "llvm"

# load ppm image amd convert to grayscale
img0 = Image.open("datasets/current/frame1.ppm").convert("L")
img1 = Image.open("datasets/current/frame2.ppm").convert("L") 
img2 = Image.open("datasets/current/frame3.ppm").convert("L")
img3 = Image.open("datasets/current/frame4.ppm").convert("L")
img4 = Image.open("datasets/current/frame5.ppm").convert("L")

img0 = np.asarray(img0.getdata(), dtype=np.uint32).reshape(img0.size[1], img0.size[0]) 
img1 = np.asarray(img1.getdata(), dtype=np.uint32).reshape(img1.size[1], img1.size[0]) 
img2 = np.asarray(img2.getdata(), dtype=np.uint32).reshape(img2.size[1], img2.size[0]) 
img3 = np.asarray(img3.getdata(), dtype=np.uint32).reshape(img3.size[1], img3.size[0]) 
img4 = np.asarray(img4.getdata(), dtype=np.uint32).reshape(img4.size[1], img4.size[0]) 
imgs = [img0, img1, img2, img3, img4]


def optical_flow(target=target):

    image0 = hcl.placeholder((436,1024), "input_image0")
    image1 = hcl.placeholder((436,1024), "input_image1")
    image2 = hcl.placeholder((436,1024), "input_image2")
    image3 = hcl.placeholder((436,1024), "input_image3")
    image4 = hcl.placeholder((436,1024), "input_image4")
    g_w = hcl.placeholder((5,), "grad_weight")
    g_f = hcl.placeholder((7,), "grad_filter")
    t_f = hcl.placeholder((3,), "tensor_filter")
    output = hcl.placeholder((436,1024,2), "output_image")

    def kernel(img0, img1, img2, img3, img4, g_w, g_f, t_f, output):

       sum = hcl.reducer(0, lambda x, y: x + y, dtype="float")

       @hcl.def_([size, (5,), size, size])
       def calc_xy_gradient(input_image, g_w, out_x, out_y):
           rx = hcl.reduce_axis(0, 5, name="rdx")
           ry = hcl.reduce_axis(0, 5, name="rdy")
           def update(y, x):
               with hcl.if_(hcl.and_(y>=2, y<height-2, x>=2, x<width-2)):
                   out_x[y,x] = sum(input_image[y, x-rx+2] * g_w[rx], axis=rx)
                   out_y[y,x] = sum(input_image[y-ry+2, x] * g_w[ry], axis=ry)
           hcl.mutate(size, lambda y, x: update(y, x))
           
       @hcl.def_([size, size, size, size, size, (5,), size])
       def calc_z_gradient(img0, img1, img2, img3, img4, g_w, grad_z):
           hcl.update(grad_z, 
               lambda y, x: (img0[y,x] * g_w[0] +
                             img1[y,x] * g_w[1] +
                             img2[y,x] * g_w[2] +
                             img3[y,x] * g_w[3] +
                             img4[y,x] * g_w[4]) / 12.0)

       # averaging gradients in y dim
       @hcl.def_([size, size, size, (7,), (436,1024,3)])
       def grad_weight_y(grad_x, grad_y, grad_z, g_f, y_filt):
           rd = hcl.reduce_axis(0, 7, name="rdx")
           def acc(y, x, c):
               with hcl.if_(hcl.and_(y>=3, y<height-3)):
                   y_filt[y, x, c] = sum(hcl.select(c==0, grad_x[y-rd+3,x],
                               hcl.select(c==1, grad_y[y-rd+3,x],
                               grad_z[y-rd+3,x])) * g_f[rd], axis=rd)
           hcl.mutate(y_filt.shape, lambda y, x, c: acc(y, x, c))


       @hcl.def_([(436,1024,3), (7,), (436,1024,3)])
       def grad_weight_x(y_filt, g_f, filt_grad):
           rd = hcl.reduce_axis(0, 7, name="rdx")
           def acc(y, x, c):
               with hcl.if_(hcl.and_(x>=3, x<width-3)):
                   filt_grad[y, x, c] = sum(y_filt[y, x-rd+3, c] * g_f[rd], axis=rd)
           hcl.mutate(filt_grad.shape, lambda y, x, c: acc(y, x, c))
               

       @hcl.def_([(436,1024,3), (436,1024,6)])
       def outer_product(filt_grad, outer):
           hcl.update(outer, 
               lambda y, x, c: 
                   hcl.select(c==0, filt_grad[y,x,0] * filt_grad[y,x,0],
                   hcl.select(c==1, filt_grad[y,x,1] * filt_grad[y,x,1],
                   hcl.select(c==2, filt_grad[y,x,2] * filt_grad[y,x,2],
                   hcl.select(c==3, filt_grad[y,x,0] * filt_grad[y,x,1],
                   hcl.select(c==4, filt_grad[y,x,0] * filt_grad[y,x,2], 
                                    filt_grad[y,x,1] * filt_grad[y,x,2]))))))

       @hcl.def_([(436,1024,6), (3,), (436,1024,6)])
       def tensor_weight_x(tensor_y, t_w, tensor):
           rd = hcl.reduce_axis(0, 3, name="rdx_x")
           def acc(y, x, c):
               out = hcl.scalar(0, "out")
               with hcl.if_(hcl.and_(x>=1, x<width-1)):
                   out.v = sum(tensor_y[y,x-rd+1,c] * t_w[rd], axis=rd)
               return out.v
           hcl.update(tensor, lambda y, x, c: acc(y, x, c))


       @hcl.def_([(436,1024,6), (3,), (436,1024,6)])
       def tensor_weight_y(outer, t_w, tensor_y):
           rd = hcl.reduce_axis(0, 3, name="rdx_y")
           def acc(y, x, c):
               out = hcl.scalar(0, "out")
               with hcl.if_(hcl.and_(y>=1, y<height-1)):
                   out.v = sum(outer[y-rd+1,x,c] * t_w[rd], axis=rd)
               return out.v
           hcl.update(tensor_y, lambda y, x, c: acc(y, x, c))


       @hcl.def_([(436,1024,6), (436,1024,2)])
       def flow_calc(tensor, output):
           with hcl.for_(0, height, name="r") as r:
             with hcl.for_(0, width, name="c") as c:
               with hcl.if_(hcl.and_(r>=2, r<height-2, c>=2, c<width-2)):
                 s0 = hcl.scalar(0, "denom")
                 s0.v = tensor[r,c,0]*tensor[r,c,1] - tensor[r,c,3]*tensor[r,c,3]
                 output[r,c,0] = (tensor[r,c,5]*tensor[r,c,3]-tensor[r,c,1]*tensor[r,c,4]) / s0.v
                 output[r,c,1] = (tensor[r,c,4]*tensor[r,c,3]-tensor[r,c,5]*tensor[r,c,0]) / s0.v

       # def pack(y, x):
       #     out = hcl.scalar(0, "packed", dtype=hcl.UFixed(40))    
       #     out.v[1:8]   = img0[y, x]
       #     out.v[9:16]  = img1[y, x]
       #     out.v[17:24] = img2[y, x]
       #     out.v[25:32] = img3[y, x]
       #     out.v[33:40] = img4[y, x]
       #     return out.v
       #     
       # frames = hcl.compute((height, width), lambda y, x: 
       #              pack(y, x), dtype=hcl.UFixed(40), name="frames")

       # # unpack data 
       # i0 = hcl.compute((height, width), lambda *args: frames[args][1:8], "i0")
       # i1 = hcl.compute((height, width), lambda *args: frames[args][2:16], "i1")
       # i2 = hcl.compute((height, width), lambda *args: frames[args][17:24], "i2")
       # i3 = hcl.compute((height, width), lambda *args: frames[args][25:32], "i3")
       # i4 = hcl.compute((height, width), lambda *args: frames[args][33:40], "i4")

       init = lambda *args: 0
       grad_x = hcl.compute(size, init, name="grad_x")
       grad_y = hcl.compute(size, init, name="grad_y")
       grad_z = hcl.compute(size, init, name="grad_z")
       y_filt      = hcl.compute((436,1024,3), init, name="y_filt")
       filt_grad   = hcl.compute((436,1024,3), init, name="filt_grad")
       out_product = hcl.compute((436,1024,6), init, name="outer")
       tensor_y = hcl.compute((436,1024,6), init, name="tensor_y")
       tensor   = hcl.compute((436,1024,6), init, name="tensor")

       calc_xy_gradient(image2, g_w, grad_x, grad_y)
       calc_z_gradient(image0, image1, image2, image3, image4, g_w, grad_z)

       grad_weight_y(grad_x, grad_y, grad_z, g_f, y_filt)
       grad_weight_x(y_filt, g_f, filt_grad)

       outer_product(filt_grad, out_product)
       tensor_weight_y(out_product, t_f, tensor_y)
       tensor_weight_x(tensor_y, t_f, tensor)
       flow_calc(tensor, output)

    s = hcl.create_schedule([image0, image1, image2, image3, image4, g_w, 
                             g_f, t_f, output], kernel)

    if target != "llvm":

      # transmit packed data to device 
      # s.to(kernel.frames, target.xcel, occ=1)
      s.to([image4, image3, image2, image1, image0], target.xcel)
      s.to(output, target.host)

      k_grad_xy   = kernel.calc_xy_gradient
      k_grad_z    = kernel.calc_z_gradient
      k_grad_y    = kernel.grad_weight_y
      k_grad_x    = kernel.grad_weight_x
      k_outer     = kernel.outer_product
      k_tensor_x  = kernel.tensor_weight_x
      k_tensor_y  = kernel.tensor_weight_y
      k_calc_flow = kernel.flow_calc

      # creat streaming channels + reuse buffer
      # s.reuse_at(k_grad_x.y_filt, s[k_grad_x], k_grad_x.axis[1])
      # s.reuse_at(k_grad_y.grad_x, s[k_grad_y], k_grad_y.axis[1])
      s.to(kernel.y_filt, 
           s[k_grad_x], s[k_grad_y], hcl.Stream.FIFO)
      s.to(kernel.filt_grad, 
           s[k_outer], s[k_grad_x], hcl.Stream.FIFO)
      s.to(kernel.outer, 
           s[k_tensor_y], s[k_outer], hcl.Stream.FIFO)
      s.to(kernel.tensor_y, 
           s[k_tensor_x], s[k_tensor_y], hcl.Stream.FIFO)
      s.to(kernel.tensor, 
           s[k_calc_flow], s[k_tensor_x], hcl.Stream.FIFO)

      # pipeline streaming rd/wr 
      s[k_grad_xy].pipeline(k_grad_xy.axis[1])
      s[k_grad_z].pipeline(k_grad_z.axis[1])
      s[k_grad_x].pipeline(k_grad_x.axis[1])
      s[k_grad_y].pipeline(k_grad_y.axis[1])
      s[k_tensor_x].pipeline(k_tensor_x.axis[1])
      s[k_tensor_y].pipeline(k_tensor_y.axis[1])

    print(hcl.lower(s))
    return hcl.build(s, target)

g_w = hcl.asarray(np.array([-1, -8, 0, 8, 1]), dtype)
g_f = hcl.asarray(np.array([0.0755, 0.133, 0.1869, 0.2903, 0.1869, 0.133, 0.0755]), dtype)
t_f = hcl.asarray(np.array([0.3243, 0.3513, 0.3243]), dtype)
hcl_output = hcl.asarray(np.zeros((463,1024,2)), dtype)    
hcl_grad_x = hcl.asarray(np.zeros((463,1024,6)), dtype)    
imgs = [hcl.asarray(_) for _ in imgs]

f = optical_flow(target)
f(*imgs, g_w, g_f, t_f, hcl_output)
print(hcl_output.asnumpy())
print(hcl_grad_x.asnumpy())
