from setuptools import setup, find_packages

setup(
    name="phpypamobjects",
    version="0.1",
    packages=find_packages(),
    description="A high level API client library for phpIPAM.  This library wraps the phpypam library with higher level objects representing phpIPAM abstractions like addresses, subnets and scan agents.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Guillermo Pérez Trabado",
    author_email="guille@ac.uma.es",
    url="https://www.ac.uma.es/~guille/phpypamobjects",
    install_requires=[
        #'ipaddress',
        #'re',
        'numpy>=2.00',
        #'typing',
        #'logging',
        #'sys',
        #'os',
        #'getpass',
        #'ssl',
        #'datetime'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
)
