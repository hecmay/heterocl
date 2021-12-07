import os, subprocess, time, re, glob
from ..mutator import Mutator
from . import expr as _expr
from . import stmt as _stmt
from . import make as _make


def replace_text(f_name, prev, new):
    with open(f_name, 'r') as fp:
        data = fp.read()
    data = data.replace(prev, new)
    with open(f_name, 'w') as fp:
        fp.write(data)


def run_process(cmd, pattern=None, env=None, debug=True):
    if debug: print("[DEBUG] Running commands: \n{}\n".format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if err: raise RuntimeError("Error raised: ", err.decode())
    if pattern: return re.findall(pattern, out.decode("utf-8"))
    if debug: 
        print("[DEBUG] Commands outputs: \n{}\n".format(out.decode("utf-8")))
    return out.decode("utf-8")


class ExtractAttachingStages(Mutator):
    def __init__(self):
        self.children_stages = list()

    def mutate_AttrStmt(self, node):
        value = self.mutate(node.value)
        body = self.mutate(node.body)

        if node.attr_key == "attach_scope":
            self.children_stages.insert(0, node.node)

        return _make.AttrStmt(node.node, node.attr_key, value, body)

    def analyze(self, body):
        self.mutate(body)
        return self.children_stages

def get_attaching_stages(body):
    return ExtractAttachingStages().analyze(body)

# TODO: add visitor to extract tensor shape
def get_update_tensor_shape(stage):
    return [10, 32]

def post_process_hls_code(path):
    img_lib_path = os.path.dirname(os.path.abspath(__file__)) + "/../harness/imageLib/"
    run_process("cp " + img_lib_path + "* ./project/")
    return True