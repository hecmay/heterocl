import heterocl as hcl
import numpy as np
import hlib

def test1():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute((10, 8), lambda y, x: A[y, x] + A[y, x+1] + A[y, x+2])
    s = hcl.create_schedule([A, B])
    RB = s.reuse_at(A, s[B], B.axis[1])
    print(hcl.lower(s))

def test2():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute((10, 8), lambda y, x: A[y, x] + A[y, x+1] + A[y, x+2])
    s = hcl.create_schedule([A, B])
    # read cache for A
    # CA = s.cache_read(A, "global")
    # RB = s.reuse_at(A, s[B], B.axis[1])
    print(hcl.lower(s))

def test3():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute((10, 8), lambda y, x: A[y, x] + A[y, x+1] + A[y, x+2], name="B")
    C = hcl.compute((10,8), lambda y, x: A[y,x])
    s = hcl.create_schedule([A, B])
    s.reshape(C, (5,2,2,4))
    print(hcl.lower(s))

def test4():
    hcl.init()
    A = hcl.placeholder((10, 10))
    r = hcl.reduce_axis(0, 3)
    c = hcl.reduce_axis(0, 3)
    B = hcl.compute((8, 8), lambda y, x: hcl.sum(A[y+r, x+c], axis=[r, c]),name="B")
    s = hcl.create_schedule([A, B])
    xo, xi = s[B].split(B.axis[1], 4)
    # s[B].reorder(xo, B.axis[0], xi)
    # LB = s.reuse_at(A, s[B], B.axis[0])
    # WB = s.reuse_at(LB, s[B], xi)
    # s.partition(LB, dim=2)
    # s.partition(WB)
    # s.reshape(B, (8, 2, 4))
    s[B].pipeline(B.axis[0])
    s[B].reorder(xi, xo)
    print(hcl.lower(s))

def test5():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute(A.shape, lambda x, y: A[x, y], "B")
    C = hcl.compute(A.shape, lambda x, y: B[x, y], "C")
    s = hcl.create_schedule([A, C])
    s.reshape(B, (2, 5, 2, 5))
    ir = str(hcl.lower(s))
    print(ir)

def test_conv2D_lb_wb_schedule():
    hcl.init()
    A = hcl.placeholder((10, 10))

def test_conv():
    hcl.init()
    batch = 100

    # sobel + reusable conv2d
    def kernel(A, K1, K2, B): 
      # (in, out, filter, num_in, num_out, width)
      C = hcl.compute()
      hlib.function.conv2d_ncwh(A, B, K1)

    A  = hcl.placeholder((10, 10), "A")
    B  = hcl.placeholder((10, 10), "B")
    K1 = hcl.placeholder((10, 10), "K1")
    K2 = hcl.placeholder((10, 10), "K2")

# test1()
# test2()
# test3()
test4()
# test5()

