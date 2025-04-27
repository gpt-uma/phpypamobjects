#!/usr/bin/python3
"""This file provides management for wrapping a dictionary describing a phpIPAM Scan Agent with an object that adds functions to manage it."""

from datetime import datetime, timezone
from typing import Optional

class ipamScanAgent:
    """This object wraps a JSON dictionary representing a phpIPAM Scan Agent either returned by phpypam or created to insert a new IP address."""
    def __init__(self, agent:dict) -> None:
        """Creates a new object. The object is initialized with a dictionary returned by phpypam.
        :param agent: A JSON dictionary returned by phpypam.
        """
        if agent:
            self._agent:dict = agent
        else:
            raise ValueError('Both arguments are None.')

    def getId(self) -> int:
        return self._agent.get('id', 0)
    
    def getName(self) -> str:
        return self._agent.get('name', '')
    
    def getDescription(self) -> str:
        return self._agent.get('description', '')
    
    def getType(self) -> str:
        return self._agent.get('type', '')
    
    def getCode(self) -> str:
        return self._agent.get('code', '')
    
    def getLastAccess(self) -> Optional[datetime]:
        """Returns the last access date of the agent."""
        last = self._agent.get('last_access', '')
        if not last:
            return None
        ts = datetime.fromisoformat(last)
        if not ts.tzname():
            ts = ts.astimezone()
        return ts
    
    def getDictionary(self) -> dict:
        return self._agent

    def updateLastAccess(self) -> dict:
        """Updates the last access date of the agent."""
        self._agent['last_access'] = datetime.now().isoformat()
        return {'last_access': self._agent['last_access']}

    def __str__(self) -> str:
        return f"ScanAgent {self._agent['name']} ({self._agent['description']}): {self._agent['type']} ({self._agent['code']}) {self._agent['last_access']}"
    

    