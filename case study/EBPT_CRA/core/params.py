
# Simulation Parameters

# Network
NUM_NODES = 100
FIELD_X = 100
FIELD_Y = 100

# Energy (Joules)
INITIAL_ENERGY = 0.5
E_ELEC = 50e-9   # Energy for running radio electronics
E_DA = 5e-9      # Energy for Data Aggregation (J/bit/signal)
E_MP = 0.0013e-12 # (Not always used in first order, but standard LEACH param) - check first_order_radio
EPS_FS = 10e-12  # Free space model
EPS_MP = 0.0013e-12 # Multipath model

# Data
DATA_BITS = 2000
AGGR_RATIO = 1.0 # Aggregation ratio (1.0 means no aggregation, pure forwarding)
                 # Usually LEACH assumes perfect aggregation -> constant size packet. 
                 # Here we might imply output is 10% of input sum? or standard LEACH 'single packet out'.

# Routing / Clustering
CH_PROB = 0.05
TRANSMISSION_RANGE = 70 # Standard clustering range for 100x100 field

# Heterogeneity (IEEE/Scopus Enhancement)
HETEROGENEITY_ENABLED = False
HETEROGENEITY_M = 0.1   # Fraction of advanced nodes
HETEROGENEITY_ALPHA = 1.0 # Energy multiplier for advanced nodes (E_adv = E_init * (1 + alpha))
