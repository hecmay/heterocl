from setuptools import setup, find_packages
import os
import sys

CURRENT_DIR = os.path.dirname(__file__)

def get_lib_path():
    """Get library path, name and version"""
    # We can not import `libinfo.py` in setup.py directly since __init__.py
    # Will be invoked which introduces dependences
    libinfo_py = os.path.join(CURRENT_DIR, '../../python/heterocl/tvm/_ffi/libinfo.py')
    libinfo = {'__file__': libinfo_py}
    exec(compile(open(libinfo_py, "rb").read(), libinfo_py, 'exec'), libinfo, libinfo)
    version = libinfo['__version__']
    lib_path = libinfo['find_lib_path']()
    libs = [lib_path[0]]
    if libs[0].find("runtime") == -1:
        for name in lib_path[1:]:
            if name.find("runtime") != -1:
                libs.append(name)
                break
    return libs, version

LIB_LIST, __version__ = get_lib_path()

curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
for i, path in enumerate(LIB_LIST):
    LIB_LIST[i] = os.path.relpath(path, curr_path)
setup_kwargs = {
    "include_package_data": True,
    "data_files": [('lib', LIB_LIST)]
}

setup(
  name = "hlib",
  version = "0.1",
  packages = find_packages(),
  install_requires=[
      'numpy==1.16.1',
      'decorator',
      'networkx==2.2',
      'matplotlib==2.2.3',
      'backports.functools_lru_cache==1.2.1',
      'ordered_set',
      'keras',
      'tensorflow',
      'tvm',
      ],
  **setup_kwargs)


