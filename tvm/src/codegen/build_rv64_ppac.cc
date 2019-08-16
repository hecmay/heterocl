/*
    author Guyue Huang (gh424@cornell.edu)
 */

#include "./codegen_rv64_ppac.h"
#include "./build_common.h"

namespace TVM{
namespace codegen{

std::string BuildRV64PPAC(Array<LoweredFunc> funcs) {
    //CodeAnalysMerlinC ca;
    CodeGenRV64PPAC cg;
    for (LoweredFunc f: funcs) {
        //ca.AddFunction(f);
        //str2tupleMap<std::string, Type> map_arg_type;
        //map_arg_type = ca.Finish();
        cg.AddFunction(f);
    }
    std::string code = cg.Finish();
    LOG(WARNING) << "RV64_PPAC backend doesn't yet have runtime, return kernel code";
    return code;
}

TVM_REGISTER_API("codegen.build_rv64_ppac")
.set_body([](TVMArgs args, TVMRetValue* rv) {
    *rv = BuildRV64PPAC(args[0]);
  });

}
}