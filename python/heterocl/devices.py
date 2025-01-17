"""Define HeteroCL device types"""
#pylint: disable=too-few-public-methods, too-many-return-statements
from .debug import DeviceError
from .tools import option_table, model_table
from future.utils import with_metaclass

class tooling(type):
    def __getattr__(cls, key):
        if key in option_table:
           return cls(key, *option_table[key])
        else: # unsupported device
           raise DeviceError("not supported")

class tool(with_metaclass(tooling, object)):
    """The base class for all device tooling

    mode (sim/impl) is decided by tool configuration
    e.g. run sw emulation by passing gcc / vivado_hls arg
    and actual impl by passing sdaccel / aocl arg 

    Parameters
    ----------
    types: str
        Device of device to place data
    model: str
        Model of device to place date
    """
    def __init__(self, name, mode, kwargs):
        self.name = name
        self.mode = mode
        self.options = kwargs

    def __getattr__(self, entry):
        return self.mapping[entry] 

    def __call__(self, mode, setting={}):
        self.mode = mode
        self.options = setting
        return self

    def __str__(self):
        return str(self.name) + "-" + \
               str(self.mode) + ":\n" + \
               str(self.options)

    def __repr__(self):
        return str(self.name) + "-" + \
               str(self.mode) + ":\n" + \
               str(self.options)

tool_table = {
  "aws_f1"      : tool("sdaccel", *option_table["sdaccel"]),
  "zc706"       : tool("vivado_hls", *option_table["vivado_hls"]),
  "ppac"        : tool("rocket", *option_table["rocket"]),
  "stratix10_sx": tool("aocl", *option_table["aocl"]),
  "llvm"        : tool("llvm", *option_table["llvm"])
}

class Device(object):
    """The base class for all device types

    The default data placement is on CPU.

    Parameters
    ----------
    types: str
        Device of device to place data
    model: str
        Model of device to place date
    """
    def __init__(self, types, vendor, 
                 model, **kwargs):
        self.vendor = vendor
        self.types = types
        self.model = model
        self.impls = {"lang": ""}
        for key, value in kwargs.items(): 
            self.impls[key] = value

    def __getattr__(self, key):
        """ device hierarchy """
        return self.impls[key] 

    def set_lang(self, lang):
        assert lang in \
            ["opencl", "hlsc", "c", "opengl", "merlinc", "cuda", "metal"], \
            "unsupported lang sepc " + lang
        self.impls["lang"] = lang
        return self

class CPU(Device):
    """cpu device with different models"""
    def __init__(self, vendor, model, **kwargs):
        if vendor not in ["riscv", "arm", "intel", "sparc", "powerpc"]: 
            raise DeviceError(vendor + " not supported yet")
        assert "cpu_" + model in model_table[vendor], \
            model + " not supported yet"
        super(CPU, self).__init__("CPU", vendor, model, **kwargs)
    def __repr__(self):
        return "cpu-" + self.vendor + "-" + str(self.model) + \
               ":" + self.impls["lang"]

class FPGA(Device):
    """fpga device with different models"""
    def __init__(self, vendor, model, **kwargs):
        if vendor not in ["xilinx", "intel"]: 
            raise DeviceError(vendor + " not supported yet")
        assert "fpga_" + model in model_table[vendor], \
            model + " not supported yet"
        super(FPGA, self).__init__("FPGA", vendor, model, **kwargs)
    def __repr__(self):
        return "fpga-" + self.vendor + "-" + str(self.model) + \
               ":" + self.impls["lang"]

class GPU(Device):
    """gpu device with different models"""
    def __init__(self, vendor, model, **kwargs):
        if vendor not in ["nvidia", "amd"]: 
            raise DeviceError(vendor + " not supported yet")
        assert "gpu_" + model in model_table[vendor], \
            model + " not supported yet"
        super(GPU, self).__init__("GPU", vendor, model, **kwargs)
    def __repr__(self):
        return "gpu-" + self.vendor + "-" + str(self.model) + \
               ":" + self.impls["lang"]

class PIM(Device):
    """cpu device with different models"""
    def __init__(self, vendor, model, **kwargs):
        if model not in ["ppac"]: 
            raise DeviceError(model + " not supported yet")
        super(PIM, self).__init__("PIM", vendor, model, **kwargs)
    def __repr__(self):
        return "pim-" + str(self.model)

dev_table = {
  "aws_f1" : [CPU("intel", "e5"), FPGA("xilinx", "xcvu19p")],
  "zc706" : [CPU("arm", "a9"), FPGA("xilinx", "xc7z045")],
  "rocc-ppac" : [CPU("riscv", "riscv"), PIM("ppac", "ppac")],
  "stratix10_sx": [CPU("arm", "a53"), FPGA("intel", "stratix10_sx")]
}

class env(type):
    """The platform class for compute environment setups
    
     serves as meta-class for attr getting
     default platform: aws_f1, zynq, ppac

    Parameters
    ----------
    host: str
        Device of device to place data
    model: str
        Model of device to place date
    """
    def __getattr__(cls, key):
        if key == "aws_f1":
            devs = dev_table[key]
            host = devs[0].set_lang("opencl")
            xcel = devs[1].set_lang("hlsc")
        elif key == "zc706":
            devs = dev_table[key]
            host = devs[0].set_lang("hlsc")
            xcel = devs[1].set_lang("hlsc")
        elif key == "stratix10_sx":
            devs = dev_table[key]
            host = devs[0].set_lang("opencl")
            xcel = devs[1].set_lang("aocl")
        elif key == "llvm":
            devs = None 
            host = None 
            xcel = None 
        elif key == "ppac":
            devs = dev_table["rocc-ppac"]
            host = devs[0].set_lang("c")
            xcel = None 
        else: # unsupported device
            raise DeviceError("not supported")
        tool = tool_table[key]
        return cls(key, devs, host, xcel, tool)
           
class platform(with_metaclass(env, object)):
    def __init__(self, name, devs, host, xcel, tool):
        self.name = name
        self.devs = devs
        self.host = host
        self.xcel = xcel
        self.tool = tool

        if isinstance(host, CPU):
            self.cpu = host
        if isinstance(xcel, FPGA):
            self.fpga = xcel
        elif isinstance(xcel, PIM) and \
             xcel.model == "ppac":
            self.ppac = xcel

    def __getattr__(self, key):
        """ return tool options """
        return self.tool.__getattr__(key)
   
    def __call__(self, tooling=None):
        if tooling: # check and update
            assert isinstance(tooling, tool)
            self.tool = tooling
        return self

    def __str__(self):
        return str(self.name) + "(" + \
               str(self.host) + " : " + \
               str(self.xcel) + ")"

    def __repr__(self):
        return str(self.name) + "(" + \
               str(self.host) + " : " + \
               str(self.xcel) + ")"

def device_to_str(dtype):
    """Convert a device type to string format.

    Parameters
    ----------
    dtype : Device or str
        The device type to be converted

    Returns
    -------
    str
        The converted device type in string format.
    """
    if isinstance(dtype, Device):
        if isinstance(dtype, CPU):
            return "cpu_" + str(dtype.model)
        elif isinstance(dtype, FPGA):
            return "fpga_" + str(dtype.model)
    else:
        if not isinstance(dtype, str):
            raise DeviceError("Unsupported device type format")
        return dtype

def device_to_hcl(dtype):
    """Convert a device type to Heterocl type.

    Parameters
    ----------
    dtype : Device or str
        The device type to be converted

    Returns
    -------
    Device
    """
    if isinstance(dtype, Device):
        return dtype
    elif isinstance(dtype, str):
        device, model = dtype.split("_") 
        if device == "cpu":
            return CPU(model)
        elif device == "gpu":
            return GPU(model)
        elif device == "fpga":
            return FPGA(model)
        else:
            raise DeviceError("Unrecognized device type")
    else:
        raise DeviceError("Unrecognized device type format")

def get_model(dtype):
    """Get the model of a given device type.

    Parameters
    ----------
    dtype : Device or str
        The given device type

    Returns
    -------
    str
    """
    dtype = dtype_to_hcl(dtype)
    return dtype.types, dtype.model

