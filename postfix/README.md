Postfix Local Relay Config
==========================

This directory contains a Postfix config to route most mail through a relay
host (a "smarthost"), via SMTP. (For your smarthost, you can use something like
Amazon SES, Mailgun, or even Gmail with an app-specific password).

With the configuration instructions below, the following kinds of mail are
relayed:

  * Mail to a remote domain name (destination is unmodified)
  * Mail to this machine's hostname (destination is rewritten according to
    /etc/postfix/virtual!)

The mail server listens only to connections to localhost, so you should not
become an open relay.


Installation
------------

The config is mostly ready to go, but you must add info about your relay host,
and you must fill out your hostname for the redirection rules.

   * Edit `relayhost' in `main.cf'; set it to your actual relay host.
   * Create `/etc/postfix/relay_password'. The format is this:
     `relayhost:port username:password'
     Mind the permissions of this file when you create it.
   * Create /etc/postfix/virtual, enter your rewriting rules. See
     http://www.postfix.org/VIRTUAL_README.html for documentation on the
     format. Set this to something like:
     `@$HOSTNAME destination@email.address'
     Where you fill out `$HOSTNAME' and your destination email address.
   * Copy `main.cf' to `/etc/postfix'.
   * Run `postmap /etc/postfix/relay_password' and `postmap
     /etc/postfix/virtual' to generate DB files postfix can use.

These instructions blithely assume you have a standard `master.cf' file already
in /etc/postfix. I've used this with the master.cf files from Debian Testing
from April 2014, and CentOS 6.

Cautionary Tales
----------------
I know just enough about Postfix to write up this config, and no more. Don't
trust Postfix configs from some stranger on the internet. You could fall and
hurt yourself.

Feel free to email michael@michaelkelly.org if want.
