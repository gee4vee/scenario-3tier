resource "tls_private_key" "ssh" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

output "generated_ssh_key" {
  value     = tls_private_key.ssh
  sensitive = true
}

locals {
  ssh_key_name           = "${var.basename}"
}

output "ssh_key_name" {
  value     = local.ssh_key_name
}

resource "local_file" "ssh-key" {
  content         = tls_private_key.ssh.private_key_pem
  filename        = "../generated_key_rsa"
  file_permission = "0600"
}

resource "ibm_is_ssh_key" "generated_key" {
  name           = local.ssh_key_name
  public_key     = tls_private_key.ssh.public_key_openssh
  resource_group = data.ibm_resource_group.group.id
}



