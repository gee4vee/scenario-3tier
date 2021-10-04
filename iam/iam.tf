locals {
  provider_region = var.region
}

output basename {
  value = var.basename
}

data "ibm_resource_group" "group" {
  name = var.resource_group_name
}

resource "ibm_iam_access_group" "network" {
  name        = "${var.basename}-network"
  description = "network administrators"
}
resource "ibm_iam_service_id" "network" {
  name        = "${var.basename}-network"
  description = "network service id"
}
resource "ibm_iam_access_group_members" "network" {
  access_group_id = ibm_iam_access_group.network.id
  iam_service_ids = [ibm_iam_service_id.network.id]
}

resource "ibm_iam_access_group_policy" "network_policy" {
  access_group_id = ibm_iam_access_group.network.id
  roles           = ["Viewer"]
  resources {
    resource_type = "resource-group"
    resource      = data.ibm_resource_group.group.id
  }
}

resource "ibm_iam_access_group_policy" "networkshared_is_resources" {
  access_group_id = ibm_iam_access_group.network.id
  roles           = ["Editor"]
  resources {
    service = "is"
  }
}

# Manager is needed to delete a key
resource "ibm_iam_access_group_policy" "postgresql" {
  access_group_id = ibm_iam_access_group.network.id
  roles           = ["Editor"]
  resources {
    service           = "databases-for-postgresql"
  }
}

resource "ibm_iam_service_api_key" "network" {
  name = var.basename
  iam_service_id = ibm_iam_service_id.network.iam_id
}

output apikey {
  sensitive = true
  value = ibm_iam_service_api_key.network.apikey
}
