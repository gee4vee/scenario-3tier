#!/usr/bin/env python3

import urllib.request
from typing import Optional
from fastapi import FastAPI
import uvicorn
import logging
import functools
import socket
import platform
import os
import json
from  pathlib import Path
import postgresql
import base64


def initialize():
  logging.basicConfig(level=logging.INFO)
  logging.info("starting")

class Cached2:
  """read and cache these properties"""
  def read_log_environment(self, environment_variable, log_contents=True, warn_not_found=False):
    """read an environment variable.  Log that it was read"""
    if environment_variable in os.environ:
      ret = os.environ[environment_variable]
      logging.info(f'{environment_variable} found in environment.  Value is {ret if log_contents else "hidden"}')
    else:
      if warn_not_found:
        logging.warn(f"environment variable {environment_variable} not in environment")
      else:
        logging.info(f"environment variable {environment_variable} not in environment")
      ret = None
    return ret

  @property
  @functools.lru_cache()
  def external_ip(self):
    """fip"""
    logging.info("external_ip check")
    try:
      ret = urllib.request.urlopen('https://ident.me', data=None, timeout=1).read().decode('utf8')
    except Exception as e:
      logging.warning(e)
      ret = "unknown"
    return ret

  @property
  @functools.lru_cache()
  def private_ip(self):
    """10.x"""
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      s.connect(("8.8.8.8", 80))
      ret = s.getsockname()[0]
      s.close()
    except Exception as e:
      logging.warn(e)
      ret = "unkown"
    return ret

  @property
  @functools.lru_cache()
  def name(self):
    try:
      return platform.uname().node
    except Exception as e:
      logging.warn(e)
      ret = "unkown"
    return ret

  @property
  @functools.lru_cache()
  def remote_url(self):
    return self.read_log_environment("REMOTE_URL")

  @property
  @functools.lru_cache()
  def front_back(self):
    """Expecting front or back"""
    return self.read_log_environment("FRONT_BACK", log_contents=True, warn_not_found=True)

  @property
  @functools.lru_cache()
  def front(self):
    return self.front_back == "front"

  @property
  @functools.lru_cache()
  def back(self):
    return self.front_back == "back"

  @property
  @functools.lru_cache()
  def python_directory(self):
    return Path(__file__).parent

  @property
  @functools.lru_cache()
  def postgresql_credentials(self):
    """the postgresql credentials json file is from the terraform ibm_resource_key for the postgresql database"""
    ret = None
    postgresql_credentials_s = (self.python_directory / "postgresql.json").read_text()
    if postgresql_credentials_s.strip() == f'__{"POSTGRESQL_CREDENTIALS"}__':
      logging.info("no postgresql credentials")
    else:
      logging.info("loading postgresql credentials")
      ret = json.loads(postgresql_credentials_s)
    return ret

  def read_log_postgresql(self, key, log_contents=True):
    """read a key from the postgresql credentials.  Log it"""
    if key in self.postgresql_credentials:
      ret = self.postgresql_credentials[key]
      logging.info(f'{key} found in postgresql.json.  Value is {ret if log_contents else "hidden"}')
    else:
      logging.warn(f"key {key} not in postgresql.json")
      ret = None
    return ret

  @property
  @functools.lru_cache()
  def postgresql_host(self):
    return self.read_log_postgresql("connection.postgres.hosts.0.hostname")

  @property
  @functools.lru_cache()
  def postgresql_port(self):
    return self.read_log_postgresql("connection.postgres.hosts.0.port")

  @property
  @functools.lru_cache()
  def postgresql_user(self):
    return self.read_log_postgresql("connection.postgres.authentication.username")

  @property
  @functools.lru_cache()
  def postgresql_password(self):
    return self.read_log_postgresql("connection.cli.environment.PGPASSWORD", log_contents=False)

  @property
  @functools.lru_cache()
  def postgresql_certificate_file(self):
    certificate_path = self.python_directory / "cert"
    if not certificate_path.exists():
      base64_s = self.read_log_postgresql("connection.postgres.certificate.certificate_base64")
      certificate_s = base64.b64decode(base64_s)
      certificate_path.write_bytes(certificate_s)
    return str(certificate_path.resolve())

class G:
  cache = Cached2()

def id():
  return {"uname": G.cache.name, "floatin_ip": G.cache.external_ip, "private_ip": G.cache.private_ip}

def remote_get(path):
  try:
    remote_url = f"{G.cache.remote_url}/{path}"
    ret_str = urllib.request.urlopen(remote_url, data=None, timeout=1).read().decode('utf8')
    try:
      ret = json.loads(ret_str)
    except Exception as e_inner:
      logging.warn(e_inner)
      logging.warn(ret_str)
      ret = {"notjson": str(ret_str)}
  except Exception as e:
    logging.warn(e)
    ret = {"error": f"error accessing {remote_url}"}
  return ret

# GLOBAL
count = 0
app = FastAPI()

@app.get("/")
def read_root():
  return id()

@app.get("/health")
def read_health():
  return {"status": "healthy"}

def id_increment_count():
  """Return the id() dict with an incremented count global variable"""
  global count
  count = count + 1
  return {**id(), "count": count}

@app.get("/increment")
def read_increment():
  ret = id_increment_count()
  if G.cache.remote_url:
    ret["remote"] = remote_get("increment")
  return ret

@app.get("/postgresql")
def read_increment_postgresqlincrement():
  """Everything in /increment along with a postgresql database read and a remote postgresql read"""
  ret = id_increment_count()
  ret["postgresql"] = postgresql.get_increment_postgresql(G.cache) if G.cache.postgresql_credentials else "no postgresql configured"
  if G.cache.remote_url:
    ret["remote"] = remote_get("postgresql")
  return ret

if __name__ == "__main__":
  initialize()
  uvicorn.run(app, host="0.0.0.0", port=8000)