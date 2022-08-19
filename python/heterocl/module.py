import copy
from multiprocessing import Process
import warnings
import numpy as np

import ctypes
from hcl_mlir.dialects import func as func_d
from hcl_mlir.ir import *
from hcl_mlir.dialects import hcl as hcl_d
from hcl_mlir.runtime import *

from .context import get_context, get_location
from .devices import Platform
from .report import report_stats
from .runtime import execute_fpga_backend, execute_llvm_backend
from .utils import hcl_dtype_to_mlir


class HCLModule(object):

    def __init__(self, name, src, target, host_src=None, context=None, return_num=0):
        self.name = name
        self.src = src  # device src
        self.host_src = host_src
        self.target = copy.copy(target)
        self.context = context
        self.return_num = return_num

    def run_hls(self, shell=False):
        execute_fpga_backend(self.target, shell)
        report = self.report()
        report.display()

    def __call__(self, *argv):
        if "target" not in self.__dict__.keys():
            raise RuntimeError("No attached target!")
        if "name" not in self.__dict__.keys():
            raise RuntimeError("No module name specified!")
        target = self.target
        if isinstance(target, Platform) and target.tool.name in ["vivado_hls", "vitis_hls"]:
            self.run_hls(shell=True)
        elif target == "llvm":
            original_results = []
            with get_context() as ctx, get_location():
                for op in self.host_src.body.operations:
                    if isinstance(op, func_d.FuncOp) and op.sym_name.value == "top":
                        # test inputs
                        for i, arg in enumerate(op.arguments):
                            if not MemRefType.isinstance(arg.type):
                                continue
                            memref_type = MemRefType(arg.type)
                            assert memref_type.element_type == hcl_dtype_to_mlir(
                                argv[i].dtype, signless=True), "Input types: {} {}".format(memref_type.element_type, hcl_dtype_to_mlir(argv[i].dtype, signless=True))
                            if tuple(memref_type.shape) != argv[i].np_array.shape:
                                warnings.warn(
                                    "Shape mismatch between input {} and kernel argument {}!".format(tuple(memref_type.shape), argv[i].np_array.shape))
                                pad_shape = []
                                for dst, src in zip(memref_type.shape, argv[i].np_array.shape):
                                    pad_shape.append((0, dst - src))
                                argv[i].np_array = np.pad(
                                    argv[i].np_array, pad_shape)
                        # test outputs
                        for i, res_type in enumerate(op.type.results):
                            if not MemRefType.isinstance(res_type):
                                continue
                            memref_type = MemRefType(res_type)
                            assert memref_type.element_type == hcl_dtype_to_mlir(
                                argv[len(op.arguments)+i].dtype, signless=True), "Input types: {} {}".format(memref_type.element_type, hcl_dtype_to_mlir(argv[len(op.arguments)+i].dtype, signless=True))
                            if tuple(memref_type.shape) != argv[len(op.arguments)+i].np_array.shape:
                                warnings.warn(
                                    "Shape mismatch between output {} and kernel result {}!".format(tuple(memref_type.shape), argv[len(op.arguments)+i].np_array.shape))
                                pad_shape = []
                                for dst, src in zip(memref_type.shape, argv[len(op.arguments)+i].np_array.shape):
                                    pad_shape.append((0, dst - src))
                                original_results.append(
                                    [argv[len(op.arguments)+i], argv[len(op.arguments)+i].np_array.shape])
                                argv[len(op.arguments)+i].np_array = np.pad(
                                    argv[len(op.arguments)+i].np_array, pad_shape)
            execute_llvm_backend(self.src, self.name, self.return_num, *argv)
            for res, shape in original_results:
                slicing = []
                for s in shape:
                    slicing.append(slice(0, s))
                res.np_array = res.np_array[tuple(slicing)]
        else:
            raise RuntimeError("Not implemented")

    def report(self):
        """Get tool report
        """
        if "target" not in self.__dict__.keys():
            raise RuntimeError("No attached target!")
        if "name" not in self.__dict__.keys():
            raise RuntimeError("No module name specified!")
        target = self.target
        if target.tool.name == "vivado_hls":
            if "csyn" not in target.tool.mode and target.tool.mode != "debug":
                raise RuntimeError(
                    "Not supported mode {}. Use csyn mode to retrieve the report instead.".format(target.tool.mode))
        else:
            raise RuntimeError("Not implemented")
        return report_stats(target, target.project)


class HCLSuperModule(object):

    def __init__(self, modules, maps=dict(), deps=[]):
        self.modules = modules
        self.maps = maps
        self.mod_map = dict()
        self.mod_args = dict()
        self.task_deps = deps

    def __call__(self, mode="sim"):
        if mode == "hls":
            if len(self.modules) > 1:
                pool = []
                for module in self.modules:
                    pool.append(Process(target=module.run_hls, args=(False,)))
                    pool[-1].start()
                for p in pool:
                    p.join()
            else:
                self.modules[0].run_hls(True)
        
        else:
            hcl_d.tf_execute_tasks(self.mod_map, self.mod_args)
    
    def task(self, sub_mod, args):
        # ctypes_args = [ctypes.pointer(ctypes.pointer(
        #         get_ranked_memref_descriptor(arg))) for arg in args]
        # packed_args = (ctypes.c_void_p * len(ctypes_args))()
        # for argNum in range(len(ctypes_args)):
        #   packed_args[argNum] = ctypes.cast(ctypes_args[argNum], ctypes.c_void_p)
        
        self.mod_args[sub_mod.fname] = args
        # ctypes.void_p_Array
        self.mod_map[sub_mod.fname] = str(sub_mod.host_src)
    
    def __getattr__(self, key):
        sub_mod = self.maps[key]
        sub_mod.fname = key
        return sub_mod
