# Lockdown

Make a copy of `hosts.example` that includes the hosts you want to configure.
This requires a user with passwordless sudo by default. (It uses
`ansible_become`.)

## WARNING

If you rely on the root password to administer your server(s) (via `su`), or
logging in as root via ssh, do not apply this recipe. We disable the root
password and disallow root from logging in via ssh.

## Configuration

Check `group_vars/all.yml` for config options.

## Running

Assuming you created a file named `hosts`, run this:

```
ansible-playbook -i hosts lockdown.yml
```

## Caveats

I'm a total noob at Ansible; don't look here for best practices. This is just
an exercise to give me a little more familiarity with writing my own Ansible
stuff.
