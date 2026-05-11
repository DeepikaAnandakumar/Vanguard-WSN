import importlib, inspect
m = importlib.import_module('clustering.ch_selection')
print('module file:', m.__file__)
print(inspect.getsource(m))