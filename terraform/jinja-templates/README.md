# Background

This is an experiment with generating .tf files from jinja2 templates.
Terraform includes modules and variables, but the language is underfeatured.

It's very hard, for instance, to conditionally set an attribute in a map.
(Setting it to a value if a variable is true, and leaving it unset if a
variable is false.)

It's also hard to generate a series of resources -- if 'count' doens't work for
you, there's nothing to fall back on.

The motivation to do things this way will probably go away when Terraform 0.12
is released.

I'm not claiming this is the right way to do things -- it's an example of what
doing it this way would look like.

# Setup

1. Run 'make venv'
2. Make sure `terraform` is installed

# Usage

Run `./venv/bin/python generate.py hosts.tf.j2`

You'll get a generated `hosts.tf` file.
