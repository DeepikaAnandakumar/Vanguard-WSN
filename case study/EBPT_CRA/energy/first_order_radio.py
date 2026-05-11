E_ELEC = 50e-9
E_FS = 10e-12

def tx_energy(bits, distance):
    return bits * (E_ELEC + E_FS * distance * distance)

def rx_energy(bits):
    return bits * E_ELEC

# Aliases for compatibility
ETX = tx_energy
ERX = rx_energy
