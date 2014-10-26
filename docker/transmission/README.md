transmission
------------

This is a `Dockerfile` for transmission, the bittorrent client. We set up
transmission-daemon running in Docker, and let clients connect to it from the
host.

Usage
------

`run.sh` is an example of how to start this image. Notably, the expectation is
that the user will mount a data directory from the host.

Additionally, if you have in-progress torrents (either downloading or seeding)
that you want to import from your existing setup, you can populate the
`/torrents` and `/resume` directories in `transmisison-daemon-config` before
building, if you like. (Though this will dirty your image with your in-progress
state.)


Default Settings
----------------

`settings.json` is mostly standard. Noteworth settings:

  * The RPC whitelist is disabled. It is expected that you will expose the RPC
    port only to localhost on the host machine (like in `run.sh`), or change
    the settings.
  * Blocklists are enabled. You probably want to set up a cron job on the host
    to update the block list. Something like this:
    `@daily transmission-remote --blocklist-update`
