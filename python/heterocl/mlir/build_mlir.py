import io
from collections import OrderedDict

import hcl_mlir
from hcl_mlir import (get_context, get_insertion_point, get_location,
                      set_insertion_point)
from ordered_set import OrderedSet

from mlir import passmanager
from mlir.dialects import builtin, memref, std
from mlir.execution_engine import *
from mlir.ir import *

from ..schedule import Schedule, Stage
from ..tvm.schedule import create_schedule as tvm_create_schedule
from .base import get_module, get_top_function


def placeholder(shape, name=None, dtype=None):
    """Construct a HeteroCL placeholder for inputs/outputs.
    """
    with get_context() as ctx, get_location() as loc:
        memref_type = MemRefType.get(shape, F32Type.get(ctx), loc=loc)
        tensor = hcl_mlir.TensorOp(shape, memref.AllocOp, memref_type)
        return tensor


def create_schedule(inputs, func, name=""):
    """Create a schedule for compute optimizations.
    """
    outputs = []
    if not isinstance(inputs, list):
        inputs = [inputs]
    # reset the global variables
    Schedule.stage_ops = []
    Schedule.mod_calls = dict()
    Schedule.stage_names = set()
    Schedule.last_stages = OrderedSet([])
    # create exact HCL IR nodes
    with get_context() as ctx, get_location() as loc, Stage("_top") as top:
        # create top-level function
        input_types = []
        for tensor in inputs:
            input_types.append(tensor.memref_type)
        func_op = builtin.FuncOp(name="top", type=FunctionType.get(
            inputs=input_types, results=[]), ip=InsertionPoint(get_module().body))
        func_op.add_entry_block()
        set_insertion_point(InsertionPoint(func_op.entry_block))
        # create exact memref alloc
        for tensor, arg in zip(inputs, func_op.entry_block.arguments):
            tensor.op = arg
        # execute all fcompute and generate inner IR nodes
        ret = func(*inputs)

        # append the output tensors to the input list
        if ret is not None:
            if isinstance(ret, tuple):
                outputs = list(ret)
            else:
                outputs.append(ret)
        else:
            raise RuntimeError("Function should have return value")

        # recompute the function type
        return_types = [v.memref_type for v in outputs]
        function_type = FunctionType.get(
            inputs=input_types, results=return_types)
        func_op.attributes["type"] = TypeAttr.get(function_type)

        # create block terminator
        outputs = [output.op.result for output in outputs]
        ret_op = std.ReturnOp(outputs, ip=get_insertion_point())

        # let the later schedule nodes insert before ret_op
        #   compute1
        #   compute2
        #   schedule1 # inserted _before_ the point
        #   ret_op    <- InsertionPoint
        set_insertion_point(InsertionPoint(ret_op))

    # let each stage be an attribute of the function
    for op in top.substages:
        func.__setattr__(op.name, op)
    t = Schedule.last_stages
    ops = [t_._op.op for t_ in t]
    s = Schedule(tvm_create_schedule(ops), inputs, outputs, name)
    return s


def build(schedule, target=None, name="default_function", stmt=None):
    """Build the executable according to the schedule and target.
    """
    new_inputs = []
    for input_tensor in schedule.inputs:  # should be hcl_mlir.TensorOp
        new_inputs.append(input_tensor)

    # apply the schedule and lower
    func = get_top_function()
    hcl_mlir.loop_transformation(func.operation)
    get_module().dump()

    if target == "vhls":
        return build_fpga_kernel(schedule, new_inputs, target, name, stmt)
    else:
        return build_llvm(schedule, new_inputs, target, name, stmt)


def build_fpga_kernel(schedule, inputs, target=None, name="default_function", stmt=None):
    # generate code
    buf = io.StringIO()
    hcl_mlir.emit_hlscpp(get_module(), buf)
    buf.seek(0)
    return buf.read()


def lowerToLLVM(module):
    import mlir.conversions
    pm = passmanager.PassManager.parse(
        "reconcile-unrealized-casts")
    pm.run(module)
    return module


def build_llvm(schedule, inputs, target=None, name="default_function", stmt=None):
    with get_context() as ctx, get_location():
        # mod = get_module()
        print("\n\nBefore Lowering: ")
        get_module().dump()
        hcl_mlir.lower_hcl_to_llvm(get_module(), ctx)
        lowerToLLVM(get_module())
        print("lowered.")
        print("\n\nAfter Lowering: ")
        get_module().dump()
        execution_engine = ExecutionEngine(get_module())
        execution_engine.invoke(name)
        print("Execution success")
