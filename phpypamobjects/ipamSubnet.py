#!/usr/bin/python3
"""This file provides management for wrapping a dictionary describing a phpIPAM subnet with an
object that adds functions to manage it."""

from datetime import datetime, timedelta, timezone
from typing import Any
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, ip_network, ip_address

class ipamSubnet:
    """This object wraps a JSON dictionary representing a phpIPAM IP subnet returned by phpypam."""
    def __init__(self, net:dict) -> None:
        """Creates a new object. The object is initialized with a dictionary returned by phpypam.
        :param addr: A JSON dictionary returned by phpypam."""
        self._net:dict = net
        self.id:int | None =  net.get('id')
        self.subnet:str | None =  net.get('subnet')
        self.mask:str | None =  net.get('mask')
        self.sectionId:int | None =  net.get('sectionId')
        self.description:str | None =  net.get('description')
        self.linked_subnet:int | None =  net.get('linked_subnet')
        self.firewallAddressObject:int | None =  net.get('firewallAddressObject')
        self.vrfId:int | None =  net.get('vrfId')
        self.masterSubnetId:int | None =  net.get('masterSubnetId')
        self.allowRequests:int | None =  net.get('allowRequests')
        self.vlanId:int | None =  net.get('vlanId')
        self.showName:int | None =  net.get('showName')
        self.device:int | None =  net.get('device')
        self.permissions:list | None =  net.get('permissions')
        self.pingSubnet:int | None =  net.get('pingSubnet')
        self.discoverSubnet:int | None =  net.get('discoverSubnet')
        self.resolveDNS:int | None =  net.get('resolveDNS')
        self.DNSrecursive:int | None =  net.get('DNSrecursive')
        self.DNSrecords:int | None =  net.get('DNSrecords')
        self.nameserverId:int | None =  net.get('nameserverId')
        self.scanAgent:int | None =  net.get('scanAgent')
        self.customer_id:int | None =  net.get('customer_id')
        self.isFolder:int | None =  net.get('isFolder')
        self.isFull:int | None =  net.get('isFull')
        self.isPool:int | None =  net.get('isPool')
        self.tag:int | None =  net.get('tag')
        self.threshold:int | None =  net.get('threshold')
        self.location:list | None =  net.get('location')
        if net.get('editDate'):
            ts= datetime.fromisoformat(self._net['editDate'])
            if not ts.tzname():
                ts = ts.astimezone()
            self.editDate:datetime|None = ts
        else:
            self.editDate:datetime|None = None
        if net.get('editDate'):
            ts= datetime.fromisoformat(self._net['editDate'])
            if not ts.tzname():
                ts = ts.astimezone()
            self.lastScan:datetime|None= ts
        else:
            self.lastScan:datetime|None = None
        if net.get('lastDiscovery'):
            ts= datetime.fromisoformat(self._net['lastDiscovery'])
            if not ts.tzname():
                ts = ts.astimezone()
            self.lastDiscovery:datetime|None= ts
        else:
            self.lastDiscovery:datetime|None = None

    def buildDictionary(self) -> dict:
        """Build a dictionary translating the fields of the object to dictionary format.
        :return: A dictionary representing a subnet in phpIPAM format."""
        self._net['id']=self.id
        self._net['subnet']=self.subnet
        self._net['mask']=self.mask
        self._net['sectionId']=self.sectionId
        self._net['description']=self.description
        self._net['linked_subnet']=self.linked_subnet
        self._net['firewallAddressObject']=self.firewallAddressObject
        self._net['vrfId']=self.vrfId
        self._net['masterSubnetId']=self.masterSubnetId
        self._net['allowRequests']=self.allowRequests
        self._net['vlanId']=self.vlanId
        self._net['showName']=self.showName
        self._net['device']=self.device
        self._net['permissions']=self.permissions
        self._net['pingSubnet']=self.pingSubnet
        self._net['discoverSubnet']=self.discoverSubnet
        self._net['resolveDNS']=self.resolveDNS
        self._net['DNSrecursive']=self.DNSrecursive
        self._net['DNSrecords']=self.DNSrecords
        self._net['nameserverId']=self.nameserverId
        self._net['scanAgent']=self.scanAgent
        self._net['customer_id']=self.customer_id
        self._net['isFolder']=self.isFolder
        self._net['isFull']=self.isFull
        self._net['isPool']=self.isPool
        self._net['tag']=self.tag
        self._net['threshold']=self.threshold
        self._net['location']=self.location

    def getEditData(self) -> datetime|None:
        if not self._net.get('editDate'):
            return None
        ts= datetime.fromisoformat(self._net['editDate'])
        # Set timezone if not in database field
        if not ts.tzname():
            ts = ts.astimezone()
        return ts

    def getLastRescan(self, interval:timedelta=timedelta(hours=1)) -> datetime:
        if not self._net.get('lastScan'):
            return datetime.now() - interval
        ts= datetime.fromisoformat(self._net['lastScan'])
        # Set timezone if not in database field
        if not ts.tzname():
            ts = ts.astimezone()
        return ts

    def getLastDiscovery(self, interval:timedelta=timedelta(hours=1)) -> datetime:
        if not self._net.get('lastDiscovery'):
            return datetime.now() - interval
        ts= datetime.fromisoformat(self._net['lastDiscovery'])
        # Set timezone if not in database field
        if not ts.tzname():
            ts = ts.astimezone()
        return ts

    def getId(self) -> int | None:
        return self._net.get('id')

    def getBaseaddr(self) -> IPv4Address|IPv6Address|None:
        return ip_address(str(self._net.get('subnet'))) if self._net.get('subnet') else None

    def getMask(self) -> int|None:
        return self._net.get('mask')

    def getDictionary(self) -> dict:
        return self._net

    def updateLastDiscovery(self) -> dict:
        """Updates the last discovery date of the agent."""
        self._net['lastDiscovery'] = datetime.now().isoformat()
        return {'lastDiscovery': self._net['lastDiscovery']}

    def updateLastScan(self) -> dict:
        """Updates the last scan date of the agent."""
        self._net['lastScan'] = datetime.now().isoformat()
        return {'lastScan': self._net['lastScan']}

    def getSubnet(self) -> IPv4Network | IPv6Network:
        """Returns an object representing the subnet range.
        :return: A IPv4|6Network object."""
        return ip_network(f"{self._net['subnet']}/{self._net['mask']}")

    def __str__(self) -> str:
        return f"{self._net['subnet']}/{self._net['mask']} ({self._net['description']})"