import importlib
m = importlib.import_module('routing.ebpt')
print('module loaded:', m)
print('members:', [n for n in dir(m) if not n.startswith('__')])