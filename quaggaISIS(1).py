#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting four IP subnets"

    def build( self, **_opts ):

        defaultIP1 = '192.168.5.1/30'	# IP address for r1-eth1
        defaultIP2 = '192.168.5.2/30'	# IP address for r2-eth1
        defaultIP3 = '192.168.5.6/30'	# IP address for r3-eth1
        defaultIP4 = '192.168.5.9/30'  # IP address for r4-eth1
        
        router1 = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP1)
        router2 = self.addNode( 'r2', cls=LinuxRouter, ip=defaultIP2)
        router3 = self.addNode( 'r3', cls=LinuxRouter, ip=defaultIP3)
        router4 = self.addNode( 'r4', cls=LinuxRouter, ip=defaultIP3) 
       
	
        h1 = self.addHost( 'h1', ip='192.168.0.2/24', defaultRoute='via 192.168.0.1') #define gateway
        h2 = self.addHost( 'h2', ip='192.168.3.2/24', defaultRoute='via 192.168.3.1')
        h3 = self.addHost( 'h3', ip='192.168.1.2/24', defaultRoute='via 192.168.1.1') #define gateway
        h4 = self.addHost( 'h4', ip='192.168.4.2/24', defaultRoute='via 192.168.4.1')

	self.addLink(router1,router2,intfName1= 'r1-eth1',intfName2='r2-eth1')
	#self.addLink(router2,router1, intfName1= 'r2-eth1',intfName2='r1-eth1')
	self.addLink(router2,router3,intfName1= 'r2-eth2',params1={ 'ip' : '192.168.5.5/30' },intfName2='r3-eth1')
	#self.addLink(router3,router2,intfName1= 'r3-eth1',intfName2='r3-eth1')
	self.addLink(router4,router3,intfName1= 'r4-eth1',intfName2='r3-eth2',params2={ 'ip' : '192.168.5.10/30' })
	
	#self.addLink(router1,router4,intfName1= 'r1-eth3',params1={ 'ip' : '192.168.5.14/30' },intfName2='r4-eth1')
	
	self.addLink(router4,router1,intfName1= 'r4-eth2' ,params1={ 'ip' : '192.168.5.14/30'},intfName2='r1-eth2',params2={ 'ip' : '192.168.5.13/30' })
	
	self.addLink(h1,router1,intfName2='r1-eth0',params2={ 'ip' : '192.168.0.1/24' })#params2 define the eth0 ip address
	self.addLink(h2,router2,intfName2='r2-eth0',params2={ 'ip' : '192.168.3.1/24' })
	self.addLink(h3,router3,intfName2='r3-eth0',params2={ 'ip' : '192.168.1.1/24' })
	self.addLink(h4,router4,intfName2='r4-eth0',params2={ 'ip' : '192.168.4.1/24' })#params2 define the eth0 ip address
	
	
	

	
def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet(controller = None, topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
    #info( net[ 'r1' ].cmd( 'route' ) )

    r1=net.getNodeByName('r1')
    r2=net.getNodeByName('r2')
    r3=net.getNodeByName('r3')
    r4=net.getNodeByName('r4')
    info('starting zebra and isisd service:\n')


    r1.cmd('zebra -f /usr/local/etc/quagga/local/etc/r1zebra.conf -d -z ~/Desktop/r1zebra.api -i ~/Desktop/r1zebra.interface')    
    r2.cmd('zebra -f /usr/local/etc/quagga/local/etc/r2zebra.conf -d -z ~/Desktop/r2zebra.api -i ~/Desktop/r2zebra.interface')
    r3.cmd('zebra -f /usr/local/etc/quagga/local/etc/r3zebra.conf -d -z ~/Desktop/r3zebra.api -i ~/Desktop/r3zebra.interface')
    r4.cmd('zebra -f /usr/local/etc/quagga/local/etc/r4zebra.conf -d -z ~/Desktop/r4zebra.api -i ~/Desktop/r4zebra.interface')
    time.sleep(1)#time for zebra to create api socket

    r1.cmd('isisd -f /usr/local/etc/quagga/local/etc/r1isisd.conf -d -z ~/Desktop/r1zebra.api -i ~/Desktop/r1isisd.interface')
    r2.cmd('isisd -f /usr/local/etc/quagga/local/etc/r2isisd.conf -d -z ~/Desktop/r2zebra.api -i ~/Desktop/r2isisd.interface')
    r3.cmd('isisd -f /usr/local/etc/quagga/local/etc/r3isisd.conf -d -z ~/Desktop/r3zebra.api -i ~/Desktop/r3isisd.interface')
    r4.cmd('isisd -f /usr/local/etc/quagga/local/etc/r4isisd.conf -d -z ~/Desktop/r4zebra.api -i ~/Desktop/r4isisd.interface')

    info( net[ 'r1' ].cmd( 'route' ) )
    info( net[ 'r2' ].cmd( 'route' ) )
    info( net[ 'r3' ].cmd( 'route' ) )
    info( net[ 'r4' ].cmd( 'route' ) )
       
    CLI( net )
    net.stop()
    os.system("killall -9 isisd zebra")
    os.system("rm -f *api*")
    os.system("rm -f *interface*")

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

