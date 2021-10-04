import procin
import urllib.request
import pytest
import functools
import json

class Cache:
  def app_url(self, ip):
    return f"http://{ip}:8000"

  @functools.lru_cache()
  def tf_output(self, dir):
    c = procin.Command(json=True)
    return c.run(["terraform", "output", f"-state={dir}/terraform.tfstate", "-json"])

  @property
  @functools.lru_cache()
  def tf_output_vpc_tf(self):
    return self.tf_output("../vpc_tf")

  @property
  @functools.lru_cache()
  def instances_front_fip(self):
    return [ self.app_url(value["fip"]) for key, value in self.tf_output_vpc_tf['instances_front']['value'].items() ]

  @property
  @functools.lru_cache()
  def instances_back_fip(self):
    return [ self.app_url(value["fip"]) for key, value in self.tf_output_vpc_tf['instances_back']['value'].items() ]

  @property
  @functools.lru_cache()
  def lb_front(self):
    return self.tf_output_vpc_tf['lb_front']['value']

class G:
  cache = Cache()

def curl(url):
  """curl url"""
  return urllib.request.urlopen(url, data=None, timeout=1).read().decode('utf8')

def verify_against_example_deep(curl_dict, example_dict):
  assert len(curl_dict) == len(example_dict)
  for k, v in curl_dict.items():
    assert k in example_dict
    if isinstance(v, dict):
      verify_against_example_deep(curl_dict[k], example_dict[k])

def verify_root(curl_s):
  """verify the root of the application"""
  example_dict = dict(uname="vpc3tier-front-0", floatin_ip="52.118.144.159",private_ip="10.0.0.5")
  curl_dict = json.loads(curl_s)
  verify_against_example_deep(curl_dict, example_dict)

def verify_back_increment(curl_s):
  """verify the /increment of the application"""
  example_dict = {"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":2}
  curl_dict = json.loads(curl_s)
  verify_against_example_deep(curl_dict, example_dict)


def verify_front_increment(curl_s):
  """verify the /increment of the application"""
  example_dict = {"uname":"vpc3tier-front-0","floatin_ip":"52.118.144.159","private_ip":"10.0.0.5","count":1,"remote":{"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":6}}
  curl_dict = json.loads(curl_s)
  verify_against_example_deep(curl_dict, example_dict)

def verify_front_postgresql(curl_s):
  example_dict = {"uname":"vpc3tier-front-0","floatin_ip":"52.118.144.159","private_ip":"10.0.0.5","count":10,"postgresql":"no postgresql configured","remote":{"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":21,"postgresql":{"count":3}}}
  curl_dict = json.loads(curl_s)
  verify_against_example_deep(curl_dict, example_dict)

def verify_back_postgresql(curl_s):
  example_dict = {"uname":"vpc3tier-back-0","floatin_ip":"169.48.154.27","private_ip":"10.0.1.5","count":34,"postgresql":{"count":14}}
  curl_dict = json.loads(curl_s)
  verify_against_example_deep(curl_dict, example_dict)

@pytest.mark.parametrize("url", G.cache.instances_front_fip + G.cache.instances_back_fip + [G.cache.lb_front])
def test_curl_root(url):
  verify_root(curl(url))

@pytest.mark.parametrize("url", G.cache.instances_back_fip)
def test_back_curl_increment(url):
  verify_back_increment(curl(f"{url}/increment"))

@pytest.mark.parametrize("url", G.cache.instances_front_fip + [G.cache.lb_front])
def test_front_curl_increment(url):
  verify_front_increment(curl(f"{url}/increment"))

@pytest.mark.parametrize("url", G.cache.instances_back_fip)
def test_back_curl_increment(url):
  verify_back_increment(curl(f"{url}/increment"))

@pytest.mark.parametrize("url", G.cache.instances_front_fip + [G.cache.lb_front])
def test_front_curl_postgresql(url):
  verify_front_postgresql(curl(f"{url}/postgresql"))

@pytest.mark.parametrize("url", G.cache.instances_back_fip)
def test_back_curl_postgresql(url):
  verify_back_postgresql(curl(f"{url}/postgresql"))
