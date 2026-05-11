def select_forwarders(nodes, bs, k=5):
    # Clear previous forwarder flags
    for n in nodes:
        try:
            n.is_forwarder = False
        except Exception:
            pass

    # Nodes closest to BS
    nodes_sorted = sorted(
        [n for n in nodes if getattr(n, 'alive', True)],
        key=lambda n: n.distance_to(bs)
    )

    forwarders = nodes_sorted[:k]

    for f in forwarders:
        f.is_forwarder = True

    return forwarders

