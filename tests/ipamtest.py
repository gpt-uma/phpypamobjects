#!/usr/bin/python3
"""Test of the library"""

# Initialize logger to provide debugging from the 
import logging, sys, os
mylogger = logging.getLogger()
logging.basicConfig(format='%(asctime)s:%(name)s:%(filename)s(line %(lineno)d)/%(funcName)s:%(levelname)s:%(message)s',stream=sys.stderr, level=logging.DEBUG)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import re

from phpypamobjects import ipamServer, ipamAddress, ipamSubnet, ipamScanAgent

# You can set the following variables in your environment to connect the phpIPAM service.
# You can override the values of the environment variables with function arguments
# If you don't set the password, it will be asked for in the console

# export MYIPAM_URL="https://myphpipam.example.com"
# export MYIPAM_APPID="myipamclient"
# export MYIPAM_TOKEN="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
# export MYIPAM_USER="myipamuser"
# export MYIPAM_CACERT="NONE"
# export MYIPAM_PASSWD="ppppppppppppppppppppp"

# Connect a phpIPAM service (values for not specified arguments come from environment variables)
ipam = ipamServer(
    # url='https://myphpipam.example.com',
    # app_id='myipamclient',
    # token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    # user='myipamuser',
    # cacert= "NONE",
    # password='ppppppppppppppppppppp'
)

# Get only /24 subnets
subnets=[sn for sn in ipam.getAllSubnets() if sn.getMask() == '24']

# Get addresses from those subnets matching a pattern in the description
aList = [a for sn in subnets for a in ipam.findIPsbyNet(sn) if re.match(r".*ldap.*", a.getHostname())]

# Get all subnets scanned by second scanning agent
agent = [agent for agent in ipam.getAllScanAgents()][1]
scannedSubnets = [sn for sn in ipam.getAllSubnets() if sn.scanAgent == agent.getId()]
for sn in scannedSubnets:
    # Print subnet description
    print(f'{sn} -- last scanned at: {sn.getLastRescan()} -- last discovered at: {sn.getLastDiscovery()}')


for sn in subnets:
    # Print subnet description
    print(f'{sn} -- last scanned at: {sn.getLastRescan()} -- last discovered at: {sn.getLastDiscovery()}')

    # Find all IPs of this subnet
    aList = ipam.findIPsbyNet(sn)
    
    # Print all IPs of this subnet
    for a in aList:
        # Print IP address description
        print(a)

        # Some fancy operations using ipaddress library
        if a.getIP() in sn.getSubnet():
            print(f'{a} is in {sn}')
        else:
            print(f'{a} is NOT in {sn}')
