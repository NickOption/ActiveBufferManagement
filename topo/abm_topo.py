from mininet.topo import Topo
from mininet.link import TCLink

class ABMTopo(Topo):
    def build(self):
        # senders
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        # receiver
        h5 = self.addHost('h5')

        # switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        # host links
        self.addLink(h1, s1, cls=TCLink, bw=100)
        self.addLink(h2, s1, cls=TCLink, bw=100)
        self.addLink(h3, s2, cls=TCLink, bw=100)
        self.addLink(h4, s2, cls=TCLink, bw=100)
        self.addLink(h5, s2, cls=TCLink, bw=100)

        # bottleneck/core links
        self.addLink(s1, s3, cls=TCLink, bw=10, delay='5ms', max_queue_size=100)
        self.addLink(s2, s3, cls=TCLink, bw=10, delay='5ms', max_queue_size=100)

topos = {'abm': ABMTopo}
