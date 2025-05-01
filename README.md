# PHPYPAMOBJECTS

A high level API client library for phpIPAM written in Python.

## Description
This library is a wrapper around the phpypam library, which is a Python client for the phpIPAM API. It provides a higher-level interface to interact with phpIPAM, making it easier to work with IP address management tasks.
The library is designed to simplify the process of managing IP addresses, subnets, and other related tasks in phpIPAM. It provides a set of classes and methods that abstract away the complexities of the underlying API, allowing developers to focus on their specific use cases.
The library includes features such as:
- Simplified connection to a phpIPAM service.
- Simplified methods for creating, retrieving, and updating IP addresses, subnets and other objects from phpIPAM.
- Simple object-oriented interface with methods for common tasks on IP addresses and subnets.
- Support for retrieval of IP addresses and networks from phpIPAM service, such as searching by IP address, subnet, hostname or subnet address range.
- Support for IPv4 and IPv6 addresses.
- Handling and logging of errors and exceptions.
- Support for timestamping of changes for subnets and addresses.
- Support for allocation of free IP addresses from subnets selecting algorithms managing fragmentation of ranges of free addresses (best-fit, first-fit, and worst-fit).
- Implements some form of protection against the scanning agent updating or deleting some special addresses (base address, broadcast address, router address) in subnets.

## Requirements
- Python 3.9 or higher (it uses python typing)
- phpypam library
- python-nmap library
- nmap tool installed in the system

## Installation

This library is distributed as a Python package and can be installed using pip. By now it is not available in PyPi, but you can download and install it or specify the URL of the package in git repository.

```bash
pip install phpypamobjects-<version>.tar.gz
```

Remember to make the changes to the SQL schema needed by this library and by the scan agent. Changes include some additional `custom fields` for the ipaddresses table, and some additional ipTags used to mark addresses.

To apply those changes to your database, look for the `sql` directory in this project and execute the SQL script(s) in there on your phpIPAM MySQL database.

# Usage

This library is designed to be used in a Python client application that needs to interact with a phpIPAM service. It provides a set of classes and methods that allow you to perform various operations on IP addresses, subnets, and other related objects in phpIPAM.

The constructors of the classes in this library and methods operating on the phpIPAM service raise exceptions when the phpIPAM service returns an error. Functions also use the default Logger provided by the logging module in Python. You can configure the logging level and format according to your needs to control the verbosity of the output of the library

## Connecting to phpIPAM service

To use the library, you need to create an instance of the `ipamServer` class, which represents a connection to a phpIPAM service. You can then use this instance to perform various operations on IP addresses, subnets and other objects in phpIPAM.

The `ipamServer` class constructor takes the following parameters:
- `url`: The URL of the phpIPAM service (e.g. `https://myphpipam.example.com`)
- `app_id`: The application ID of the phpIPAM service (e.g. `myipamclient`)
- `token`: The token of the phpIPAM service (e.g. `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
- `user`: The user of the phpIPAM service (e.g. `myipamuser`)
- `password`: The password of the phpIPAM service (e.g. `pppppppppppppppppp`)
- `cacert`: The path to the CA certificate file in PEM format (e.g. `/path/to/cacert.pem`)

After calling the constructor, the library will attempt to connect to the phpIPAM service using the provided parameters. If the connection fails, an exception will be raised. You can handle this exception to provide appropriate error handling in your application.

## Operating on the phpIPAM service data (ipamService class)

If successful, you can use the methods of the `ipamServer` class to find subnets, IP addresses, and other objects in phpIPAM. Each object returned by the library is an instance of a specific class that represents the corresponding object in phpIPAM and can be modified. Modifications to the object do not alter the object in phpIPAM. To persist the changes in the phpIPAM service, you need to call the appropriate method of the `ipamServer` class.

### Finding objects

The methods for listing or searching objects in phpIPAM return lists of objects. You can use these lists to iterate over the objects and perform operations on them. Be carefull with the number of objects returned by the methods, as some methods can return a large number of objects. You can use search methods to reduce the number of objects returned by the methods.

Methods for listing objects in phpIPAM include:
- `getAllSections()`: Returns a list of all sections in the phpIPAM service.
- `getAllSubnets()`: Returns a list of all subnets in the phpIPAM service.
- `getAllAddresses()`: Returns a list of all IP addresses in the phpIPAM service.
- `getAllVLANs()`: Returns a list of all VLANs in the phpIPAM service.
- `getAllScanAgents()`: Returns a list of all scanning agents in the phpIPAM service.

Methods for searching objects in phpIPAM include:
- `findSubnetsbyIPMask(baseaddress, mask)`: Returns a list of subnets that match the given base address and mask. Formally, it should return only one subnet, but in phpIPAM it can return a supernet and a subnet with the same base address and mask.
- `findVLANbyId(id)`: Returns a list of VLANs containing the one identified by the given id (this is the `DB id`, **not** the `802.1Q tag`).
- `findIPs(ip)`: Returns a list of IP addresses that match the given IP address. The IP address can be a IPv4 or IPv6 address. The method returns a list of IP addresses that match the given IP address. Again, it should return only one IP address, but it returns a list for consistency with the result of the other methods.
- `findIPsbyNet(subnet)`: Returns a list of IP addresses that belong to the given subnet.
- `findIPsbyHostName(hostname)`: Returns a list of IP addresses that have exactly the given hostname. As a host may have multiple IP addresses, this method returns a list of IP addresses.
- `findIPsbyField(subnet, field, pattern)`: Returns a list of IP addresses that match the given regular expression pattern in the given field. The field can be any field of the phpIPAM address object, including custom fields.

### Allocating free IP addresses and deallocating (removing) them
The library provides methods for allocating free IP addresses from subnets. The returned addresses are not registered as used in phpIPAM. You need to call the `registerIP` method to register the IP address as used.
There is not locking mechanism in the library to prevent multiple clients from allocating the same IP address at the same time. However, registering the address as used in phpIPAM will prevent other clients from simultaneously registering the same address as used.

The allocation of free addresses can be done using different algorithms that treat fragmentation of the free address space of the subnet in different ways. The algorithms are:
- `FirstFit`: Allocates the first fit for the requested number of addresses. This algorithm tries to find the first range of free addresses that can accommodate the requested number of addresses. This is the default algorithm as it is the fastest and produces a pseudo-random fragmentation which result in a low average fragmentation of the free address space. If you always allocate IP addresses individually, this is the best choice.
- `BestFit`: Allocates the best fit for the requested number of addresses. This algorithm tries to find the smallest range of free addresses that can accommodate the requested number of addresses. This algorithm produces the smaller residual block of free addresses, but it can produce more fragmentation in the free address space if you usually allocate IPs in groups.
- `WorstFit`: Allocates the worst fit for the requested number of addresses. This algorithm tries to find the largest range of free addresses that can accommodate the requested number of addresses. This algorithm produces the larger residual block of free addresses, but it can increase fragmentation if you need large blocks of free addresses in the future.

The library provides the following methods for allocating free IP addresses:
- `findFree(subnet, num, fitAlg)`: Returns a list of `num` free IP addresses from the given subnet using the specified allocation algorithm. The `fitAlg` parameter can be one of the following values: `FirstFit`, `BestFit`, or `WorstFit`. The default value is `FirstFit`. The returned addresses are not registered as used in phpIPAM. You need to call the `registerIP` method to register the IP address as used.
- `registerIP(ip)`: Registers the given IP address as used in phpIPAM. The IP address must be an instance of the `ipamAddress` class. This method will create a new address in phpIPAM if the address does not exist yet. If the address already exists, it will raise an exception. You can additional fields of the ipamAddress object before calling this method to set the description, hostname, MAC address, and other fields of the address. You should *not* fill the `id` nor the `subnet` fields of the address, as they are set automatically by the phpIPAM service.
- `unregisterIP(ip)`: Removes the given IP address in phpIPAM adding it to the list of free addresses of the subnet. The IP address must be an instance of the `ipamAddress` class. This method will delete the address from phpIPAM if it is not protected against removal. Addresses are protected when any of the following conditions are met:
  * The custom field `custom_apiblock` exists and it is 1 for this address.
  * The custom field `custom_apinotremovable` exists and it is 1 for this address.
  * The field `is_gateway` is set to 1 for this address.
  * The field `tag` is different from offline or used for this address (only addresses tagged as **offline** or **used** can be deleted).

### Updating objects

The following methods are used to update objects in phpIPAM service:
- `updateAddress(ip)`: Updates an existing IP address in phpIPAM service. The IP address must be an instance of the `ipamAddress` class. You must **always** update the fields of the address using the `updateField` method before calling this method, as only the fields that have been modified through that method will be updated in phpIPAM.
- `updateSubnetLastScan(subnet)`: Updates the `lastScan` field of the given subnet in phpIPAM service to the current date and time. This method is used by address scannning agents to update the last scan time of the subnet. The subnet must be an instance of the `ipamSubnet` class.
- `updateSubnetLastDiscovery(subnet)`: Updates the `lastDiscovery` field of the given subnet in phpIPAM service to the current date and time. This method is used by address scannning agents to update the last discovery time of the subnet. The subnet must be an instance of the `ipamSubnet` class.
- `updateScanAgent(agent)`: Updates the `lastAccess` field of the given scanning agent in phpIPAM service to the current date and time. This method is used by address scannning agents to update the last access time every time that thay connect to the phpIPAM service. The agent must be an instance of the `ipamScanAgent` class.

Remember that there are some special conditions that prevent updating addresses. When any condition prevents against update, an exception is raised by the method updating a field of an address, as the verification is done in the client library. The conditions preventing modification are listed at the end of the previous section.

### Miscellaneous methods

The library provides some additional methods for performing miscellaneous tasks in phpIPAM:
- `annotate_subnet(subnet, hasRouter, routerPos, routerHostname, force)`: This function registers and annotates as `not usable` the base and broadcast addresses of the given subnet. Optionally, it can also register and annotate as `not usable` the addresss of the default router of the subnet if given and annotate it with the given hostname. The `hasRouter` parameter indicates if the subnet has a router address while the `routerPos` parameter indicates the position of the router address in the subnet (1 for the first address after the base address, and -2 for the last address before the broadcast address). The `routerHostname` parameter is the hostname of the router address. The `force` parameter indicates if the function should force the registration of the addresses even if they are already registered as used. Addresses are also marked with the `custom_apinotremovable` custom field set to 1 to protect them against further updating of these addresses by scanning agents. The subnet must be an instance of the `ipamSubnet` class. 

  This function helps in protecting the base, broadcast and router addresses of a subnet againts being allocated, updated or deleted by any API client.

- `annotate_address(address, subnet, description, tag, apiblock, apinotremovable, isrouter, hostname, cleanLastSeen, force)`: This function annotates the given address with the given parameters. This function is used by `annotate_subnet` to protect each address, but it can also be used to annotate any address that need special protection.
  - Besides common fields, the `tag` parameter can set specially reserved tags in phpIPAM.
  - The `apiblock` field is a custom field that indicates that the address is protected against being manager through this library. As the protection is checked by the client library, the address can not be protected agains being updated or deleted by API clients that do not use this library or agains the phpIPAM web interface.
  - The `apinotremovable` field is a custom field that indicates that the address is protected against being deleted by any API client using this library.
  - The `isrouter` field indicates that the address is the router of the subnet. Only one address in the subnet can be marked as router.
  - The cleanLastSeen parameter indicates if the last seen timestamp of the address should be cleaned. This is useful when you want the address to appear as **never seen before**.
  - The force parameter indicates if the function should force the modification even if the address is protected agains modification through this library. This is useful when you want to reset the protection of the address.

-`dns_subnet(subnet)`: This function return a list with the addresses of the DNS servers of the given subnet.


## Operating on subnets (ipamSubnet class)

The methods of this class only operate on the object itself and not on the phpIPAM service. The methods of the `ipamServer` class are used to persist the changes in the phpIPAM service.

The methods of this class are:
  - `getId()`: Returns the numeric ID of the subnet which is used to reference the subnet in ipamAddress objects. It is seldom used directly as this library uses objects and not IDs as arguments.
  - `getSubnet()`: Returns the definition of the subnet as `IPv4Network` or `IPv6Network` objects.
  - `getBaseaddr()`: Returns the base IP address of the subnet.
  - `getMask()`: Returns the mask of the subnet as the length of the prefix in bits.
  - `getEditDate()`: Returns the date of the last modification of the subnet in the phpIPAM service.
  - `getLastRescan(inteval)`: Returns the date of the last rescan of the subnet by a scanning agent. The interval is the default age that is returned if the subnet has never been rescanned before.
  - `getLastDiscovery(interval)`: Returns the date of the last discovery of the subnet by a scanning agent. The interval is the default age that is returned if the subnet has never been discovered before.
  - `updateLastScan()`: Updates the last scan date of the subnet to the current date and time. This method is used by scanning agents to update the last scan date of the subnet.
  - `updateLastDiscovery()`: Updates the last discovery date of the subnet to the current date and time. This method is used by scanning agents to update the last discovery date of the subnet.

## Operating on addresses (ipamAddress class)

The methods of this class only operate on the object itself and not on the phpIPAM service. The methods of the `ipamServer` class are used to persist the changes in the phpIPAM service.
The methods of this class are:
  - `getId()`: Returns the numeric ID of the address which is used to reference the address in phpIPAM. It is seldom used directly as this library uses objects and not IDs as arguments.
  - `getIP()`: Returns the IP address of the address as `IPv4Address` or `IPv6Address` objects.
  - `setIP()`: Sets the IP address of the address from `IPv4Address` or `IPv6Address` objects. However, this can only be done for new addresses that have not been registered yet. The IP address of existing addresses can not be changed.
  - `getSubnetId()`: Returns the numeric ID of the subnet to which the address belongs.
  - `setSubnetId()`: Sets the numeric ID of the subnet to which the address belongs. This can only be done for new addresses that have not been registered yet. The subnet ID of existing addresses can not be changed.
  - `getHostname()`: Returns the hostname of the address.
  - `getDescription()`: Returns the description of the address.
  - `getNote()`: Returns the note field of the address.
  - `getLastSeen()`: Returns the date of the last seen of the address. If the address has never been seen before it returns a None value.
  - `getField(field, default)`: Returns the value of the given field of the address. The field can be any field of the phpIPAM address object, including custom fields. The field name must be exactly as it is defined in phpIPAM database. If the field does not exist, it returns the default value. The default value is None if not specified.
  - `getFieldInt(field, default)`: This function is similar to `getField`, but it returns the value of the field as an integer. If the field does not exist, it returns the default value. The default value is None if not specified.
  - `updateField(field, value)`: Updates a field of the address with a new value. The field can be any field of the phpIPAM address object, including custom fields. The field name must be exactly as it is defined in phpIPAM database. This method checks if the address is protected against modification before updating the field. If the address is protected, it raises an exception. The fields updated by scan agents are exceptions as they are not protected against modification in special addresses.
  - `updateLastSeen()`: Updates the last seen date of the address to the current date and time. This method is used by scanning agents to update the last seen date of the address.
  - `clearLastSeen()`: Clears the last seen date of the address. This method is used by scanning agents to clear the last seen date of the address. It is used when it is desired to reset the last seen date of the address to None. 
  - `updateMac(mac)`: Updates the MAC address of the address.
  - `format_simple()`: Returns a text printable representation of the address with some details for listing.

## Operating on scan agents (ipamScanAgent class)

The methods of this class only operate on the object itself and not on the phpIPAM service. The methods of the `ipamServer` class are used to persist the changes in the phpIPAM service.
The methods of this class are:
  - `getId()`: Returns the numeric ID of the scanning agent which is used to reference the agent in ipamAddress objects. It is seldom used directly.
  - `getName()`: Returns the name of the scanning agent. It has only descriptive purposes and is not used to identify the agent in the phpIPAM service.
  - `getDescription()`: Returns the description of the scanning agent. Only for descriptive purposes.
  - `getType()`: Returns the type of the scanning agent. Currently it is not used in the library as the web interface of phpIPAM does not allow to set any value different from **mysql**.
  - `getCode()`: Returns the code of the scanning agent. This is the code used by a library client to retrieve its scan agent identity. However, it is not used for any authorization purposes by the phpIPAM service.
  - `getLastAccess()`: Returns the date of the last access of the scanning agent. If the agent has never been accessed before, it returns a None value.
  - `updateLastAccess()`: Updates the last access date of the scanning agent to the current date and time. This method is used by scanning agents to update the last access date of the agent.

## Operating on VLANs (ipamVLAN class)

The methods of this class only operate on the object itself and not on the phpIPAM service. The methods of the `ipamServer` class (if any) are used to persist the changes in the phpIPAM service.
The methods of this class are:
  - `getId()`: Returns the numeric ID of the VLAN which is used to reference the agent in ipamSubnet objects. It is seldom used directly.
  - `getName()`: Returns the name of the vlan. It has only descriptive purposes and is not used to identify the VLAN in the phpIPAM service.
  - `getDescription()`: Returns the description of the VLAN. Only for descriptive purposes.
  - `getNumber()`: Returns the numeric tag (802.1Q tag) of the VLAN.

## Environment variables

The parameters of the connection to the phpIPAM service can be configured using environment variables:
* There are not default values for the connection parameters.
* If an argument of the ipamServer constructor is provided, it will override the value provided by the environment variable.
* If neither the constructor parameter nor the environment variable are provided, no default value will be used and an exception will be raised.

The list of environment variables used is:
* `MYIPAM_URL`: URL of the phpIPAM service (e.g. `https://myphpipam.example.com`)
* `MYIPAM_APP_ID`: Application ID of the phpIPAM service (e.g. `myipamclient`)
* `MYIPAM_TOKEN`: Token of the phpIPAM service (e.g. `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
* `MYIPAM_USER`: User of the phpIPAM service (e.g. `myipamuser`)
* `MYIPAM_PASSWORD`: Password of the phpIPAM service (e.g. `pppppppppppppppppp`)

## Code examples

### Connecting to phpIPAM service

This fragment show how to connect to the phpIPAM service: 
```python

from phpypamobjects import ipamServer
# This is not needed, but maybe you want to do IP address manipulation
from ipaddress import ip_address, IPv4Address, IPv6Address
# Just for pattern matching names in the example
import re

# Connect the service
ipam = ipamServer(
    url='https://myphpipam.example.com',
    app_id='myipamclient',
    token='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
    user='myipamuser',
    password='ppppppppppppppppppppp'
)
```

### Finding subnets and IP addresses and modifying them

This fragment show how to use the library to find all existing subnets and iterate on them. For each subnet, it finds all IP addresses in the subnet and modifies selected fields (MAC, description and last seen timestamp) for addresses whose description starts with the string 'test'.

```python
# Get all subnets
subnets=ipam.getAllSubnets()
for sn in subnets:
    # Print subnet description
    print(f'{sn} -- last scanned at: {sn.getLastRescan()} -- last discovered at: {sn.getLastDiscovery()}')
    # Reserve and annotate unusable IPs of this subnet (baseaddress, broadcast, router)
    ipam.annotate_subnet(sn, hasRouter=True, force=True)
    # Find all IPs of this subnet
    aList = ipam.findIPsbyNet(sn)
    
    # Print all IPs of this subnet
    for a in aList:
        # Print IP address description
        print(a)
        # Match some content in the IP description
        if re.match("test.*", a.getDescription()):
            # Modify some fields of the IP
            a.updateMac('00:00:00:00:00:00')
            a.setDescription('test-update')
            a.updateLastSeen()
            # Update address at the phpIPAM service
            ipam.updateAddress(a)

            # Use the ip address for anything else
            call_some_function(str(ip.getIP()))

            # Some fancy operations using ipaddress library
            if ip.getIP() in sn.getSubnet():
                print(f'{ip} is in {sn}')
            else:
                print(f'{ip} is NOT in {sn}')
```

### Allocating free IP addresses

This fragment show how to find free IP addresses in a subnet and register them as used. The example uses the best-fit algorithm to find 11 free IP addresses in each subnet.

```python
for sn in subnets:
    # Get a list of 11 free addresses from this subnet using the best-fit algorithm
    free_ips = ipam.getFreeIP(sn, 11, fitAlg='BestFit')
    # Register returned addresses as used
    for ip in free_ips:
        ip.setDescription('test-free')
        ip.setHostname('test-new-host')
        # Register the IP address as used
        ipam.registerIP(ip)

```

### Python comprehensions
Python comprension can be used or even abused to make more compact code:

```python
# Get only /24 subnets
subnets=[sn for sn in ipam.getAllSubnets() if sn.getMask() == '24']

# Get addresses from those subnets matching a pattern in the description
aList = [a for sn in subnets for a in ipam.findIPsbyNet(sn) if re.match(r"test.*", a.getDescription())]

# Get all subnets scanned by a Scanning Agent named 'agent1'
agent = [agent for agent in ipam.getAllScanAgents() if agent.getDescription() == 'agent1'].pop()
scannedSubnets = [sn for sn in ipam.getAllSubnets() if sn.scanAgent == agent.getId()]
for sn in scannedSubnets:
    # Print subnet description
    print(f'{sn} -- last scanned at: {sn.getLastRescan()} -- last discovered at: {sn.getLastDiscovery()}')

```    

# License
This project is released under the GPL v3 License - see the [LICENSE] file for details.

# Contact
Guillermo Pérez Trabado, University of Málaga, Spain.

For any questions or issues, please contact the author at [guille@ac.uma.es](mailto:guille@ac.uma.es).
