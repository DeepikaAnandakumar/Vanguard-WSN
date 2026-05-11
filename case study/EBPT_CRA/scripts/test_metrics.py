import importlib
try:
    m = importlib.import_module('clustering.metrics')
    print('module file:', m.__file__)
    print('members:', [n for n in dir(m) if not n.startswith('__')])
except Exception as e:
    print('IMPORT ERROR:', e)
