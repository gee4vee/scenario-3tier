#!/bin/bash

set -x

# parameters via substitution in the form __a__ done in terraform, look for all occurrances
# FRONT_BACK values of FRONT or BACK indicating the type of instance
# REMOTE_URL instances can reach out to a remote if provided
# MAIN_PY contents of the main.py python program
# POSTGRESQL_CREDENTIALS contents of the postgresql credentials

# ubuntu has a /root directory

cat > /root/postgresql.json << '__EOF__'
__POSTGRESQL_CREDENTIALS__
__EOF__

cat > /root/main.py << 'EOF'
__MAIN_PY__
EOF

cat > /root/postgresql.py << 'EOF'
__POSTGRESQL_PY__
EOF

# fix apt install it is prompting: Restart services during package upgrades without asking? <Yes><No>
export DEBIAN_FRONTEND=noninteractive

while ! ping -c 2 pypi.python.org; do
  sleep 1
done
apt update -y
apt install python3-pip -y
pip3 install --upgrade pip
pip3 install fastapi uvicorn psycopg2-binary

cat > /etc/systemd/system/threetier.service  << 'EOF'
[Service]
Environment="FRONT_BACK=__FRONT_BACK__"
Environment="REMOTE_URL=__REMOTE_URL__"
ExecStart=/usr/bin/python3 /root/main.py
EOF

systemctl start threetier
