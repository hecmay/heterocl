import tvm
import keras
import tvm.relay.frontend as relay_front
import numpy as np
import heterocl as hcl
import hlib
import re
from ..utils import *
from .relay_attr import _attrib, _convert_map
from tvm.relay.expr import Function, Var, Call, Let, If, Constant
from tvm.relay.expr import TupleGetItem, Tuple
from tvm.relay.ty import TensorType, TupleType

debug_mode = False

def get_module(model, shape):
    """Gets the module (computation graph) and the parameters from the Keras model

    Parameters
    ----------
    model : str
        Path to model generated by Keras

    shape : dict
        Dictionary of input shapes into the model

    Returns
    -------
    module : tvm.relay.Module
        A relay module that contains the contents of the net

    params : dict of str to NDArray
        Parameters needed for the model
    """
    relay_model = keras.models.load_model(model)
    module, params = relay_front.from_keras(relay_model, shape)
    return module, params


def gen_params(type_dict, env):
    """Finds the parameters that we need to extract from the model

    Parameters
    ---------
    type_dict: dict
        the dictionary that contains the type of each variable in the environment

    env: dict
        the dictionary that contains the computational environment that sets up the
        contained function {key: value:}

    Returns
    -------
        a list of hcl.tensor.Tensor placeholders to hold the model params
    """

    params = []
    for var in type_dict:
        if type_dict[var] == Var:
            params.append(env[var])
        elif type_dict[var] == Tuple:
            for item in env[var]:
                if isinstance(item, hcl.tensor.Tensor):
                    update_if(env, {item.name: item})
    return params


def tuple_extract(tup, dict_t, env):
    """takes a tuple and returns all the objects inside of it in a flat list

    Parameters
    ---------
    tup: tuple
        the tuple of objects we're trying to infer from

    type_dict: dict
        a dictionary of each object's type

    env: dict
        a dictionary of each object's computing environment

    Returns
    -------
        a list of objects
    """
    result = []
    if isPureList(tup):
        for item in tup:
            result.append(tuple_extract(item, dict_t, env))
    else:
        tp = dict_t[tup]
        if tp == Var:
            result.append(env[tup])
        if tp == Tuple:
            tup_env = env[tup]
            result.append(tuple_extract(tup_env[1], tup_env[2], tup_env[3]))
    return tuple(result)


def let_bind(ntype, *arg):
    """binds a computation to a variable

    Parameters
    ---------
    ntype: tvm.relay-expr
        the type of the binding

    *arg: list of arguments
        the arguments required for each ntype

    Returns
    -------
        the object we bind to the output
    """
    if debug_mode:
        print("In bind")
    if ntype == Call:
        #arg = (list of var names, type dictionary,
        # environment dictionary, input parameters)
        var = arg[0]
        call_var = var[-1]
        type_dict = arg[1]
        bind_env = arg[2]
        params = arg[3]
        call_type = type_dict[call_var]

        if call_type == Function:
            call_args = bind_env[var[-2]]
            call_env = (bind_env[call_var][2])[call_var]
            _var = call_env[0]
            _dict = call_env[1]
            _env = call_env[2]
            _size = call_env[3]
            new_params = []
            for arg in _var:
                if arg in params:
                    new_params.append(arg)
            _func = gen_func(new_params, _var, _dict, _env)
            return _func(*call_args)
        elif call_type == Call:
            _func = bind_env[call_var][1]
            _args = list(bind_env[call_var][2])
            _kwargs = bind_env[call_var][3]
            for i in range(len(_args)):
                item = _args[i]
                if isinstance(item, str):
                    if type_dict[item] == Call:
                        inner_func = bind_env[item][1]
                        inner_args = bind_env[item][2]
                        inner_kwargs = bind_env[item][3]
                        _args[i] = inner_func(*inner_args, **inner_kwargs)
            _args = tuple(_args)
            arg_list = []
            for _var in _args:
                arg_list.append(_var)
            return _func(*arg_list, **_kwargs)
    if ntype == Tuple:
        #arg = (list of var names, type dictionary,
        # environment dictionary for tuple)
        var = arg[0][0]
        env = arg[2]
        tup = env[var][1]
        dict_type = env[var][2]
        tup_env = env[var][3]
        return tuple_extract(tup, dict_type, tup_env)
    if ntype == Var:
        name = arg[0][0]
        return (arg[2])[name]
    else:
        print("Type not implemented yet")


def in_params(var, params):
    if not isinstance(var, hcl.tensor.Tensor):
        return False

    for par in params:
        is_shape = (var.shape == par.shape)
        is_name = (var.name == par.name)
        is_type = (var.dtype == par.dtype)
        if is_shape and is_name and is_type:
            return True
    return False


def get_type(ty, name):
    if isinstance(ty, TensorType):
        dtype = ty.dtype
        size = []
        for i in ty.shape:
            size.append(i.value)
        return hcl.placeholder(tuple(size), name, dtype)
    elif isinstance(ty, TupleType):
        t_vars = []
        for i in range(len(ty.fields)):
            var_name = name + "_" + str(i)
            t_vars.append(get_type(ty.fields[i], var_name))
        return tuple(t_vars)
    else:
        raise ValueError("Tensor type not implemented yet")


def get_item(env):
    tup_type = env[1]
    if tup_type == Var:
        _list = list(env[2])
        index = env[3]
        item = _list[index]
        if isinstance(item, tuple):
            name = env[0]
        else: #if the item is singular
            name = item.name
        inst_var = None
        inst_type = {name: Var}
        inst_env = {name: item}
    elif tup_type == Call:
        name = env[0]
        tup = env[2]
        index = env[3]
        inst_env = None
        inst_var = None
    return item, name, inst_type, inst_env, inst_var


def gen_code(item, params, var, type_dict, env):
    if debug_mode:
        print("Item:", item)
    if type_dict[item] == Function:
        if debug_mode:
            print("In Func")
        _var = env[0]
        _type_dict = env[1]
        _env = env[2]
        _size = env[3]
        _params = gen_params(type_dict, env)
        env[item] = gen_func(_params, _var, _type_dict, _env)
        type_dict[item] = Call
    elif type_dict[item] == Let:
        # Not used in Keras. Can be used for tensorflow
        if debug_mode:
            print("In Let")
        _ntype = env[item][0]
        _bind_var = env[item][1]
        _var = env[item][2]
        _dict = env[item][3]
        _env = env[item][4]
        env[item] = let_bind(_ntype, _var, _dict, _env, params)
        type_dict[item] = Var
    elif type_dict[item] == Call:
        if debug_mode:
            print("In Call")
        if not isinstance(env[item], hcl.tensor.Tensor):
            _func = env[item][1]
            _args = env[item][2]
            _kwargs = env[item][3]
            arg_list = []
            for _var in _args:
                if in_params(_var, params):
                    arg_list.append(_var)
                else:
                    if isinstance(_var, tuple):
                        for v in _var:
                            arg_list.append(v)
                    elif isinstance(_var, str):
                        if isinstance(env[_var], tuple):
                            var, env[_var] = gen_code(
                                _var, params, var, type_dict, env)
                            if type_dict[_var] == Tuple:
                                arg_list = env[_var]
                        else:
                            arg_list.append(env[_var])
                    else:
                        arg_list.append(_var)
            if len(arg_list) != 0:
                env[item] = _func(*arg_list, **_kwargs)
            else:
                env[item] = _func(**_kwargs)
            type_dict[item] = Var
        else:
            var, env[_var] = gen_code(_var, params, var, type_dict, env)
    elif type_dict[item] == Tuple:
        if not isinstance(env[item][0], hcl.tensor.Tensor):
            name = env[item][0]
            tup_res = env[item][1]
            tup = []
            for _var in tup_res:
                tup.append(env[_var])
            env[item] = tuple(tup)
        else:
            var.insert(0, item)
            env[item] = env[item]
    elif type_dict[item] == TupleGetItem:
        tup_name = env[item][2]
        index = env[item][3]
        tup = env[tup_name]
        env[item] = tup[index]
        type_dict[item] = Var
    var.remove(item)
    return var, env[item]


def gen_func(params, var, type_dict, env):
    args = []
    for _var in params:
        args.append(_var)

    def func(*args):
        if debug_mode:
            print("In func")
        _var = var
        while len(_var) != 0:
            item = _var[0]
            _var, env[item] = gen_code(item, args, _var, type_dict, env)
        return env[item]
    return func


def build_node_map(func, main=False, node_map=None, cur_length=[0]):
    if isinstance(func, Call):
        if node_map is not None:
            for node in node_map:
                if tvm.relay.analysis.alpha_equal(node, func):
                    return
        for arg in func.args:
            if isinstance(arg, Call):
                build_node_map(arg, main, node_map, cur_length)
            elif isinstance(arg, TupleGetItem):
                build_node_map(arg, main, node_map, cur_length)
            elif isinstance(arg, Tuple):
                build_node_map(arg, main, node_map, cur_length)
        if isinstance(func.op, Function):
            build_node_map(func.op, main, node_map, cur_length)
        if node_map is not None:
            node_map = update_if(node_map, {func: [cur_length[0], 0]})
            cur_length[0] += 1
        return
    elif isinstance(func, Let):
        build_node_map(func.value, main)
        build_node_map(func.body, main)
        return
    elif isinstance(func, Function):
        build_node_map(func.body, main)
        return
    elif isinstance(func, Tuple):
        if node_map is not None:
            if func in node_map:
                return
        for field in func.fields:
            build_node_map(field, main, node_map, cur_length)
        if node_map is not None:
            node_map = update_if(node_map, {func: [cur_length[0], 0]})
            cur_length[0] += 1
        return
    elif isinstance(func, TupleGetItem):
        if node_map is not None:
            if func in node_map:
                return
        build_node_map(func.tuple_value, main, node_map, cur_length)
        if node_map is not None:
            node_map = update_if(node_map, {func: [cur_length[0], 0]})
            cur_length[0] += 1
        return
    else:
        return


def relay_parser(model, shape, frontend='keras', dtype=hcl.Float()):
    hcl.init(dtype)
    defined_inputs = {}
    node_map = {}
    for item in shape:
        defined_inputs[item] = None
    if frontend == 'keras':
        try:
            keras_model = keras.models.load_model(model)
        except BaseException:
            keras_model = model
        module, params = relay_front.from_keras(keras_model, shape)
        if debug_mode:
            print(module)
        body = module.functions[module.global_var_map_["main"]]
        build_node_map(body.body, True, node_map, [0])

    def gen_call(node, name, opname):
        args = []
        var = []
        type_dict = {name: Call}
        env = {}
        for arg in node.args:
            temp_var, temp_type, temp_env = parse_rec(arg)
            if isinstance(arg, Var):
                var.append(temp_var[0])
                var = partial_flatten(var)
                args.append(temp_env[fst(temp_var[0])])
            elif isinstance(arg, Constant):
                var.append(temp_var)
                var = partial_flatten(var)
                args.append(temp_env[temp_var[0]])
                env.update(temp_env)
            elif isinstance(arg, Call):
                var.append(temp_var)
                var = partial_flatten(var)
                args.append(temp_env[temp_var[-1]][0])
                env.update(temp_env)
            elif isinstance(arg, TupleGetItem):
                if temp_env[temp_var[-1]][1] == Var:
                    item, item_name, temp_type, temp_env, inst_var = get_item(
                        temp_env[temp_var[-1]])
                    var.append(inst_var)
                    var = partial_flatten(var)
                    args.append(item)
                    env.update(temp_env)
                else:
                    args.append(temp_env[temp_var[-1]][0])
                    var.append(temp_var)
                    var = partial_flatten(var)
                    env.update(temp_env)
            elif isinstance(arg, Tuple):
                tup_var = temp_var[-1]
                temp_var = partial_flatten(temp_var)
                var.append(temp_var)
                var = partial_flatten(var)
                tup_env = {}
                t_name = temp_env[tup_var][0]
                t_res = temp_env[tup_var][1]
                t_dict = temp_env[tup_var][2]
                t_env = temp_env[tup_var][3]
                tup_env[tup_var] = (t_name, t_res, t_dict, t_env)
                args.append(tup_var)
                env.update(tup_env)
                update_if(env, t_env)
            type_dict.update(temp_type)
        var.append(name)
        kwargs = {}
        for i in range(len(args)):
            if hasattr(args[i], "name"):
                if args[i].name in var:
                    env[args[i].name] = args[i]
        if opname in _attrib:
            for attr in _attrib[opname]:
                kwargs[attr] = getattr(node.attrs, attr)
            env[name] = (name, _convert_map[opname], tuple(args), kwargs)
        else:
            env[name] = (name, tuple(args))
        if isinstance(node.op, Function):
            temp_var, temp_type, temp_env = parse_rec(node.op)
            var.append(opname)
            type_dict.update({opname: Function})
            env[opname] = (temp_var, temp_type, temp_env)
        return var, type_dict, env

    def parse_rec(node, init=False, global_env={}):
        if isinstance(node, (Call, Tuple)):
            if node_map[node][1] > 0:
                name = "%" + str(node_map[node][0])
                var = [name]
                type_dict = {}
                env = {}
                env[name] = global_env[name]
                return var, type_dict, env
            else:
                node_map[node][1] += 1

        if isinstance(node, Function):
            name = "%" + str(len(node_map))
            if debug_mode:
                print("Function: ", name)
            var = [name]
            type_dict = {name: Function}
            env = {}
            temp_var, temp_type, temp_env = parse_rec(node.body, global_env)
            if init:
                var = temp_var
                type_dict = temp_type
                env = temp_env
            else:
                env = update_if(
                    env, {
                        name: (
                            full_flatten(temp_var), temp_type, temp_env, len(node_map))})
        elif isinstance(node, Var):
            name = node.name_hint
            var = [name]
            type_dict = {name: Var}
            ty = node.type_annotation
            env = {}
            if node.name_hint in shape:
                dtype = ty.dtype
                if defined_inputs[name] is None:
                    env[name] = hcl.placeholder(shape[name], name, dtype)
                    defined_inputs[name] = env[name]
                else:
                    env[name] = defined_inputs[name]
            else:
                env[name] = get_type(ty, name)
            if debug_mode:
                print("Var: " + name)
        elif isinstance(node, Constant):
            name = "con(" + str(node.data) + ")"
            if debug_mode:
                print("Constant: " + name)
            var = [name]
            type_dict = {name: Constant}
            env = {}
            env[name] = hcl.scalar(float(node.data.asnumpy()))
        elif isinstance(node, TupleGetItem):
            index = node.index
            tup = node.tuple_value
            if isinstance(tup, Var):
                var_name = tup.vid.name_hint
                name = "get_" + var_name + "_" + str(index)
                ty = tup.type_annotation
                var = [name]
                type_dict = {name: TupleGetItem}
                env = {}
                env[name] = (name, Var, get_type(ty, var_name), index)
            elif isinstance(tup, Call):
                name = '%' + str(node_map[tup][0])
                get_name = 'get' + str(node_map[tup][0]) + "_" + str(index)
                if not hasattr(tup.op, "name"):
                    opname = '%' + str(node_map[tup][0] - 1)
                else:
                    opname = tup.op.name
                var, type_dict, env = gen_call(tup, name, opname)
                var.append(get_name)
                type_dict.update({get_name: TupleGetItem})
                env[get_name] = (get_name, TupleGetItem, name, index)
            if debug_mode:
                print("TupleGet: " + get_name)
        elif isinstance(node, Let):
            name = node.var.vid.name_hint
            if debug_mode:
                print("Let: " + name)
            var = [name]
            type_dict = {name: Let}
            env = {}
            args = []
            kwargs = {}
            ty = node.var.type_annotation
            bind_var = get_type(ty, name)
            value = node.value
            temp_var, temp_type, temp_env = parse_rec(value)
            if isinstance(value, Var):
                env = update_if(env, {name: (Var, bind_var, temp_type,
                                             temp_env[fst(temp_var[0])])})
            elif isinstance(value, Function):
                env = update_if(
                    env, {
                        name: (
                            Function, bind_var, temp_var, temp_type, temp_env)})
            elif isinstance(value, Tuple):
                env = update_if(
                    env, {
                        name: (
                            Tuple, bind_var, temp_var, temp_type, temp_env)})
            elif isinstance(value, TupleGetItem):
                item, get_name, get_type_, get_env, _ = get_item(
                    temp_env[temp_var[0]])
                temp_var = [get_name]
                temp_type = {get_name: get_type_}
                temp_env = {get_name: item}
                env = update_if(
                    env, {
                        name: (
                            get_type_[get_name], bind_var, temp_var, temp_type, temp_env)})
            elif isinstance(value, Call):
                if not hasattr(value.op, "name"):
                    opname = "%" + str(node_map[tup][0])
                else:
                    opname = value.op.name
                args = temp_env[temp_var[-1]][0]
                env = update_if(env, temp_env)
                for i in range(len(args)):
                    if hasattr(args[i], "name"):
                        if args[i].name in temp_var:
                            env[args[i].name] = args[i]
                if opname in _attrib:
                    for attr in _attrib[opname]:
                        kwargs[attr] = getattr(value.attrs, attr)
                env[name] = (Call,
                             bind_var,
                             temp_var,
                             temp_type,
                             temp_env)
            type_dict = update_if(type_dict, temp_type)
            temp_var, temp_type, temp_env = parse_rec(
                node.body)
            var.append(temp_var)
            type_dict = update_if(type_dict, temp_type)
            env = update_if(env, temp_env)
        elif isinstance(node, If):
            print("If not instantiated yet")
        elif isinstance(node, Tuple):
            name = "%" + str(node_map[node][0])
            if debug_mode:
                print("Tuple: " + name)
            var = []
            type_dict = {name: Tuple}
            env = {}
            tup_type_dict = {}
            tup_res = []
            tup = []
            tup_env = {}
            for field in node.fields:
                temp_var, temp_type, temp_env = parse_rec(field)
                tup.append(temp_var)
                tup_res.append(temp_var[-1])
                tup_type_dict.update(temp_type)
                tup_env.update(temp_env)
            var.append(tup)
            var.append([name])
            var = partial_flatten(var)
            update_if(type_dict, tup_type_dict)
            env.update(tup_env)
            env[name] = (name, tup_res, tup_type_dict, tup_env)
        elif isinstance(node, Call):
            if not hasattr(node.op, "name"):
                opname = '%' + str(node_map[node][0])
            else:
                opname = node.op.name
            name = '%' + str(node_map[node][0])
            if debug_mode:
                print("Call " + name + ":" + opname)
            var, type_dict, env = gen_call(node, name, opname)
        if not isinstance(node, Function):
            global_env[name] = env[name]
        return var, type_dict, env
    out_var, out_type, out_env = parse_rec(body, True)
    return out_var, out_type, out_env, params

# only used by user. Add comment


def get_relay_model(
        model,
        shape={},
        frontend='keras',
        dtype=hcl.Float(),
        in_params=None):
    """

    Parameters
    ----------

    model :
        A machine learning framework model

    shape : dict
        The model's input shape

    frontend : str
        The machine learning framework the model comes from

    dtype : heterocl type
        The model's preferred data type

    in_params :
        The input parameters of the model if not included in the model
    """
    out_var, out_type, out_env, params = relay_parser(model, shape, frontend)
    out_var = full_flatten(out_var)
    _param = gen_params(out_type, out_env)
    v_param = [holder for holder in _param if ("_param" in holder.name)]
    v_input = [holder for holder in _param if ("input" in holder.name)]
    v_param.sort(
        key=lambda x: int(
            ''.join(
                filter(
                    lambda i: i.isdigit(),
                    x.name))))
    v_input.sort(
        key=lambda x: int(
            ''.join(
                filter(
                    lambda i: i.isdigit(),
                    x.name))))
    _param = partial_flatten([v_input, v_param])
    func = gen_func(_param, out_var, out_type, out_env)
    _inputs = []
    if params is None:
        params = in_params
    for var in params:
        _inputs.append(hcl.asarray(params[var].asnumpy()))
    s = hcl.create_schedule(_param, func)
    if debug_mode:
        print(hcl.lower(s))
    return hcl.build(s), _inputs
