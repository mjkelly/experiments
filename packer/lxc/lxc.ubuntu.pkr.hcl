source "lxc" "download" {
  config_file               = "./ubuntu.config"
  template_name             = "download"
  template_environment_vars = []
  template_parameters = [
    "--dist", "ubuntu",
    "--release", "lunar",
    "--arch", "amd64",
    "--variant", "default"
  ]
}
