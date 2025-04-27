#!/usr/bin/python3
"""This file provides management for wrapping a dictionary describing a phpIPAM IPaddress with an object that adds functions to manage it."""

from .ipamSubnet import ipamSubnet

from ipaddress import IPv4Address, IPv6Address, ip_address
from datetime import datetime
from typing import Optional, Union, Any

class ipamTags:
    TAG_offline = 1
    TAG_used = 2
    TAG_reserved = 3
    TAG_DHCP = 4
    TAG_staticDHCP = 5
    TAG_staticIP = 6
    TAG_router = 7
    TAG_notusable = 8

class ipamAddress:
    """This object wraps a JSON dictionary representing a phpIPAM IP address either returned by phpypam or created to insert a new IP address."""
    def __init__(self, addr:dict = None, ip:Union[IPv4Address, IPv6Address] = None, subnet:ipamSubnet = None) -> None: # type: ignore
        """Creates a new object. The object is initialized either with a dictionary returned by phpypam or with an IP and subnet identifier.
        :param addr: A JSON dictionary returned by phpypam.
        :param ip: An IP address.
        :param subnet: An ipamSubnet object representing a phpIPAM subnet object."""
        self._updated = set()
        if addr:
            self._addr:dict = addr
        elif ip:
            self._addr:dict = {'ip': str(ip)}
            if subnet:
                self._addr['subnetId']=subnet.id
        else:
            raise ValueError('Both arguments are None.')

    def getId(self) -> Optional[int]:
        return self._addr.get('id')
    
    def getIP(self) -> Union[IPv4Address, IPv6Address]:
        return ip_address(self._addr.get('ip')) # type: ignore
    
    def setIP(self, ip:IPv4Address):
        self._addr['ip'] = str(ip)
    
    def getSubnetId(self) -> Optional[int]:
        return self._addr.get('subnetId')
    
    def setSubnetId(self, subnetid):
        self._addr['subnetId'] = subnetid
    
    def getDictionary(self) -> dict:
        return self._addr

    def getHostname(self) -> str:
        value = self.getField('hostname')
        return value if value else ''

    def getDescription(self) -> str:
        value = self.getField('description')
        return value if value else ''

    def getNote(self) -> str:
        value = self.getField('note')
        return value if value else ''

    def getLastSeen(self) -> Optional[datetime]:
        value = self.getField('lastSeen','')
        if value:
            ts = datetime.fromisoformat(value)
            if not ts.tzname():
                ts = ts.astimezone()
            return ts
        else:
            return None

    def getField(self, field:str, default:Any = None) -> Optional[Any]:
        """Get any field of the JSON object.
        :param field: The identifier of the field to return.
        :return: The value of the field."""        
        return self._addr.get(field, default)
        
    def getFieldInt(self, field:str, default:int=0) -> int:
        """Get any field of the JSON object.
        :param field: The identifier of the field to return.
        :return: The value of the field."""        
        value = self._addr.get(field,default)
        return value

    def updateField(self, field:str, value:Any, force:bool=False):
        """Set any field of the JSON object.
        :param field: The identifier of the field to return.
        :param force: Force update ignoring protection rules.
        :return: The value of the field."""        

        if not force:
            # Filter avoid updating fields if address is blocked for api
            if self.getFieldInt('custom_apiblock') == 1:
                raise PermissionError(f"Address {self._addr.get('ip')} has apiblock=true: can't update field {field}")
            # Block fields edition for special tags and routers
            if (self.getFieldInt('tag') >= ipamTags.TAG_reserved or self.getFieldInt('is_gateway') == 1 ) and (field != 'lastSeen' and field != 'custom_tcpports' and field != 'mac'):
                raise PermissionError(f"Address {self._addr.get('ip')} has type >=2(RESERVED) or isgateway: can't update field {field}")

        if self._addr.get(field) != value:
            self._addr[field] = value
            self._updated.add(field)

    def updateLastSeen(self, force=False):
        """Updates the last date in which it answered a ping."""
        if self.getFieldInt('excludePing') == 0:
            self.updateField('lastSeen', datetime.now().isoformat(), force=force)

    def cleareLastSeen(self, force=False):
        """Updates the last date in which it answered a ping."""
        if self.getFieldInt('excludePing') == 0:
            self.updateField('lastSeen', '', force=force)

    def updateMac(self, mac:str, force=False):
        """Updates the mac."""
        self.updateField('mac', mac, force=force)

    def __str__(self) -> str:
        return str(self.getIP())
    
    def format_simple(self, printDomain:bool = False):
        print(f"{str(self.getIP()):15} {self.getHostname().split('.')[0]:17} # {self.getDescription()} # {self.getNote()}")
