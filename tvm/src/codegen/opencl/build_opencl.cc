/*
    Yang.Bai
    yb269@cornell.edu
*/

# include <tvm/runtime/packed_func.h>
# include <memory>
# include <string>
# include <vector>
# include <unordered_map>
# include "../../runtime/meta_data.h"
# include <tvm/base.h>
# include "./codegen_sdaccel.h"
# include "./codegen_aocl.h"
# include "./codeanalys_openclc.h"
# include "../build_common.h"
// # include "./sdaccel/sdaccel_module.h"
// # include "./aocl/aocl_module.h"




namespace TVM {
namespace codegen {


#if HCL_SDACCEL_RUNTIME
runtime::Module BuildSDAccelSim(Array<LoweredFunc> funcs) {
  CodeAnalysOpenCLC ca;
  CodeGenSDACCEL cg;
  for (LoweredFunc f : funcs) {
    // 1st pass: Analyze AST and collect necessary information
    ca.AddFunction(f);
    str2tupleMap<std::string, Type> map_arg_type;
    map_arg_type = ca.Finish();
    // 2nd pass: Generate kernel code
    cg.AddFunction(f, map_arg_type);
  }
  std::string code = cg.Finish();

  return runtime::CreateSDAccelModule(funcs[0], code);
}

TVM_REGISTER_API("codegen.sdaccel_sw_emu")
.set_body([](TVMArgs args, TVMRetValue* rv) {
    *rv = BuildSDAccelSim(args[0]);
  });
#endif






template<class CodeGen>
std::string BuildOpenCL(Array<LoweredFunc> funcs){
    using TVM::runtime::Registry;
    CodeAnalysOpenCLC ca;
    CodeGen cg;
    for(LoweredFunc f: funcs){
        ca.AddFunction(f);
        str2tupleMap<std::string, Type>map_arg_type;
        map_arg_type = ca.Finish();

        cg.AddFunction(f, map_arg_type);
    }
    std::string code = cg.Finish();

    if (const auto* f = Registry::Get("tvm_callback_opencl_postproc")) {
        code = (*f)(code).operator std::string();
    }

    LOG(WARNING) << "OpenCL doesn't have runtime, return kernel code";
    return code;
}




TVM_REGISTER_API("codegen.build_sdaccel")
.set_body([]( TVMArgs args, TVMRetValue * rv ) {
    * rv = BuildOpenCL<CodeGenSDACCEL>(args[0]);
    });

TVM_REGISTER_API("codegen.build_aocl")
.set_body([]( TVMArgs args, TVMRetValue * rv ) {
    * rv = BuildOpenCL<CodeGenAOCL>(args[0]);
    });
}
}
