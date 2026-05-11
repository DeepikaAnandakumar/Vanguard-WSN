import importlib
m = importlib.import_module('energy.first_order_radio')
print('module loaded:', m)
print('has tx_energy:', hasattr(m, 'tx_energy'))
print('tx_energy repr:', getattr(m, 'tx_energy', None))
print('module file:', getattr(m, '__file__', None))