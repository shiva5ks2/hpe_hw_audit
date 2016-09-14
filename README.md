Configuration Drift tool for HPE Hardware

The Configuration Drift tool can be used as an audit tool to find out if the
current configuration of specific HP hardware is different from the ideal 
"golden" configuration.

The configuration information can be collected from:
- Operations Administrator of C7000 enclosure.
- Virtual Connect Manager
- P2000 stroage array
- ProCurve switch

### Version
1.2

# Prerequisites
To use the tools, please ensure that the following depenencies are met.
The tool can be run on most/all Unix platforms that provide the required python modules.

Prerequisites for using the tool:
  - python-devel - The libraries and header files needed for Python development
  - paramiko - Python (2.6+, 3.3+) implementation of the SSHv2 protocol
  - XlsxWriter - Python module for creating Excel XLSX files

Instructions for RHEL/Centos
```sh
yum install python-devel
pip install paramiko
pip install XlsxWriter
```

# Usage

