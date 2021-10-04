variable "basename" {
  default = "pfq3"
}
variable "ssh_key_name" {
  default = "pfq"
}
variable "resource_group_name" {
  default = "default"
}
variable "region" {
  default = "us-south"
}
variable "subnets" {
  default = 2
}
variable "profile" {
  default = "cx2-2x4"
}
variable "image_name" {
  default = "ibm-ubuntu-20-04-minimal-amd64-2"
}

# variable "activity_tracker_crn" {}
# variable "platform_metrics_crn" {}