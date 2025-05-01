#!/usr/bin/python3
"""This file provides management for wrapping a dictionary describing a phpIPAM VLAN with an object that adds functions to manage it."""

from datetime import datetime, timezone
from typing import Optional

class ipamVLAN:
    """This object wraps a JSON dictionary representing a phpIPAM VLAN either returned by phpypam or created to insert a new VLAN."""
    def __init__(self, vlan:dict) -> None:
        """Creates a new object. The object is initialized with a dictionary returned by phpypam.
        :param vlan: A JSON dictionary returned by phpypam.
        """
        if vlan:
            self._vlan:dict = vlan
        else:
            raise ValueError("Dictionary can't be None")

    def getId(self) -> int:
        return self._vlan.get('id', 0)
    
    def getName(self) -> str:
        return self._vlan.get('name', '')
    
    def getNumber(self) -> int:
        return self._vlan.get('number', 0)
    
    def getDescription(self) -> str:
        return self._vlan.get('description', '')
    
    def getDictionary(self) -> dict:
        return self._vlan

    def __str__(self) -> str:
        return f"VLAN {self.getNumber()} ({self.getName()}): {self.getDescription()}"
    

    