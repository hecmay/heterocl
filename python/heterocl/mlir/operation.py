import inspect
from collections import OrderedDict

import hcl_mlir
from hcl_mlir import (ASTBuilder, GlobalInsertionPoint, get_context,
                      get_location)

from hcl_mlir.dialects import (std, affine, builtin, arith, hcl as hcl_d)
from hcl_mlir.ir import *

from .. import config, types
from .schedule import Schedule, Stage
from .tensor import Tensor, PlaceHolder


def init(init_dtype=types.Int(32), raise_assert_exception=True):
    """Initialize a HeteroCL environment with configurations.
    """
    config.init_dtype = init_dtype
    config.raise_assert_exception = raise_assert_exception


def get_dtype_str(dtype=None):
    if not dtype is None and not isinstance(dtype, (types.Type, str)):
        raise RuntimeError("Type error")
    dtype = config.init_dtype if dtype is None else dtype
    if not isinstance(dtype, str):
        dtype = types.dtype_to_str(dtype)
    return dtype


def placeholder(shape, name=None, dtype=None):
    """Construct a HeteroCL placeholder for inputs/outputs.
    """
    if name is None:
        name = hcl_mlir.UniqueName.get("tensor")
    if not hcl_mlir.is_hcl_mlir_type(dtype):
        dtype = get_dtype_str(dtype)
    tensor = PlaceHolder(shape, dtype, name)
    return tensor


def asarray(np_array, dtype):
    return Tensor(np_array, dtype)


def scalar(init, name=None, dtype=None):
    """Syntactic sugar: single-value tensor 
    - init: int, float, or expr
    """
    if name is None:
        name = hcl_mlir.UniqueName.get("scalar")
    ret_tensor = placeholder((1,), name=name, dtype=dtype)
    ret_tensor.build()
    index = hcl_mlir.ConstantOp(hcl_mlir.idx_type, 0)
    if not hcl_mlir.is_hcl_mlir_type(dtype):
        dtype = get_dtype_str(dtype)
    if isinstance(init, int) or isinstance(init, float):
        init = hcl_mlir.ConstantOp(dtype, init)
    hcl_mlir.StoreOp(init, ret_tensor, [index])
    return ret_tensor


def reduce_axis(lower, upper, name=None):
    """Create a reduction axis for reduction operations.
    """
    return hcl_mlir.ReduceVar(None, bound=(lower, upper), name=name)


def cast(dtype, expr):
    return hcl_mlir.CastOp(expr, dtype)


def select(cond, true_val, false_val):
    return hcl_mlir.SelectOp(cond, true_val, false_val)


def any(*args):
    """Create a new experssion of the union of all conditions in the arguments
    """
    if not args:
        raise ValueError("Any must take at least 1 argument")
    if len(args) == 1:
        return args[0]
    ret = hcl_mlir.OrOp(args[0], args[1])
    for i in range(2, len(args)):
        ret = hcl_mlir.OrOp(ret, args[i])
    return ret


def all(*args):
    """Create a new experssion of the intersection of all conditions in the
      arguments
    """
    if not args:
        raise ValueError("Any must take at least 1 argument")
    if len(args) == 1:
        return args[0]
    ret = hcl_mlir.AndOp(args[0], args[1])
    for i in range(2, len(args)):
        ret = hcl_mlir.AndOp(ret, args[i])
    return ret


def sum(data, axis=None, dtype=None, name=""):
    return hcl_mlir.SumOp(data, axis, get_dtype_str(dtype))


def max(data, axis=None, dtype=None, name=""):
    return hcl_mlir.MaxOp(data, axis, get_dtype_str(dtype))


def min(data, axis=None, dtype=None, name=""):
    return hcl_mlir.MinOp(data, axis, get_dtype_str(dtype))


def compute_body(shape, fcompute, ret_tensor, name):
    """ Builds loop nests for declarative compute APIs.
    """
    out_ndim = len(shape)
    argspec = inspect.getfullargspec(fcompute)
    if len(argspec.args) == 0 and argspec.varargs is None:
        arg_names = ["i%d" % i for i in range(out_ndim)]
    elif argspec.varargs is not None:
        # if there is a varargs, it takes the remaining dimensions of out_ndim
        arg_names = argspec.args + [
            f"i{i}" for i in range(out_ndim - len(argspec.args))
        ]
    else:
        arg_names = argspec.args
        # if there are fewer args than out dimensions, the remaining dimensions
        # are implicitly broadcasted
        out_ndim = len(arg_names)
    assert argspec.varkw is None, "Variable keyword arguments not supported in fcompute"
    assert argspec.defaults is None, "Default arguments not supported in fcompute"
    assert (
        len(argspec.kwonlyargs) == 0
    ), "Keyword arguments are not supported in fcompute"
    # Get input tensors to fcompute
    closure_var = inspect.getclosurevars(fcompute).nonlocals
    inputs = []
    for _, var in closure_var.items():
        if isinstance(var, PlaceHolder):
            inputs.append(var.tensor)
    input_types = []
    for in_tensor in inputs:
        input_types.append(in_tensor.get_memref_type())

    # Disable build-in-place for declarative compute
    hcl_mlir.disable_build_inplace()
    # Start building loop-nest
    with get_context() as ctx, get_location() as loc, Stage(name) as stage:
        # create loop handles in the top function
        with GlobalInsertionPoint.get():
            loop_handles = []
            for loop_name in arg_names:
                loop_handles.append(
                    hcl_d.CreateLoopHandleOp(StringAttr.get(loop_name))
                )
        if hcl_mlir.EXTRACT_FUNCTION:
            if ret_tensor is not None:
                return_types = [ret_tensor.get_memref_type()]
            else:
                return_types = []
            # create stage function
            stage_func_name = "Stage_"+name
            # here we also put the return in the input argument,
            # since commonly in C++ we should pass the array by reference
            stage_func_op = builtin.FuncOp(name=stage_func_name, type=FunctionType.get(
                inputs=input_types+return_types, results=[]), ip=GlobalInsertionPoint.ip_stack[0])
            stage_func_op.attributes["inputs"] = StringAttr.get(
                ",".join([tensor.name for tensor in inputs]))
            if ret_tensor is not None:
                stage_func_op.attributes["outputs"] = StringAttr.get(
                    ret_tensor.name)
            stage_func_op.add_entry_block()
            # attach the function to the stage
            stage.set_ir_node(stage_func_op)
            # call this function in the top function
            call_arglist = [tensor.result for tensor in inputs]
            if ret_tensor is not None:
                call_arglist.append(ret_tensor.result)
            call_op = hcl_mlir.CallOp(None, stage_func_name, call_arglist)
            call_op.build()
            call_op.built_op.attributes["inputs"] = StringAttr.get(
                ",".join([tensor.name for tensor in inputs]))
            if ret_tensor is not None:
                call_op.built_op.attributes["outputs"] = StringAttr.get(
                    ret_tensor.name)
            # update inner load/store references
            # used for recovery
            original_tensor_op = [tensor.op for tensor in inputs]
            for tensor, arg in zip(inputs, stage_func_op.entry_block.arguments):
                tensor.op = arg
            # insertion point become the stage function inside
            GlobalInsertionPoint.save(
                InsertionPoint(stage_func_op.entry_block))

        func_ip = GlobalInsertionPoint.get()
        # Create for loops in the stage
        loops = []
        body_ip = func_ip
        for i, (ub, loop_name) in enumerate(zip(shape, arg_names)):
            loop = hcl_mlir.make_affine_for(
                0,
                ub,
                step=1,
                name=loop_name,
                stage=(name if i == 0 else ""),
                ip=body_ip,
            )
            if i != 0:  # manually add terminator!
                affine.AffineYieldOp([], ip=body_ip)
            loops.append(loop)
            body_ip = InsertionPoint(loop.body)

        # transform lambda function to MLIR
        GlobalInsertionPoint.save(body_ip)  # inner-most loop
        # get loop variables (BlockArgument)
        iter_var = [hcl_mlir.IterVar(loop.induction_variable)
                    for loop in loops]

        # calculate the lambda funtion,
        # at the same time build up MLIR nodes;
        # the Python builtin operators are overloaded in our custom class,
        # thus fcompute can be directly called and run
        if ret_tensor is not None:
            result_expr = fcompute(*iter_var)
            builder = ASTBuilder()
            true_result = builder.visit(result_expr)
            result_expr.built_op = true_result
            # store the result back to tensor
            # we have to read the ssa value out first, then store back to tensor
            if isinstance(result_expr, hcl_mlir.SumOp):
                zero_idx = arith.ConstantOp(
                    IndexType.get(), IntegerAttr.get(IndexType.get(), 0), ip=GlobalInsertionPoint.get())
                value = affine.AffineLoadOp(
                    result_expr.result,
                    [zero_idx.result],
                    loc=loc,
                    ip=GlobalInsertionPoint.get()
                )
                value.attributes["from"] = StringAttr.get("sum_rv")
            else:
                value = result_expr.built_op

            if hcl_mlir.EXTRACT_FUNCTION:
                write_back = list(stage_func_op.entry_block.arguments)[-1]
                # recover as top function op
                for i, tensor in enumerate(inputs):
                    tensor.op = original_tensor_op[i]
            else:
                write_back = ret_tensor.result
            ret_val = affine.AffineStoreOp(
                value.result,
                write_back,
                [loop.induction_variable for loop in loops],
                ip=GlobalInsertionPoint.get(),
            )
            ret_val.attributes["to"] = StringAttr.get(ret_tensor.name)
        else:
            fcompute(*iter_var)

        # remember to add affine.yield after each for loop
        affine.AffineYieldOp([], ip=GlobalInsertionPoint.get())

        # set loop handles
        if ret_tensor is not None:
            stage.set_output(ret_tensor)
            stage.op.set_axis(loop_handles)
        else:
            # TODO(Niansong):
            # attach axis for hcl.mutate
            pass

        # recover insertion point from inner-most loop body
        GlobalInsertionPoint.restore()

        if hcl_mlir.EXTRACT_FUNCTION:
            # recover from the subfunction
            ret_op = std.ReturnOp([], ip=GlobalInsertionPoint.get())
            GlobalInsertionPoint.restore()
        else:
            stage.set_ir_node(loops[0])

    if ret_tensor is not None:
        hcl_mlir.enable_build_inplace()
        Schedule._DataflowGraph.add_edges(inputs, ret_tensor)

    return ret_tensor


def compute(shape, fcompute, name=None, dtype=None, attrs=OrderedDict()):
    # check API correctness
    if not isinstance(shape, tuple):
        raise RuntimeError("The shape of compute API must be a tuple")
    shape = tuple([int(s) if isinstance(s, float) else s for s in shape])
    if name is None:
        name = hcl_mlir.UniqueName.get("tensor")
    # create return tensor
    ret_tensor = placeholder(shape, dtype=dtype, name=name)
    # build return tensor
    ret_tensor.build()
    return compute_body(shape, fcompute, ret_tensor, name)


def update(tensor, fcompute, name=None):
    """
    tensor: hcl_mlir.build_ir.TensorOp
    fcompute: function, callable
    name: str
    """
    # Check tensor type
    if not isinstance(tensor, hcl_mlir.build_ir.TensorOp):
        raise RuntimeError("Unexpected argument type of the " +
                           "first argument: {}, update API expects tensor as input.".format(type(tensor)))
    if name is None:
        name = tensor.name + "_updated"
    shape = tensor.shape
    compute_body(shape, fcompute, tensor, name)
    return


def mutate(domain, fcompute, name):
    """
    For now, assume no return value
    """
    # check API correctness
    if not isinstance(domain, tuple):
        raise RuntimeError("The domain of mutate API must be a tuple")
    if name is None:
        name = hcl_mlir.UniqueName.get("stage")
    compute_body(domain, fcompute, None, name)
    return
