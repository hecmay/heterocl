import heterocl as hcl
import numpy as np

def test_basic(sdsoc):
    if not sdsoc: return
    hcl.init()
    tool = hcl.tool.sdsoc
    target = hcl.platform.zc706(tool)

    A = hcl.placeholder((10,))
    def kernel(A):
        return hcl.compute(A.shape, lambda x: A[x] + 1)
    s = hcl.create_schedule(A, kernel)
    f = hcl.build(s, target)

    np_A = np.random.randint(0, 10, A.shape)
    np_B = np.zeros(A.shape)
    hcl_A = hcl.asarray(np_A)
    hcl_B = hcl.asarray(np_B)
    f(hcl_A, hcl_B)
    np_B = np_A + 1
    np.testing.assert_array_equal(np_B, hcl_B.asnumpy())

test_basic(True)
