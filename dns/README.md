# dns

Scripts for updating DNS records:

- `route53-update2.py` is the new version: it's written in python3, and uses boto and click. It can determine this machine's IP address on its own, without the need for a helper script.
- `route53-update.py` is python2, and has no dependencies. You probably shouldn't
  use it or look at it.
- `update_ip.sh` a wrapper script to determine current IP and pass arguments to
  `route53-update.py`.

# installation

To use `route53-update2.py`, run `make`. That will install dependencies in a
python virtualenv called `venv`, in the current directory.

To run the script via the venv, run:
```
./venv/bin/python ./route53-update2.py
```

To remove the venv, you can use `make clean`.
