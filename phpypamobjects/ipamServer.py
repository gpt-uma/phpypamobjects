#!/usr/bin/python3
"""This file provides management for connecting to a phpIPAM service and operating on it."""

# Initialize logger
import logging
mylogger = logging.getLogger()

import sys, os, getpass, ssl, certifi
from typing import Any
import re
import numpy as np

try:
    import phpypam
except Exception as e:
    mylogger.critical(f"{str(e)}")
    mylogger.critical(f"Install modules: phpypam setuptools \n\twith 'pip3 install <module1> <module2> ...'")
    sys.exit(1)

from .ipamSubnet import ipamSubnet
from .ipamAddress import ipamAddress, ipamTags
from .ipamScanAgent import ipamScanAgent

from ipaddress import IPv4Address, IPv6Address, IPv4Network, IPv6Network, ip_address, ip_network

class ipamServer:
    """Manages a connection to a phpIPAM service and high level operations on addresses."""
    def __init__(self, url:str = "", app_id:str = "", token:str= "", user:str = "", password:str = "", cacert:str = "") -> None:
        """Opens the connection to the service.
        :param url: The URL of the phpIPAM service.
        :param app_id: This is the identifier string of the client application operating at the phpIPAM service. It must have been registered before at the service and permissions given to access resources.
        :param token: When defining an application at the service, an exclusive access token is created to identify the client.
        :param username: The client can also authenticate using an username and a password.
        :param password: This is the password if a username is provided for authentication.
        """
        
        # Get default parameters from environment
        self.url = os.getenv("MYIPAM_URL","")
        self.app_id = os.getenv("MYIPAM_APPID","")
        self.token = os.getenv("MYIPAM_TOKEN","")
        self.user = os.getenv("MYIPAM_USER","")
        self.cacert = os.getenv("MYIPAM_CACERT","")

        # Replace environment with arguments if present
        if url:
            self.url = url
        if url:
            self.app_id = app_id
        if user:
            self.user = user
        if cacert:
            self.cacert = cacert

        # Get password from environment and replace it by argument if not null
        if not password:
            password = os.getenv("MYIPAM_PASSWD","")
        # Read password from console if null
                # Get cacert from environment
        if not password:
            password = self._getpassword()

        if not password:
            raise Exception("Empty password. Can't connect to any server.")

        if self.cacert != "NONE":
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(self.cacert)
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
        else:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        # Create the API for IPAM service
        try:
            self.pi:phpypam.api = phpypam.api(
                url=self.url,
                app_id=self.app_id,
                token=self.token,
                encryption=False,
                username=self.user,
                password=password,
                ssl_verify=False
            )
            #controllers = pi.controllers()
        except Exception as e:
            raise Exception(f"Error connecting to IPAM server {url}:") from e

    def _getpassword(self) -> str:
        """Read a string from console disabling terminal echo for privacy.
        
            Returns: An string or an exception if CTRL-C is pressed.
        """
        try:
            # Prompt the user for a password (the default prompt is "Password:")
            password = getpass.getpass("Password: ")
        except KeyboardInterrupt:
            mylogger.error("Operation canceled by user")
            password = ''
        except Exception:
            mylogger.error("Error reading password from console")
            password = ''

        return password
        
    def getAllSections(self) -> list[Any]:
        try:
            return self.pi.get_entity(controller='sections') # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []
    
    def getAllSubnets(self) -> list[ipamSubnet]:
        """Get all the subnets defined at the phpIPAM service.
        :return: An array with ipamSubnet objects representing the subnets."""
        try:
            return [ipamSubnet(s) for s in self.pi.get_entity(controller='subnets')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []
    
    def getAllAddresses(self) -> list[ipamAddress]:
        """Get all the IP addresses defined at the phpIPAM service.
        :return: An array with ipamAddress objects representing the addresses."""
        try:
            return [ipamAddress(addr=a) for a in self.pi.get_entity(controller='addresses')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []
            
    def getAllVLANs(self) -> list[Any]:
        """Get all the VLANs defined at the phpIPAM service.
        :return: An array with dictionary objects representing the addresses."""
        try:
            return self.pi.get_entity(controller='vlan') # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    def getAllScanAgents(self) -> list[ipamScanAgent]:
        """Get all the Scan Agents defined at the phpIPAM service.
        :return: An array with dictionary objects representing the scanners."""
        try:
            return [ipamScanAgent(agent) for agent in self.pi.get_entity(controller='tools/scanagents')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    ################################################

    def updateScanAgent(self, agent:ipamScanAgent) -> None:
        """Update the last access date of a scan agent.
        :param agent: The scan agent to update."""
        params = agent.updateLastAccess()
        self.pi.update_entity(controller='tools/scanagents', controller_path=f'{agent.getId()}', params=params)

    def updateSubnetLastScan(self, subnet:ipamSubnet) -> None:
        """Update the last scan date of a subnet.
        :param subnet: The subnet to update."""
        params = subnet.updateLastScan()
        self.pi.update_entity(controller='subnets', controller_path=f'{subnet.getId()}', params=params)

    def updateSubnetLastDiscovery(self, subnet:ipamSubnet) -> None:
        """Update the last scan date of a subnet.
        :param subnet: The subnet to update."""
        params = subnet.updateLastDiscovery()
        self.pi.update_entity(controller='subnets', controller_path=f'{subnet.getId()}', params=params)

    def updateAddress(self, address:ipamAddress) -> None:
        """Update the last scan date of a subnet.
        :param address: The address to update."""
        params = {}
        for key in address._updated:
            params[key] = address.getField(key)
        self.pi.update_entity(controller='addresses', controller_path=f'{address.getId()}', params=params)

    ################################################

    def findSubnetsbyIPMask(self, base_ip:IPv4Address|IPv6Address, mask:int) -> list[ipamSubnet]:
        """Find one or more subnets defined by base_ip/mask at the phpIPAM service.
        :param base_ip: The base IP address of the subnet.
        :param mask: An integer with the prefix length of the subnet mask.
        :return: An array with ipamSubnet objects representing the subnets matching the search criteria."""
        base_addr = str(base_ip)
        try:
            return [ipamSubnet(s) for s in self.pi.get_entity(controller='subnets', controller_path=f'/search/{base_addr}/{str(mask)}')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    ################################################

    def findIPs(self, ip:IPv4Address|IPv6Address) -> list[ipamAddress]:
        """Find the IP addresses registered inside a subnet at the phpIPAM service matching a given IP address.
        In theory, only one address will be returned in the list.
        :param ip: An object representing an ip address.
        :return: An array with ipamAddress objects representing the addresses registered in this subnet matching the given IP address."""
        addr = str(ip)
        try:
            return [ipamAddress(addr=a) for a in self.pi.get_entity(controller='addresses', controller_path=f'/search/{addr}')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    def findIPsbyHostName(self, hostname:str) -> list[ipamAddress]:
        """Find the IP address registered inside a subnet at the phpIPAM service matching the given hostname.
        :param hostname: The hostname of the IP address to return.
        :return: An array with ipamAddress objects representing the addresses matching the hostname. If nothing is found, an empty list is returned."""
        try:
            return [ipamAddress(addr=a) for a in self.pi.get_entity(controller='addresses', controller_path=f'search_hostname/{hostname}')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    def findIPsbyNet(self, subnet:ipamSubnet) -> list[ipamAddress]:
        """Find all the IP addresses registered inside a subnet at the phpIPAM service.
        :param subnet: An object representing the subnet.
        :return: An array with ipamAddress objects representing the addresses registered in this subnet."""
        try:
            return [ipamAddress(addr=a) for a in self.pi.get_entity(controller='subnets', controller_path=f'{subnet.id}/addresses')] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []
    

    def findIPsbyField(self, subnet:ipamSubnet, field:str, pattern:str) -> list[ipamAddress]:
        """Find all the IP addresses registered inside a subnet whose value of 'field' matches the given pattern .
        :param subnet: An object representing the subnet.
        :param field: The name of the field to match.
        :param pattern: A regular expression defining a pattern for matching values.
        :return: An array with ipamAddress objects representing the addresses registered in this subnet matching the filter."""
        addresses = self.findIPsbyNet(subnet)
        try:
            return [a for a in addresses if re.match(pattern, a.getField(field,''))] # type: ignore
        except phpypam.PHPyPAMEntityNotFoundException as e:
            return []

    def _firstFit2(self, range:IPv4Network | IPv6Network, used_ips:list[IPv4Address | IPv6Address], num) -> list[IPv4Address | IPv6Address]:
        # List of contiguous addresses
        freePool:list[IPv4Address | IPv6Address] = []
        # Go through the IP range of the subnet
        for addr in range:
            if addr in used_ips:
                # If current address is used, reset our pool
                freePool = []
            else:
                # Add another contiguous address to the pool
                freePool.append(addr)
                # If there are enough addresses, return
                if len(freePool)>= num:
                    return freePool
        return []

    def _pools(self, netRange:IPv4Network | IPv6Network, used_ips:list[IPv4Address | IPv6Address]) -> list[tuple[IPv4Address | IPv6Address, int]]:
        # List of contiguous addresses
        pools = []
        startIP = None
        count = 0
        # Go through the IP range of the subnet
        for addr in netRange.hosts():
            if addr not in used_ips:
                if count > 0:
                    # If current pool not empty add it
                    count += 1
                else:
                    # If current address is used, reset our pool
                    startIP = addr
                    count = 1
            else:
                if count > 0:
                    # Add another pool to the list
                    pools.append((startIP,count))
                    count = 0
        if count > 0:
            # Add last pool to the list
            pools.append((startIP,count))
        return pools

    def _bestFit(self, netRange:IPv4Network | IPv6Network, used_ips:list[IPv4Address | IPv6Address], num) -> IPv4Address | IPv6Address | None:
        # Get all pools
        pools = self._pools(netRange, used_ips=used_ips)
        # Get suitable pools
        suitable = [(ip,l) for ip,l in pools if l>=num]
        if not suitable:
            # No pool has enough size
            return None
        
        # Get best pool
        best = np.min([l for ip,l in pools if l>=num])
        bestpool = [(ip,l) for ip,l in pools if l==best].pop()
        return bestpool[0]

    def _worstFit(self, netRange:IPv4Network | IPv6Network, used_ips:list[IPv4Address | IPv6Address], num) -> IPv4Address | IPv6Address | None:
        # Get all pools
        pools = self._pools(netRange, used_ips=used_ips)
        # Get suitable pools
        suitable = [(ip,l) for ip,l in pools if l>=num]
        if not suitable:
            # No pool has enough size
            return None
        
        # Get worst pool
        worst = np.max([l for ip,l in pools if l>=num])
        worstpool = [(ip,l) for ip,l in pools if l==worst].pop()
        return worstpool[0]

    def _firstFit(self, range:IPv4Network | IPv6Network, used_ips:list[IPv4Address | IPv6Address], num) -> IPv4Address | IPv6Address | None:
        # List of contiguous addresses
        startIP = None
        endIP = None
        # Go through the IP range of the subnet
        for addr in range:
            if addr in used_ips:
                # If current address is used, reset our pool
                startIP = None
                endIP = None
            else:
                if startIP:
                    # Add another contiguous address to the pool
                    endIP = addr
                else:
                    # Start a Pool
                    startIP = addr
                    endIP = addr
                # If there are enough addresses, return
                if startIP + num - 1 == addr:
                    return startIP
        return None

    def findFree(self, subnet:ipamSubnet, num:int, fitAlg:str = 'FirstFit') -> list[ipamAddress]:
        """Finds a block of exactly 'num' contiguous free IP addresses inside given subnet using the indicated optimization algorithm.
        This function does not reserve or lock the addresses. If there are concurrent clients, you must arbitrate clients so that
        no other client is given the same addresses before registration. Registration will fail if another client has registered
        the address before.

        :param subnet: The subnet in which the address is sought.
        :param num: The number of contiguous addresses to return.
        :param fitAlg: The name of the algorithm to use. Default is 'FirstFit'. 'WorstFit' and 'BestFit' are also available.
        :return: A list of contiguous free IP addresses. If not enough addresses are found, an empty list is returned."""
        used = self.findIPsbyNet(subnet)
        used_ips = [u.getIP() for u in used]
        netRange = subnet.getSubnet()
        match fitAlg:
            case 'FirstFit':
                startIP = self._firstFit(netRange, used_ips, num)
            case 'BestFit':
                startIP = self._bestFit(netRange, used_ips, num)
            case 'WorstFit':
                startIP = self._worstFit(netRange, used_ips, num)
        if startIP: # type: ignore
            return [ipamAddress(ip=startIP + offset, subnet=subnet) for offset in range(num) ]
        else:
            return []
        
    def registerIP(self, addr:ipamAddress) -> ipamAddress|None:
        """Register a free IP address at phpIPAM service. If the address has been registered before,
        registration will fail.
        :param addr: The IP address to register."""
        newAddr = self.pi.create_entity(controller='addresses', data=addr.getDictionary())
        if newAddr:
            return ipamAddress(newAddr)
        else:
            return None

    def unregisterIP(self, addr:ipamAddress, force:bool=False):
        """Release the registration of an IP address at the phpIPAM service.
        :param addr: The IP address to unregister."""
        if not force:
            # Block remove  for locked addresses
            if addr.getFieldInt('custom_apiblock') == 1 or addr.getFieldInt('custom_apinotremovable') == 1:
                raise PermissionError("API can't remove protected addresses")
            # Block remove  for special tags and routers
            if addr.getFieldInt('tag') > 2 or addr.getFieldInt('is_gateway') == 1:
                raise PermissionError("API can't remove addresses marked as special ones")

        self.pi.delete_entity(controller='addresses', controller_path=f'{addr.getId()}')
    
    def annotate_address(self, ipAddress:IPv4Address|IPv6Address, sn:ipamSubnet, description:str, tag:int=2, apiblock:int = 0, apinotremovable:int = 0, isrouter:int = 0, hostname:str='', cleanLastseen:bool=False, force:bool = False):
        # Get address
        baseaddresIpam = self.findIPs(ipAddress)
        # If exists update else create
        create = False
        if baseaddresIpam:
            ipobj=baseaddresIpam.pop()
        else:
            ipobj = ipamAddress(ip=ipAddress, subnet=sn)
            create = True

        # Set fields        
        try:
            ipobj.updateField('description',description, force=force)
            ipobj.updateField('state',tag, force=force)
            ipobj.updateField('custom_apiblock',apiblock, force=force)
            ipobj.updateField('custom_apinotremovable',apinotremovable, force=force)
            ipobj.updateField('is_gateway',isrouter, force=force)
            if hostname:
                ipobj.updateField('hostname',hostname, force=force)
            if cleanLastseen:
                ipobj.cleareLastSeen(force=True)

        except PermissionError as p:
            mylogger.error(f"Address {str(ipAddress)} has 'custom_apiblock' flag set and can't be updated.")
            return
        else:
            # Create or update address
            if create:
                self.registerIP(ipobj)
                mylogger.debug(f'Annotated new IP address: {ipobj.getDictionary()}')
            else:
                self.updateAddress(ipobj)
                mylogger.debug(f'Annotated existing IP address: {ipobj.getDictionary()}')

    # Annotate basic subnet addresses
    def annotate_subnet(self, sn:ipamSubnet, hasRouter:bool, routerPos:int=-2, routerHostname:str='', force:bool=False):
        if sn.isPool:
            # Annotate addresses
            subnet = sn.getSubnet()
            baseaddresIP = subnet[0]
            broadcastIP = subnet.broadcast_address
            routerIP = subnet[routerPos]
            # Get IPAM addresses
            self.annotate_address(ipAddress=baseaddresIP, sn=sn, description="NETWORK ADDRESS", tag=ipamTags.TAG_notusable, apiblock=0, apinotremovable=1, cleanLastseen=True, force=force)
            self.annotate_address(ipAddress=broadcastIP, sn=sn, description="BROADCAST ADDRESS", tag=ipamTags.TAG_notusable, apiblock=0, apinotremovable=1, cleanLastseen=True, force=force)
            if hasRouter:
                self.annotate_address(ipAddress=routerIP, sn=sn, description="DEFAULT ROUTER", tag=ipamTags.TAG_router, apiblock=0, apinotremovable=1, isrouter=1, hostname=routerHostname, force=force)

    # Get DNS address for subnet
    def dns_subnet(self, sn:ipamSubnet) -> list[IPv4Address|IPv6Address]:
        if sn.isPool:
            dnsId=sn._net.get('nameserverId',0)
            if dnsId != 0:
                # Get nameserver
                jsonres = self.pi.get_entity(controller='tools/nameservers', controller_path=f"/{dnsId}")
                if jsonres:
                    dnsDesc=jsonres.get('name',f'DNSServer subnet {sn.description}')
                    dnsIPs=jsonres.get('namesrv1','')
                    if dnsIPs:
                        dnsAddrs=[ip_address(ip) for ip in dnsIPs.split(';')]
                        return dnsAddrs
        return []


    def listSubnetPlain(self, sn:ipamSubnet) -> str:
        # Get VLAN data
        if sn.vlanId and sn.vlanId > 0:
            try:
                jsonres = self.pi.get_entity(controller='vlan', controller_path=f"/{sn.vlanId}")
                if jsonres:
                    vlanid = jsonres.get('number')
                else:
                    vlanid = ''
            except Exception as e:
                vlanid = ''
        else:
            vlanid = ''
            
        # Get other data from subnet
        description = sn.description
        routerIP = str(sn.getSubnet()[-2])
        ipRange = f"{sn.getBaseaddr()}/{sn.getMask()}"
        routerMask = sn.getMask()

        # Generate banner
        banner = "##################################################################################################\n"
        banner += f"# vlan: {vlanid:3} red: {ipRange:18} {description:61}#\n"
        banner += f"# router: {routerIP:18} mask {routerMask:21}                                          #\n"
        banner += "##################################################################################################\n"
        output = banner

        # Generate list  header
        #output += f"{'IP':^15} {'Hostname':^17} \t # Description # Notes\n"
        output += f"\n"

        # List hosts
        aList = self.findIPsbyNet(sn)
        for a in aList:
            description = a.getField('description')
            if not description or re.match(r".*autodiscover.*", description, flags=re.RegexFlag.IGNORECASE):
                description = ''
            else:
                description = f"# {description}"
            note = a.getField('note')
            if not note or re.match(r".*autodiscover.*", note, flags=re.RegexFlag.IGNORECASE):
                note = ''
            else:
                note = f"# {note}"
            output += f"{str(a.getIP()):15} {a.getField('hostname').split('.')[0]:17} {description} {note}\n" # type: ignore
        output += '\n\n'
        return output