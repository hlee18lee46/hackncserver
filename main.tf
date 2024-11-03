terraform {
  required_providers {
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.3.1"
    }
  }
}

provider "mongodbatlas" {
  public_key  = "your_key"
  private_key = "your_key"
}

resource "mongodbatlas_project" "my_project" {
  name   = "hacknc"
  org_id = "6709ec4d6bd7a919a35399c4"
}

resource "mongodbatlas_cluster" "hacknc" {
  project_id                  = mongodbatlas_project.my_project.id
  name                        = "hackncCluster"
  provider_name            = "TENANT"
  backing_provider_name    = "AWS"
  provider_region_name     = "US_EAST_1"
  provider_instance_size_name = "M0"
  cluster_type             = "REPLICASET"
  auto_scaling_disk_gb_enabled = false
}