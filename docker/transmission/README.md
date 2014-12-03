transmission
------------

This is a `Dockerfile` for transmission, the bittorrent client. We set up
transmission-daemon running in Docker, and let clients connect to it from the
host.

Usage
------

To build, run:

    docker build -t mjkelly/transmission . 

You may choose a different tag, of course. The tag "mjkelly/transmission" is
what `run.sh` uses.

`run.sh` is an example of how to start this image, specifically to show
examples of the volumes and forwarded ports required.

This config uses volumes from the host for both the data directory (so you can
access downloaded data), and for the configuration directory (so you can put
things in the torrents directory, and so the resume directory persists).

The RPC port is forwarded and bound only to localhost. The actual listening
port is bound to 0.0.0.0 (so the host can accept incoming connections).

If you have in-progress torrents (either downloading or seeding) that you want
to import from your existing setup, you can populate the `/torrents` and
`/resume` directories in `transmisison-daemon-config` before starting the
image.


Default Settings
----------------

`settings.json` is mostly standard. Noteworth settings:

  * The RPC whitelist is disabled. It is expected that you will expose the RPC
    port only to localhost on the host machine (like in `run.sh`), or change
    the settings.
  * Blocklists are enabled. You probably want to set up a cron job on the host
    to update the block list. Something like this:
    `@daily transmission-remote --blocklist-update`
