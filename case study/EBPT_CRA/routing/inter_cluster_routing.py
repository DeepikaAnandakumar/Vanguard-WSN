def route_ch_to_bs(cluster_heads, forwarders, bs):
    paths = {}

    for ch in cluster_heads:
        # If no forwarders available, CH sends directly to BS
        if not forwarders:
            paths[ch.id] = [ch.id, "BS"]
            continue

        # Choose nearest forwarder
        fwd = min(forwarders, key=lambda f: ch.distance_to(f))
        paths[ch.id] = [ch.id, fwd.id, "BS"]

    return paths
