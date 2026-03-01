terraform {
  required_version = ">= 1.7"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.14"
    }
  }

  backend "gcs" {
    bucket = "product-os-tfstate"
    prefix = "terraform/state"
  }
}

# ── Variables ──

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run deployment"
  type        = string
  default     = "asia-southeast1"
}

variable "api_image" {
  description = "Full Artifact Registry URI for the API container image"
  type        = string
}

variable "sentry_dsn" {
  description = "Sentry DSN for error reporting"
  type        = string
  default     = ""
  sensitive   = true
}

variable "supabase_url" {
  description = "Supabase project URL"
  type        = string
}

variable "supabase_service_role_key" {
  description = "Supabase service-role key"
  type        = string
  sensitive   = true
}

variable "redis_url" {
  description = "Redis connection string"
  type        = string
  sensitive   = true
}

# ── Provider ──

provider "google" {
  project = var.project_id
  region  = var.region
}

# ── Artifact Registry ──

resource "google_artifact_registry_repository" "api" {
  location      = var.region
  repository_id = "product-os"
  format        = "DOCKER"
  description   = "ProductOS container images"
}

# ── Cloud Run service ──

resource "google_cloud_run_v2_service" "api" {
  name     = "product-os-api"
  location = var.region

  template {
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = var.api_image

      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "SUPABASE_URL"
        value = var.supabase_url
      }
      env {
        name  = "SUPABASE_SERVICE_ROLE_KEY"
        value = var.supabase_service_role_key
      }
      env {
        name  = "REDIS_URL"
        value = var.redis_url
      }
      env {
        name  = "SENTRY_DSN"
        value = var.sentry_dsn
      }
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}

# ── Public access (unauthenticated — gated by Unkey at app layer) ──

resource "google_cloud_run_v2_service_iam_member" "public" {
  name     = google_cloud_run_v2_service.api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# ── Outputs ──

output "api_url" {
  description = "Cloud Run service URL for the API"
  value       = google_cloud_run_v2_service.api.uri
}
