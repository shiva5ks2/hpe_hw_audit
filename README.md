## Configuration Drift tool for HPE Hardware

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

### Prerequisites
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
### How to use the tool

#### Getting the current configuration - getEnclosure.py
Each directory (OA, VC, ProCurve and P2000) has a getEnclosure.py file. The command line is
the same for each.  It ssh'es into the corresponding component and gets the corresponding
configuration details that need to be compared.

```sh
usage: getEnclosure.py [-h] -i INPUTCSV [-o OUTDIR]
Arguments:
  -h, --help            show this help message and exit
  -i INPUTCSV, --inputcsv INPUTCSV
                        Input CSV that contains the OA login credentials. Format : <IP address>,<UserID>,<Password>
  -o OUTDIR, --outdir OUTDIR [OPTIONAL]
                        Output Directory in which the output files are generated
```

Before you start comparing the current configuration against the golden configuration,
you also need to know how to poulate the golden configuration templates. See the section -
How to get Golden configuration - for more information on this.

#### Compare the current configuration with golden configuration - diff*.py
Each directory contains a diff*.py file - OA/diffOA.py, P2000/diffP2K.py, ProCurve/diffPC.py, VC/diffVC.py.
Once getEnclosure.py gets the current configuration, the diff*.py script compares it with the "golden" configuration.

```sh
usage: diffOA.py [-h] -g GOLDEN (-i INFILE | -f FILELIST) [-o OUTPUT]

Arguments:
  -h, --help            show this help message and exit
  -g GOLDEN, --golden GOLDEN
                        OA file from golden configuration
  -i INFILE, --infile INFILE
                        OA file to compare with
  -f FILELIST, --filelist FILELIST
                        File that contains list of OA config file paths
  -o OUTPUT, --output OUTPUT
                        Output XLSX file in which the configuration differences are dumped
```

#### Master scripts - getAll and diffAll

If you don’t want to remember all these options, all you need to do is run getAll and diffAll.
All you need to populate are the CSV files which have the login credentials.

getAll - (takes no options) – assumes that you have populated the LoginCSVs directory with the
4 csv files - OA.csv, VC.csv, P2000.csv and ProCurve.csv. If that is done correctly, it will
try to access each IP/hostname given and get the config. data. It will populate that in a YYYY_MM_DD
directory.
Format of CSV : <IP address>,<UserID>,<Password> - each line will represent a device

diffAll - given a input configuration directory, look for any OA, VC, P2000 and ProCurve files and
compare it against the golden configuration.

```sh
usage: diffAll [-h] -c CONFIGDIR [-o OUTDIR]

Arguments:
    -c CONFIGDIR – input directory where all the configuration files are
    -o OUTDIR – place all the outputs XLSX in the specified directory. [OPTIONAL]. If this directory is not provided, then create the files in the current directory.
```
### How to get Golden configuration
For each of the following components, log on to the component and collect information
for the following commands. You can do that manually or you can also get the date from
the corresponding getEnclosure.py.
  - OA (OA/getEnclosure.py)
  - VC (VC/getEnclosure.py)
  - ProCurve (ProCurve/getEnclosure.py)
  - P2000 (P2000/getEnclosure.py)
 
#### Manual command for OA
```sh
show config
show firmware summary csv
```

#### Manual command for VC
```sh
show config
show firmware
```

#### Manual command for ProCurve
```sh
no page
show config
```

#### Manual command for P2000
```sh
set cli-parameters pager off json
show advanced-settings
show auto-write-through-trigger
show disk-parameters
show email-parameters
show isci-parameters
show job-parameters
show network-parameters
show protocols
show redundancy-mode
show snmp-parameters
show system-parameters
show users
versions
```
