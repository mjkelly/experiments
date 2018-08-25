# Ansible

Ansible experiments.

I use virtualenv for this stuff. Here's the initial setup:

```
virtualenv .venv
source .venv/bin/activate
pip install ansible
```

You can do either of the following things when you want to use ansible:

**Thing 1**: Source the virtualenv and use `ansible-playbook` there:
```
source .venv/bin/activate
# ansible things
```
(Run `deactivate` to exit the environment without exiting your shell.)

**Thing 2**: Run `.venv/bin/ansible-playbook` directly from the virtualenv. No
sourcing required!
