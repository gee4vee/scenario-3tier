
# Implementation
## TLDR
```
cp template.local.env local.env
vi local.env
source local.env
```

- 000-prerequisites.sh
- 010-create.sh
- 800-test.sh - see notes below for pytest set up
- 900-cleanup.sh

## Description
The vpc_tf directory has a terraform implementation.  The 010-create.sh script initializes the directory and calls `terraform apply`.  The files in vpc_tf/:
- vpc.tf - vpc resources like subnets and instance a
- resources.tf - postgresql creation
- user_data.sh - script to create the systemctl service from a python3 program.  Note that the application example in the app/ directory is referenced

The files in the app/ are for a python application that returns json from the api:
- / - uname and ip address information dict(uname="vpc3tier-front-0", floatin_ip="52.118.144.159",private_ip="10.0.0.5")
- /increment - {"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":2} - same as / but add a count of the times this instance has been called.  When called on a front instance a "remote" key will contain the back values {"uname":"vpc3tier-front-0","floatin_ip":"52.118.144.159","private_ip":"10.0.0.5","count":10,"postgresql":"no postgresql configured","remote":{"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":21,"postgresql":{"count":3}}}
- /postgresql - same as increment but a counter will also be kept in the database of the total times the database is incremented.  Only the back instances are configured for postgresql

### Running the app/ on your desktop

- cd app
- verify you have a python3 environment with pip, that you are willing to install more packages
- pip install -r app/requirements.txt
- python3 main.py
- curl localhost:8000/
- curl localhost:8000/increment

Set environment variables to reference the postgresql - more instructions needed sorry