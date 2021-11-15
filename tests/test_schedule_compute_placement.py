import heterocl as hcl
import numpy as np
from itertools import permutations
import os

# Test DFG partitioning
def test_graph_partition_01():
    hcl.init()
    A = hcl.placeholder((10, 32), "A")
    def kernel(A):
        B = hcl.compute(A.shape, lambda i, j: A[i, j] * 2, "B")
        hcl.update(B, lambda i, j: B[i, j] + 1, "update1")
        hcl.update(B, lambda i, j: B[i, j] * 2, "update2")
        return B

    target = hcl.Platform.aws_f1
    s = hcl.create_schedule([A], kernel)
    # compute stage B and update 1 on FPGA
    s.to(A, target.xcel)
    s.to(kernel.update1.B, target.host)

    code = str(hcl.lower(s)); print(code)
    assert "test(int32(B[10*32]), int32(A[10*32]))" in code, code


def test_graph_partition_02():
    hcl.init()
    A = hcl.placeholder((10, 32), "A")
    def kernel(A):
        B = hcl.compute(A.shape, lambda i, j: A[i, j] * 2, "B")
        hcl.update(B, lambda i, j: B[i, j] + 1, "update1")
        hcl.update(B, lambda i, j: B[i, j] * 2, "update2")
        return B

    target = hcl.Platform.aws_f1
    s = hcl.create_schedule([A], kernel)
    # compute stage B on FPGA, update1 on host and update2 on FPGA
    s.to(A, target.xcel)
    s.to(kernel.B, target.host)
    s.to(kernel.update1.B, target.xcel)

    code = str(hcl.lower(s)); print(code)
    assert "test(int32(B[10*32]), int32(A[10*32]))" in code, code


def test_multiple_subgraph():
    hcl.init()
    A = hcl.placeholder((10, 32), "A")
    B = hcl.placeholder((10, 32), "B")
    def kernel(A, B):
        C = hcl.compute(A.shape, lambda i, j: A[i,j] + 1, "C")
        D = hcl.compute(C.shape, lambda i, j: B[i,j] + 1, "D")
        return hcl.compute(C.shape, lambda i, j: C[i,j] + D[i,j], "E")

    target = hcl.Platform.aws_f1
    s = hcl.create_schedule([A, B], kernel)
    s.to([A, B], target.xcel)
    s.to([kernel.E], target.host)
    code = str(hcl.lower(s))
    assert "io attr: \"B\"" in code
    assert "io attr: \"A\"" in code
    assert "io attr: \"E\"" in code

def test_extern_ops():
    hcl.init()
    A = hcl.placeholder((10, 32), "A")
    def kernel(A):
        B = hcl.compute(A.shape, lambda *args : A[args] + 1, "B")
        C = hcl.compute(A.shape, lambda *args : B[args] + 1, "C")
        D = hcl.compute(A.shape, lambda *args : C[args] * 2, "D")
        return D
    
    target = hcl.Platform.aws_f1
    s = hcl.create_schedule([A], kernel)
    s.to(kernel.B, target.xcel)
    s.to(kernel.C, target.host)
    code = str(hcl.lower(s))
    print(code)
    assert "test(B, C)" in code

if __name__ == '__main__':
    test_graph_partition_02()