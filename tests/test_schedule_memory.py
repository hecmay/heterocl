import heterocl as hcl
import numpy as np

def test_reuse_blur_x():
    hcl.init()
    A = hcl.placeholder((10, 10))
    B = hcl.compute((10, 8), lambda y, x: A[y, x] + A[y, x+1] + A[y, x+2])
    s = hcl.create_schedule([A, B])
    RB = s.reuse_at(A, s[B], B.axis[1])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((10, 8), dtype="int")
    np_C = np.zeros((10, 8), dtype="int")

    for y in range(0, 10):
        for x in range(0, 8):
            np_C[y][x] = np_A[y][x] + np_A[y][x+1] + np_A[y][x+2]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_reuse_blur_y():
    hcl.init()
    A = hcl.placeholder((10, 10))
    B = hcl.compute((8, 10), lambda y, x: A[y, x] + A[y+1, x] + A[y+2, x])
    s = hcl.create_schedule([A, B])
    RB = s.reuse_at(A, s[B], B.axis[0])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 10), dtype="int")
    np_C = np.zeros((8, 10), dtype="int")

    for y in range(0, 8):
        for x in range(0, 10):
            np_C[y][x] = np_A[y][x] + np_A[y+1][x] + np_A[y+2][x]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_reuse_blur_x_y():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute((8, 8), lambda y, x: A[y, x] + A[y+1, x+1] + A[y+2, x+2], "B")
    s = hcl.create_schedule([A, B])
    RB_y = s.reuse_at(A, s[B], B.axis[0], "RB_y")
    RB_x = s.reuse_at(RB_y, s[B], B.axis[1], "RB_x")
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 8), dtype="int")
    np_C = np.zeros((8, 8), dtype="int")

    for y in range(0, 8):
        for x in range(0, 8):
            np_C[y][x] = np_A[y][x] + np_A[y+1][x+1] + np_A[y+2][x+2]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_conv2D_lb():
    hcl.init()
    A = hcl.placeholder((10, 10))
    r = hcl.reduce_axis(0, 3)
    c = hcl.reduce_axis(0, 3)
    B = hcl.compute((8, 8), lambda y, x: hcl.sum(A[y+r, x+c], axis=[r, c]))
    s = hcl.create_schedule([A, B])
    LB = s.reuse_at(A, s[B], B.axis[0])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 8), dtype="int")
    np_C = np.zeros((8, 8), dtype="int")

    for y in range(0, 8):
        for x in range(0, 8):
            for r in range(0, 3):
                for c in range(0, 3):
                    np_C[y][x] += np_A[y+r][x+c]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_conv2D_wb():
    hcl.init()
    A = hcl.placeholder((10, 10))
    r = hcl.reduce_axis(0, 3)
    c = hcl.reduce_axis(0, 3)
    B = hcl.compute((8, 8), lambda y, x: hcl.sum(A[y+r, x+c], axis=[r, c]))
    s = hcl.create_schedule([A, B])
    WB = s.reuse_at(A, s[B], B.axis[1])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 8), dtype="int")
    np_C = np.zeros((8, 8), dtype="int")

    for y in range(0, 8):
        for x in range(0, 8):
            for r in range(0, 3):
                for c in range(0, 3):
                    np_C[y][x] += np_A[y+r][x+c]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_conv2D_lb_wb():
    hcl.init()
    A = hcl.placeholder((10, 10))
    r = hcl.reduce_axis(0, 3)
    c = hcl.reduce_axis(0, 3)
    B = hcl.compute((8, 8), lambda y, x: hcl.sum(A[y+r, x+c], axis=[r, c]))
    s = hcl.create_schedule([A, B])
    LB = s.reuse_at(A, s[B], B.axis[0])
    WB = s.reuse_at(LB, s[B], B.axis[1])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 8), dtype="int")
    np_C = np.zeros((8, 8), dtype="int")

    for y in range(0, 8):
        for x in range(0, 8):
            for r in range(0, 3):
                for c in range(0, 3):
                    np_C[y][x] += np_A[y+r][x+c]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_partition_basic():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute(A.shape, lambda x, y: A[x, y], "B")
    s = hcl.create_schedule([A, B])
    s.partition(A)
    ir = str(hcl.lower(s))
    assert "partition variable=A" in ir

def test_partition_type():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute(A.shape, lambda x, y: A[x, y], "B")
    s1 = hcl.create_schedule([A, B])
    s1.partition(A)
    ir = str(hcl.lower(s1))
    assert "partition variable=A complete" in ir
    s1 = hcl.create_schedule([A, B])
    s1.partition(A, hcl.Partition.Block)
    ir = str(hcl.lower(s1))
    assert "partition variable=A block" in ir
    s1 = hcl.create_schedule([A, B])
    s1.partition(A, hcl.Partition.Cyclic)
    ir = str(hcl.lower(s1))
    assert "partition variable=A cyclic" in ir

def test_partition_dim_factor():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute(A.shape, lambda x, y: A[x, y], "B")
    s = hcl.create_schedule([A, B])
    s.partition(A, dim=1, factor=2)
    ir = str(hcl.lower(s))
    assert "partition variable=A complete factor=2 dim=1" in ir

def test_reshape():
    hcl.init()
    A = hcl.placeholder((10, 10), "A")
    B = hcl.compute(A.shape, lambda x, y: A[x, y], "B")
    C = hcl.compute(A.shape, lambda x, y: B[x, y], "C")
    s = hcl.create_schedule([A, C])
    s.reshape(B, (2, 5, 2, 5))
    ir = str(hcl.lower(s))
    assert "allocate B[int32 * 2 * 5 * 2 * 5]" in ir

def test_conv2D_lb_wb_schedule():
    hcl.init()
    A = hcl.placeholder((10, 10))
    r = hcl.reduce_axis(0, 3)
    c = hcl.reduce_axis(0, 3)
    B = hcl.compute((8, 8), lambda y, x: hcl.sum(A[y+r, x+c], axis=[r, c]))
    s = hcl.create_schedule([A, B])
    xo, xi = s[B].split(B.axis[1], 4)
    s[B].reorder(xo, B.axis[0], xi)
    LB = s.reuse_at(A, s[B], B.axis[0])
    WB = s.reuse_at(LB, s[B], xi)
    s.partition(LB, dim=2)
    s.partition(WB)
    s.reshape(B, (8, 2, 4))
    s[B].pipeline(B.axis[0])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10))
    np_B = np.zeros((8, 2, 4), dtype="int")
    np_C = np.zeros((8, 2, 4), dtype="int")

    for y in range(0, 8):
        for xo in range(0, 2):
            for xi in range(0, 4):
                for r in range(0, 3):
                    for c in range(0, 3):
                        np_C[y][xo][xi] += np_A[y+r][xi+xo*4+c]

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)

def test_reuse_select():
    hcl.init()
    A = hcl.placeholder((10, 10, 2))
    B = hcl.compute((10, 8, 2), lambda y, x, c: 
            hcl.select(c==0, A[y, x, c]*1 + A[y, x+1, c]*1 + A[y, x+2, c]*1,
                             A[y, x, c]*3 + A[y, x+1, c]*5 + A[y, x+2, c]*6))
    s = hcl.create_schedule([A, B])
    RB = s.reuse_at(A, s[B], B.axis[1])
    f = hcl.build(s)

    np_A = np.random.randint(0, 10, size=(10, 10, 2))
    np_B = np.zeros((10, 8, 2), dtype="int")
    np_C = np.zeros((10, 8, 2), dtype="int")

    for y in range(0, 10):
        for x in range(0, 8):
            np_C[y][x][0] = np_A[y][x][0]*1 + np_A[y][x+1][0]*1 + np_A[y][x+2][0]*1
            np_C[y][x][1] = np_A[y][x][1]*3 + np_A[y][x+1][1]*5 + np_A[y][x+2][1]*6

    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)
    print(hcl.lower(s))

    f(hcl_A, hcl_B)

    np_B = hcl_B.asnumpy()

    assert np.array_equal(np_B, np_C)


# def test_reuse_multiple_pattern():
#     hcl.init()
# 
#     A = hcl.placeholder((10, 10))
#     B = hcl.placeholder((10, 8))
#     C = hcl.placeholder((8, 10))
# 
#     def kernel(a, b, c):
# 
#         @hcl.def_([(10,10), (10,8), (8,10)])
#         def stencil(A, B, C):
#             hcl.update(B, lambda y, x: A[y, x] + 2*A[y, x+1] + 3*A[y, x+2])
#             hcl.update(C, lambda y, x: A[y, x] + 3*A[y+1, x] + 5*A[y+2, x])
# 
#         stencil(a, b, c)
# 
#     s = hcl.create_schedule([A, B, C], kernel)
# 
#     k = kernel.stencil
#     RB1 = s.reuse_at(k.A, s[k], k.axis[1])
#     RB2 = s.reuse_at(k.A, s[k], k.axis[0])
#     f = hcl.build(s)
# 
#     np_A = np.random.randint(0, 10, size=(10, 10))
#     np_B = np.zeros((10, 8), dtype="int")
#     np_C = np.zeros((8, 10), dtype="int")
# 
#     for y in range(0, 10):
#         for x in range(0, 8):
#             np_B[y][x] = np_A[y][x]*1 + np_A[y][x+1]*2 + np_A[y][x+2]*3
#             np_C[x][y] = np_A[x][y]*1 + np_A[x+1][y]*3 + np_A[x+2][y]*5
# 
#     hcl_A = hcl.asarray(np_A)
#     hcl_B = hcl.asarray(np.zeros((10, 8), dtype="int"))
#     hcl_C = hcl.asarray(np.zeros((8, 10), dtype="int"))
# 
#     f(hcl_A, hcl_B, hcl_C)
# 
#     ret_B = hcl_B.asnumpy()
#     ret_C = hcl_C.asnumpy()
#     assert np.array_equal(np_B, ret_B)
#     assert np.array_equal(np_C, ret_C)



