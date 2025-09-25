#!/usr/bin/python3
"""
This file provides management for wrapping a dictionary describing a phpIPAM subnet with an object that adds functions to manage it.
"""

from datetime import datetime, timedelta
from email.policy import default
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network, ip_network, ip_address
from typing import Optional, Union, Dict, Any
from macaddress import MAC

class ipamSubnet:
    """This object wraps a JSON dictionary representing a phpIPAM IP subnet returned by phpypam."""
    def __init__(self, net:dict) -> None:
        """Creates a new object. The object is initialized with a dictionary returned by phpypam.
        :param addr: A JSON dictionary returned by phpypam."""
        self._net:Dict[str,Any] = net

    def getField(self, field:str, default:Any = None) -> Optional[Any]:
        """Get any field of the JSON object.
        :param field: The identifier of the field to return.
        :return: The value of the field."""        
        return self._net.get(field, default)
        
    def getFieldInt(self, field:str, default:int=0) -> int:
        """Get any field of the JSON object.
        :param field: The identifier of the field to return.
        :return: The value of the field."""        
        value = self._net.get(field,default)
        return value

    def getEditDate(self) -> Optional[datetime]:
        date = self._net.get('editDate','')
        if not date:
            return None
        ts = datetime.fromisoformat(date)
        # Set timezone
        ts = ts.astimezone()
        return ts

    def getLastRescan(self, interval:timedelta=timedelta(hours=1)) -> Optional[datetime]:
        date = self._net.get('lastScan','')
        if not date:
            return None
        ts = datetime.fromisoformat(date)
        # Set timezone
        ts = ts.astimezone()
        return ts

    def getLastDiscovery(self, interval:timedelta=timedelta(hours=1)) -> Optional[datetime]:
        date = self._net.get('lastDiscovery','')
        if not date:
            return None
        ts = datetime.fromisoformat(date)
        # Set timezone
        ts = ts.astimezone()
        return ts

    def getId(self) -> int:
        return self.getFieldInt('id')

    def getBaseaddr(self) -> Union[IPv4Address, IPv6Address, None]:
        return ip_address(self.getField('subnet')) if self.getField('subnet') else None  # type: ignore

    def getMask(self) -> int:
        return self.getFieldInt('mask',0)

    def getSubnet(self) -> Union[IPv4Network, IPv6Network]:
        """Returns an object representing the subnet range.
        :return: A IPv4|6Network object."""
        if self._net.get('subnet','') and self._net.get('mask',''):
            return ip_network(f"{self._net.get('subnet')}/{self._net.get('mask')}")
        else:
            raise Exception('ipamSubnet does not have a defined subnet')

    def getisPool(self) -> int:
        return self.getFieldInt('isPool',0)

    def getdiscoverSubnet(self) -> int:
        return self.getFieldInt('discoverSubnet',0)

    def getpingSubnet(self) -> int:
        return self.getFieldInt('pingSubnet',0)

    def getresolveDNS(self) -> int:
        return self.getFieldInt('resolveDNS',0)

    def getvlanId(self) -> int:
        return self.getFieldInt('vlanId')

    def getscanAgent(self) -> int:
        return self.getFieldInt('scanAgent')

    def getNameServerId(self) -> int:
        return self.getFieldInt('nameserverId')

    def getDescription(self) -> str:
        return self.getField('description','') # type: ignore

    def getBaseMAC(self) -> Optional[MAC]:
        mac = self.getField('custom_basemac','')
        if mac:
            try:
                return MAC(mac)
            except ValueError:
                raise Exception(f"Invalid MAC address {mac} in subnet {self}")
        return None
    
    def updateLastDiscovery(self) -> dict:
        """Updates the last discovery date of the agent."""
        self._net['lastDiscovery'] = datetime.now().isoformat()
        return {'lastDiscovery': self._net['lastDiscovery']}

    def updateLastScan(self) -> dict:
        """Updates the last scan date of the agent."""
        self._net['lastScan'] = datetime.now().isoformat()
        return {'lastScan': self._net['lastScan']}

    def __str__(self) -> str:
        return f"{self._net.get('subnet','?')}/{self._net.get('mask','?')} ({self._net['description']})"
    