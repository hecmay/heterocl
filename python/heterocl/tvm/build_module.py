"""The build utils in python.

This module provides the functions to transform schedule to
LoweredFunc and compiled Module.
"""
from __future__ import absolute_import as _abs
import os, subprocess, time, re
import warnings
import types

from ._ffi.node import NodeBase, register_node
from ._ffi.function import register_func
from ._ffi.base import _RUNTIME_ONLY
from . import api
from . import tensor
from . import schedule
from . import expr
from . import ir_pass
from . import stmt as _stmt
from . import container
from . import module
from . import codegen
from . import ndarray
from . import target as _target
from . import make
from ..devices import platform

def replace_text(f_name, prev, new):
    with open(f_name, 'r') as fp:
        data = fp.read()
    data = data.replace(prev, new)
    with open(f_name, 'w') as fp:
        fp.write(data)

def run_process(cmd, pattern=None, env=None):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if err: print("error raised: ", err.decode())
    if pattern: return re.findall(pattern, out.decode("utf-8"))
    return out.decode("utf-8")

@register_func
def tvm_callback_exec_evaluate(platform, mode):
    # perform simulation and extract qor
    qor = dict()

    if platform == "vivado":
      out = run_process("cd __tmp__; make vivado 2>&1")
      print(out)

    elif platform == "vivado_hls": 
      assert os.system("which vivado_hls >> /dev/null") == 0, \
        "cannot find vivado hls on system path"
      ver = run_process("g++ --version", "\d\.\d\.\d")[0].split(".")
      assert int(ver[0]) * 10 + int(ver[1]) >= 48, \
        "g++ version too old {}.{}.{}".format(ver[0], ver[1], ver[2])
      out = run_process("cd __tmp__; make csim 2>&1")
      runtime = [k for k in out.split("\n") if "seconds" in k][0]
      print("[{}] Simulation runtime {}".format(
          time.strftime("%H:%M:%S", time.gmtime()), runtime))

    elif platform == "sdsoc":
      assert os.system("which sds++ >> /dev/null") == 0, \
        "cannot find sds++ on system path"
      out = run_process("cd __tmp__; make sdsoc")
      print(out)

    elif platform == "sdaccel":
      assert os.system("which xocc >> /dev/null") == 0, \
        "cannot find xocc on system path"

      if mode == "sw_emu":
        cmd = "cd __tmp__; export XCL_EMULATION_MODE=sw_emu; ./top_function_0_host.exe -f top_function_0.sw_emu.xclbin"
        out = run_process(cmd)

      elif mode == "hw_emu":
        cmd = "cd __tmp__; export XCL_EMULATION_MODE=hw_emu; ./top_function_0_host.exe -f top_function_0.hw_emu.xclbin"
        out = run_process(cmd)
        os.system("cat __tmp__/profile_summary.csv")

      elif mode == "hw":
        cmd = "cd __tmp__; export XCL_EMULATION_MODE=hw; ./top_function_0_host.exe -f top_function_0.hw.xclbin"
        out = run_process(cmd)

    else: # unsupported 
      assert False, "unsupported " + platform

    return str(qor) 

@register_func
def copy_and_compile(platform, mode, backend):
    """  create necessary files and compile into binary """
    path = api.__file__
    path = os.path.join(path[0:path.find("python")], "tvm/src/template/")

    if platform == "rocket":
        ppac = "/work/zhang-x1/users/sx233/heterocl/hlib/rocc-ppac" 
        emulator = os.path.join(ppac, "rocket/emulator/emulator-freechips." + \
                                      "rocketchip.system-RoccExampleConfig-debug")
        # build emulator if not exist
        if not os.path.isfile(emulator):
            cmd = "cd " + ppac + ";"
            cmd += "cp src/Ppac.v rocket/src/main/resources/vsrc;" + \
                   "cp src/PpacRoCC.scala rocket/src/main/scala/tile;" + \
                   "cd rocket && git apply ../src/rocc-ppac.patch;" + \
                   "cd emulator && make CONFIG=RoccExampleConfig debug"
            # create subprocess to check
            subprocess.Popen(cmd, shell=True, stdout=open("build.log", "w")).wait()
             
        # re-build proxy kernel 
        if not os.path.isfile(ppac + "/rocket/riscv-pk/build/pk"):
            cmd = "cd " + ppac + "/rocket/riscv-pk;"
            cmd += "git apply ../../tests/patches/riscv-pk.patch;"
            cmd += "mkdir build; cd build;"
            cmd += " ../configure --prefix=$RISCV/riscv64-unknown-elf --host=riscv64-unknown-elf;"
            cmd += "make -j8; make install"
            subprocess.Popen(cmd, shell=True, stdout=open("build.log", "w")).wait()
        # return util folder needed to compile generated test files
        return "/work/zhang-x1/users/sx233/heterocl/rocc-ppac/tests" 

    # copy tcl and testbench  
    elif platform == "vivado_hls" or platform == "vivado":
        os.system("cp " + path + "vivado/* __tmp__/")
        os.system("cp " + path + "harness.mk __tmp__/")
        return "success"

    # copy sdsoc makefile
    elif platform == "sdsoc":
        os.system("cp " + path + "sdsoc/* __tmp__/")
        os.system("cp " + path + "harness.mk __tmp__/")
        return "success"

    if platform == "sdaccel":
        os.system("cp " + path + "sdaccel/* __tmp__/")
        os.system("cp " + path + "harness.mk __tmp__/")
        replace_text("__tmp__/Makefile", "App", "top_function_0")
        replace_text("__tmp__/utils.h", 
                     "xilinx_aws-vu9p-f1-04261818_dynamic_5_0", 
                     "xilinx_vcu1525_dynamic_5_1")
        if backend == "vhls":
          replace_text("__tmp__/Makefile", "kernel.cl", "kernel.cpp")

        # compile the program 
        assert os.system("which xocc >> /dev/null") == 0, \
            "cannot find xocc on system path"

        # compilation mode sw_emu, hw_emu, hw
        if mode == "sw_emu":
            env = os.environ.copy()
            assert "AWS_PLATFORM" in os.environ, \
                   "aws platform info missing" 

            # re-compile host only (reuse context ?) 
            if False and os.path.isfile("top_function_0.sw_emu.xclbin"):
              run_process("cd __tmp__; make clean; make host")
              run_process("cp top_function_0.sw_emu.xclbin __tmp__/")

            else: # config & compile
              env["XCL_EMULATION_MODE"] = "sw_emu"
              cmd = "cd __tmp__; make clean;"
              cmd += "emconfigutil --platform=$AWS_PLATFORM;"
              cmd += "make ocl OCL_TARGET=sw_emu \
                      OCL_PLATFORM=$AWS_PLATFORM \
                      APPLICATION_DIR=" + os.getcwd() + "/__tmp__/"
              out = run_process(cmd, env=env)

        # enable profiler 
        elif mode == "hw_emu":
            env = os.environ.copy()
            assert "AWS_PLATFORM" in os.environ, \
                   "aws platform info missing" 

            env["XCL_EMULATION_MODE"] = "hw_emu"
            cmd = "cd __tmp__; make clean;"
            cmd += "emconfigutil --platform=$AWS_PLATFORM;"
            cmd += "make ocl OCL_TARGET=hw_emu \
                    OCL_PLATFORM=$AWS_PLATFORM \
                    APPLICATION_DIR=" + os.getcwd() + "/__tmp__/"
            out = run_process(cmd, env=env)

        elif mode == "hw":
            env = os.environ.copy()
            assert "AWS_PLATFORM" in os.environ, \
                   "aws platform info missing" 

            env["XCL_EMULATION_MODE"] = "hw"
            cmd = "cd __tmp__; make clean;"
            cmd += "emconfigutil --platform=$AWS_PLATFORM;"
            cmd += "make ocl OCL_TARGET=hw \
                    OCL_PLATFORM=$AWS_PLATFORM \
                    APPLICATION_DIR=" + os.getcwd() + "/__tmp__/"
            out = run_process(cmd, env=env)
          
        return "success"

    else: # unrecognized platform
        assert False, "unsupported platform " + platform


class DumpIR(object):
    """
    Dump IR for each pass.
    With it, you can dump ir just like gcc/llvm.

    How to use:
    -----------
    .. code-block:: python

        with tvm.build_config(dump_pass_ir=True)
            run()
    """
    scope_level = 0
    def __init__(self):
        self._pass_id = 0
        self._recover_list = []

    def decorate(self, func):
        """ decorate the pass function"""
        def dump(*args, **kwargs):
            """dump function"""
            retv = func(*args, **kwargs)
            if not isinstance(retv, (_stmt.Stmt, container.LoweredFunc, container.Array)):
                return retv
            pname = str(self._pass_id) + "_" + func.func_name + "_ir.cc"
            with open(pname, "a") as f:
                out = retv.body if isinstance(retv, container.LoweredFunc) else retv
                f.write(str(out))
                if isinstance(retv, container.Array):
                    for x in retv:
                        out = x.body if isinstance(x, container.LoweredFunc) else x
                        f.write("---------%s\n%s\n-----------\n"%(x.name, str(out)))
                self._pass_id += 1
            return retv
        return dump

    def decorate_irpass(self):
        """decorate ir_pass and ScheduleOps"""
        self._old_sgpass = schedule.ScheduleOps
        schedule.ScheduleOps = self.decorate(schedule.ScheduleOps)
        vset = vars(ir_pass)
        k = v = 0
        def recover():
            vset[k] = v
        for k, v in vset.items():
            self._recover_list.append(recover)
            vset[k] = self.decorate(v) if isinstance(v, types.FunctionType) else v

    def decorate_custompass(self):
        """ decorate add_lower_pass pass in BuildConfig"""
        cfg = BuildConfig.current
        self._old_custom_pass = cfg.add_lower_pass
        custom_pass = cfg.add_lower_pass if cfg.add_lower_pass else []
        pass_list = [(x[0], self.decorate(x[1])) for x in custom_pass]
        BuildConfig.current.add_lower_pass = pass_list

    def enter(self):
        """only decorate outermost nest"""
        if DumpIR.scope_level > 0:
            return
        self.decorate_irpass()
        self.decorate_custompass()
        self._pass_id = 0
        DumpIR.scope_level += 1

    def exit(self):
        """recover outermost nest"""
        if DumpIR.scope_level > 1:
            return
        # recover decorated functions
        for f in self._recover_list:
            f()
        schedule.ScheduleOps = self._old_sgpass
        BuildConfig.current.add_lower_pass = self._old_custom_pass
        DumpIR.scope_level -= 1

@register_node
class BuildConfig(NodeBase):
    """Configuration scope to set a build config option.

    Note
    ----
    This object is backed by node system in C++, with arguments that can be
    exchanged between python and C++.

    Do not construct directly, use build_config instead.

    The fields that are backed by the C++ node are immutable once an instance
    is constructed. See _node_defaults for the fields.
    """

    current = None
    _node_defaults = {
        "auto_unroll_max_step": 0,
        "auto_unroll_max_depth": 8,
        "auto_unroll_max_extent": 0,
        "unroll_explicit": True,
        "detect_global_barrier": False,
        "partition_const_loop": False,
        "offset_factor": 0,
        "data_alignment": -1,
        "restricted_func": True,
        "double_buffer_split_loop": 1,
        "generate_reuse_buffer": True
    }

    # pylint: disable=no-member
    def __init__(self, handle):
        """Initialize the function with handle

        Parameters
        ----------
        handle : SymbolHandle
            the handle to the underlying C++ Symbol
        """
        super(BuildConfig, self).__init__(handle)
        self.handle = handle
        self._old_scope = None
        self._dump_ir = DumpIR()
        self.dump_pass_ir = False
        self.add_lower_pass = None

    def __enter__(self):
        # pylint: disable=protected-access
        self._old_scope = BuildConfig.current
        BuildConfig.current = self
        if self.dump_pass_ir is True:
            self._dump_ir.enter()
        return self

    def __exit__(self, ptype, value, trace):
        assert self._old_scope
        if self.dump_pass_ir is True:
            self._dump_ir.exit()
        BuildConfig.current = self._old_scope

    def __setattr__(self, name, value):
        if name in BuildConfig._node_defaults:
            raise AttributeError(
                "'%s' object cannot set attribute '%s'" % (str(type(self)), name))
        return super(BuildConfig, self).__setattr__(name, value)

def build_config(**kwargs):
    """Configure the build behavior by setting config variables.

    Parameters
    ----------
    auto_unroll_max_step: int, default=0
        Threshold of number of steps in the loop to be automatically unrolled.
        This takes inner loop count into consideration.

    auto_unroll_max_depth: int, default=4
        The maximum nested level of loops that can be automatically unrolled.

    unroll_explicit: bool, default=True
        Whether explicitly unroll the loop, if set false, the unroll hint will
        be passed to the CodeGen phase, which may generate pragma unroll hint.
        Set this to be true if CodeGen support unroll pragma and
        when we want to be more readable.

    detect_global_barrier: bool, default=True
        Whether detect global barrier.

    partition_const_loop: bool, default=False
        Whether partition const loop

    data_alignment: int, optional
        The alignment of data pointer in bytes.
        If -1 is passed, the alignment will be set to TVM's internal default.

    offset_factor: int, default=0
        The factor used in default buffer declaration.
        If specified as 0, offset field is not used.

    restricted_func: bool, default=True
        Whether build restricted function.
        That is each buffer argument to the function are guaranteed
        not to overlap. This enables more optimization.
        Corresponds to restricted keyword in C99

    double_buffer_split_loop: int, default=2
        Whether split the loop with factor. If it is zero, no splitting will happen.
        It it is bigger than one, the logic will do a split with factor equals the integer
        and unroll the inner loop. This allows the buffer fetching won't contain condition.

    add_lower_pass: list of tuiple (phase, function(Stmt->Stmt)), default=None
        phase contains an integer on which optimization pass we apply the pass.
        Additional lowering passes to be applied before make_api.

    dump_pass_ir: dump ir of each pass into file idx_passname_ir.cc, default=False

    generate_reuse_buffer: bool, default=True
        Lower the Reuse node to reuse buffers

    Returns
    -------
    config: BuildConfig
        The build configuration
    """
    node_args = {k: v if k not in kwargs else kwargs[k]
                 for k, v in BuildConfig._node_defaults.items()}
    config = make.node("BuildConfig", **node_args)

    for k in kwargs:
        if not k in node_args:
            setattr(config, k, kwargs[k])
    return config

if not _RUNTIME_ONLY:
    # BuildConfig is not available in tvm_runtime
    BuildConfig.current = build_config()

def get_binds(args, binds=None):
    """Internal function to get binds and arg_list given arguments.

    Parameters
    ----------
    args : list of Buffer or Tensor or Var
        The argument lists to the function.

    binds : dict of :any:`Tensor` to :any:`Buffer`, optional
        Dictionary that maps the Tensor to Buffer which specified the data layout
        requirement of the function. By default, a new compact buffer is created
        for each tensor in the argument.

    Returns
    -------
    binds: dict
        The bind specification

    arg_list: list
        The list of symbolic buffers of arguments.
    """
    binds = {} if binds is None else binds.copy()
    cfg = BuildConfig.current
    arg_list = []
    for x in args:
        if isinstance(x, tensor._Tensor):
            if x not in binds:
                buf = api.decl_buffer(x.shape,
                                      dtype=x.dtype,
                                      name=x.name,
                                      data_alignment=cfg.data_alignment,
                                      offset_factor=cfg.offset_factor)
                binds[x] = buf
                arg_list.append(buf)
            else:
                arg_list.append(binds[x])
        elif isinstance(x, schedule.Buffer):
            arg_list.append(x)
        elif isinstance(x, expr.Var):
            arg_list.append(x)
        else:
            raise ValueError("args must be Tensor, Buffer or Var")
    return binds, arg_list

def lower(sch,
          args,
          name="default_function",
          binds=None,
          simple_mode=False,
          kernel_only=False,
          stmt=None):
    """Lowering step before build into target.

    Parameters
    ----------
    sch : tvm._Schedule
        The schedule to be builded

    args : list of Buffer or Tensor or Var
        The argument lists to the function.

    name : str, optional
        The name of result function.

    binds : dict of :any:`Tensor` to :any:`Buffer`, optional
        Dictionary that maps the Tensor to Buffer which specified the data layout
        requirement of the function. By default, a new compact buffer is created
        for each tensor in the argument.

    simple_mode : bool, optional
        Whether only output simple and compact statement, this will skip
        LoopPartition, api wrapper generation and Unrolling.

    kernel_only: bool, optional
        This will skip inserting all checkers and only keep the kernel part
        when making LoweredFunc.

    Returns
    -------
    f : LoweredFunc or Stmt
       The result function, if with_api_wrapper=False
       Then the Stmt before make api is returned.
    """
    binds, arg_list = get_binds(args, binds)
    cfg = BuildConfig.current
    if stmt is not None:
        stmt = ir_pass.StorageFlatten(stmt, binds, 64)
        if kernel_only:
            return ir_pass.MakeKernelAPI(stmt, name, arg_list)
        else:
            return ir_pass.MakeAPI(stmt, name, arg_list, 0, cfg.restricted_func)
    add_lower_pass = cfg.add_lower_pass if cfg.add_lower_pass else []
    lower_phase0 = [x[1] for x in add_lower_pass if x[0] == 0]
    lower_phase1 = [x[1] for x in add_lower_pass if x[0] == 1]
    lower_phase2 = [x[1] for x in add_lower_pass if x[0] == 2]
    lower_phase3 = [x[1] for x in add_lower_pass if x[0] > 2]
    # normalize schedule first
    sch = sch.normalize()
    # Phase 0
    # sch = schedule.ScopePartition(sch)
    bounds = schedule.InferBound(sch)
    stmt = schedule.ScheduleOps(sch, bounds)
    stmt = ir_pass.InjectPrefetch(stmt)
    for f in lower_phase0:
        stmt = f(stmt)
    # Phase 1
    stmt = ir_pass.StorageFlatten(stmt, binds, 64)
    #stmt = ir_pass.CanonicalSimplify(stmt) #TODO: SOLVE THIS!!
    stmt = ir_pass.LiftAllocateAttrs(stmt)
    if cfg.generate_reuse_buffer:
        stmt = ir_pass.GenerateReuseBuffer(stmt, arg_list)
    for f in lower_phase1:
        stmt = f(stmt)
    # Phase 2
    if not simple_mode:
        stmt = ir_pass.LoopPartition(stmt, cfg.partition_const_loop)
    #stmt = ir_pass.VectorizeLoop(stmt) #TODO: FIX THIS!!
    #stmt = ir_pass.InjectVirtualThread(stmt) #TODO: FIX THIS!!
    stmt = ir_pass.InjectDoubleBuffer(stmt, cfg.double_buffer_split_loop)
    #stmt = ir_pass.StorageRewrite(stmt) #TODO: SOLVE THIS!!
    """ TODO: also fix this
    stmt = ir_pass.UnrollLoop(
        stmt,
        cfg.auto_unroll_max_step,
        cfg.auto_unroll_max_depth,
        cfg.auto_unroll_max_extent,
        cfg.unroll_explicit)
    """
    for f in lower_phase2:
        stmt = f(stmt)
    # Phase 2
    stmt = ir_pass.Simplify(stmt) #TODO: SOLVE SHIFTING
    stmt = ir_pass.LowerStorageAccessInfo(stmt)
    stmt = ir_pass.RemoveNoOp(stmt)
    stmt = ir_pass.RewriteUnsafeSelect(stmt)
    stmt = ir_pass.InferStream(stmt, arg_list, 32)
    for f in lower_phase3:
        stmt = f(stmt)
    if simple_mode:
        return stmt

    if kernel_only:
        return ir_pass.MakeKernelAPI(stmt, name, arg_list)
    else:
        return ir_pass.MakeAPI(stmt, name, arg_list, 0, cfg.restricted_func)

def build_fpga_kernel(sch, args, target, name="default_function"):
    """Build an FPGA kernel.

    Parameters
    ----------
    sch : tvm._Schedule, or LoweredFunc
        The schedule to be builded

    args : list of Buffer or Tensor or Var, optional
        The argument lists to the function.

    target_name : str
        The target string to indicate the language to be used.

    Returns
    -------
    module : Module
        The generated kernel module.

    Note
    ----
    This function should only be called by `build`.
    """
    if not isinstance(sch, schedule._Schedule):
        raise ValueError("sch for generating FPGA kernel must be Schedule")

    if args is None:
        raise ValueError("args must be given for build from schedule")

    # generate host (device) code / function 
    if target == "merlinc":
        BuildConfig.current = build_config(generate_reuse_buffer=False)
    else:
        BuildConfig.current = build_config()

    flist = lower(sch, args, kernel_only=True, name=name)
    if isinstance(flist, container.LoweredFunc):
        flist = [flist]
    fdevice = [ir_pass.LowerIntrin(x, str(target)) for x in flist]

    if isinstance(target, str): # string type (legacy support)
        builder = getattr(codegen, "build_{0}".format(target))
        ret = builder(fdevice)
        if isinstance(ret, str):
            decl = ret[:ret.find("{device}")]
            start = ret.find("{host}")
            end = ret.rfind("{host}")
            ret = decl + "\n" + ret[start+6:end]
            ret = ret.strip("\n").lstrip("\n") + "\n\n" 
        return ret

    try: # generate and split code
        host, xcel = None, None
        if target.tool.name == "sdaccel":
            host = target.host.lang.replace("opencl", "sdaccel")
            xcel = target.xcel.lang.replace("hlsc", "sdaccel")
        if target.tool.name == "aocl":
            host = target.host.lang = "aocl"
            xcel = target.xcel.lang = "aocl"
        elif target.tool.name in ("vivado_hls", "vivado", "sdsoc"):
            host = target.host.lang.replace("hlsc", "vhls")
            xcel = target.xcel.lang.replace("hlsc", "vhls")
        elif target.tool.name == "rocket":
            host = target.host.lang.replace("c", "rv64_ppac")
   
        # return simulation built function
        mode = str(target.tool.mode)
        assert mode in ["debug", "sw_emu", "hw_emu", "hw"], \
               "not support mode " + mode
        if mode == "debug": # return source code only
            host_code, xcel_code = "", ""
            if host: # src mode generate host code 
                builder = getattr(codegen, "build_{0}".format(host))
                host_code = builder(fdevice)
                findex, rindex = host_code.find("{host}"), host_code.rfind("{host}")
                host_code = host_code[findex + 6 : rindex]
            if xcel: # src mode generate xcel code
                builder = getattr(codegen, "build_{0}".format(xcel))
                xcel_code = builder(fdevice)
                findex, rindex = xcel_code.find("{device}"), xcel_code.rfind("{device}")
                xcel_code = xcel_code[findex + 8 : rindex]
            return xcel_code + host_code 
        else: # impl mode or sim mode
            builder = getattr(codegen, "build_{0}".format("sim"))
            keys = [k for k in target.tool.options.keys()]
            vals = [v for v in target.tool.options.values()]
            # platform & backend lang
            keys.insert(0, "name")
            vals.insert(0, target.tool.name)
            keys.insert(1, "mode")
            vals.insert(1, mode)
            keys.insert(2, "backend")
            vals.insert(2, xcel)
            return builder(fdevice, keys, vals)

    except AttributeError:
        raise AttributeError("Cannot find the target builder %s" % target)
    return None

def build(sch,
          args=None,
          target=None,
          target_host=None,
          name="default_function",
          binds=None,
          stmt=None):
    """Build a function with arguments as signiture.

    Parameters
    ----------
    sch : tvm._Schedule, or LoweredFunc
        The schedule to be builded

    args : list of Buffer or Tensor or Var, optional
        The argument lists to the function.

    target : str or :any:`tvm.target.Target`, optional
        The target and option of the compilation.

    target_host : str or :any:`tvm.target.Target` optional
        Host compilation target, if target is device.
        When TVM compiles device specific program such as CUDA,
        we also need host(CPU) side code to interact with the driver
        setup the dimensions and parameters correctly.
        target_host is used to specify the host side codegen target.
        By default, llvm is used if it is enabled,
        otherwise a stackvm intepreter is used.

    name : str, optional
        The name of result function.

    binds : dict, optional
        Dictionary that maps the binding of symbolic buffer to Tensor.
        By default, a new buffer is created for each tensor in the argument.

    Returns
    -------
    f : Function, or pair of functions
       The result function.

    Note
    ----
    See the note on :any:`tvm.target` on target string format.
    """
    if isinstance(target, platform):
        return build_fpga_kernel(sch, args, target, name=name)
    else: # default string type target
        target = _target.current_target() if target is None else target
        target = _target.create(target) if target else _target.create("llvm")
        if "fpga" in target.keys:
            return build_fpga_kernel(sch, args, target.target_name, name=name)
    BuildConfig.current = build_config()

    if isinstance(sch, schedule._Schedule):
        if args is None:
            raise ValueError("args must be given for build from schedule")
        flist = lower(sch, args,
                      name=name,
                      binds=binds,
                      stmt=stmt)
        if isinstance(flist, container.LoweredFunc):
            flist = [flist]
    elif isinstance(sch, container.LoweredFunc):
        if args:
            raise ValueError("args must be done when build from LoweredFunc")
        flist = [sch]
    elif isinstance(sch, (list, tuple, container.Array)):
        flist = sch
    else:
        raise ValueError("sch have to be Schedule, LoweredFunc or list of LoweredFunc")
    fname_set = set()
    for x in flist:
        if not isinstance(x, container.LoweredFunc):
            raise ValueError("sch have to be Schedule, LoweredFunc or list of LoweredFunc")
        if x.name in fname_set:
            raise ValueError("Duplicate function name %s" % x.name)
        fname_set.add(x.name)

    fhost = []
    fdevice = []
    for func in flist:
        if func.func_type == container.LoweredFunc.MixedFunc:
            if BuildConfig.current.detect_global_barrier:
                func = ir_pass.ThreadSync(func, "global")
            func = ir_pass.ThreadSync(func, "shared")
            warp_size = target.thread_warp_size
            func = ir_pass.LowerThreadAllreduce(func, warp_size)
            fsplits = [s for s in ir_pass.SplitHostDevice(func)]
            fhost.append(fsplits[0])
            for x in fsplits[1:]:
                fdevice.append(x)
        elif func.func_type == container.LoweredFunc.HostFunc:
            fhost.append(func)
        elif func.func_type == container.LoweredFunc.DeviceFunc:
            fdevice.append(func)
        else:
            raise ValueError("unknown function type %d" % func.func_type)

    if "gpu" in target.keys and not fdevice:
        warnings.warn(
            "Specified target %s, but cannot find device code, did you do bind?" % target)

    device_type = ndarray.context(target.target_name, 0).device_type
    fhost = [ir_pass.BindDeviceType(x, device_type) for x in fhost]
    fhost = [ir_pass.LowerTVMBuiltin(x) for x in fhost]

    if not target_host:
        if device_type == ndarray.cpu(0).device_type:
            target_host = target
            assert not fdevice
        else:
            target_host = "llvm" if module.enabled("llvm") else "stackvm"
    target_host = _target.create(target_host)
    target_device = target
    fdevice = [ir_pass.LowerIntrin(x, target_device.target_name) for x in fdevice]
    fhost = [ir_pass.LowerIntrin(x, target_host.target_name) for x in fhost]
    fhost = [ir_pass.CombineContextCall(x) for x in fhost]
    mhost = codegen.build_module(fhost, str(target_host))

    if fdevice:
        mdev = codegen.build_module(fdevice, str(target_device))
        mhost.import_module(mdev)
    return mhost
