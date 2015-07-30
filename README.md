# ceilometer-janitor
Small script that does a cleanup of idle vms based on ceilometer stats.


* Install:

```
ubuntu@machine:~$ sudo pip install --upgrade ceilometer-janitor --force Downloading/unpacking ceilometer-janitor
  Downloading ceilometer-janitor-0.1.2.tar.gz
  Running setup.py (path:/tmp/pip_build_root/ceilometer-janitor/setup.py) egg_info for package ceilometer-janitor
    
Installing collected packages: ceilometer-janitor
  Found existing installation: ceilometer-janitor 0.1.2
    Uninstalling ceilometer-janitor:
      Successfully uninstalled ceilometer-janitor
  Running setup.py install for ceilometer-janitor
    
    Installing ceilometer-janitor script to /usr/local/bin Successfully installed ceilometer-janitor Cleaning up... 
```


* Options:

```
ubuntu@machine:~$ ceilometer-janitor --help 

Usage: ceilometer-janitor [options] Options:
  -h, --help show this help message and exit
  -d days, --days=days Days delta for instances
  -m METERS, --meters=METERS
                        Meters to check, i.e: 'cpu_util<=0.9'
  -e EXCLUDE_TENANTS, --exclude-tenants=EXCLUDE_TENANTS
  -s DISPATCH_REPORT, --send-report=DISPATCH_REPORT
  -w WHITELIST, --whitelist=WHITELIST
  -q QUIET, --quiet=QUIET
  -a ACTION, --action=ACTION 
```


* Usage:

```
ubuntu@machine:~$ ceilometer-janitor --action=stop --quiet=True -d 5 --exclude-tenants=niedbalski 

Looking for instances matching: cpu_util<=0.9 usage criteria ignoring the ones created over the last 5 days 

louis-bouchard,ntp-coredump,2015-07-27T16:14:14Z 
thkang0,juju-thkang0-machine-10,2015-07-27T16:14:25Z 
vtapia,vtapia-precise,2015-07-27T16:18:20Z 
petermatulis,pmatulis-juju-kvm,2015-07-28T17:05:35Z
```
