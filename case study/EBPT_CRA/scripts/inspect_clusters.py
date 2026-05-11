from core.network import Network
n=Network(50,100,100,(50,50))
n.build()
print('CH ids:', [ch.id for ch in n.cluster_heads])
print('num CHs:', len(n.cluster_heads))
print('cluster sizes:', {ch.id: len(n.clusters[ch.id]) for ch in n.cluster_heads})
print('example cluster[0]:', [m.id for m in n.clusters[n.cluster_heads[0].id]])
