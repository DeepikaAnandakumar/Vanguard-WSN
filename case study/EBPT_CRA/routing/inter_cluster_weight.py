from energy.first_order_radio import ETX, ERX

A, B, C = 0.6, 0.1, 0.3
DATA_BITS = 2500


def inter_cluster_weight(i, j, bs):
    """
    Inter-cluster routing weight:
    W_ij = a*E(i)/ETX + b*E(j)/ERX + c*E(j)/ETX_to_BS

    Treat BS specially: BS energy is infinite, which would make weights infinite
    and prevent any path reaching the BS. Cap or replace BS energy for weight
    computation so edges to BS remain finite and represent the actual link cost.
    """
    if i.energy <= 0:
        return float("inf")

    # Treat BS as special case to avoid infinite weights
    if getattr(j, 'id', None) == 'BS' or j is bs:
        j_energy = 1.0
    else:
        if j.energy <= 0:
            return float("inf")
        j_energy = j.energy

    d_ij = i.distance_to(j)
    d_jbs = j.distance_to(bs)

    return (
        A * i.energy / ETX(DATA_BITS, d_ij)
        + B * j_energy / ERX(DATA_BITS)
        + C * j_energy / ETX(DATA_BITS, d_jbs)
    )
