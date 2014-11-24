FROM ubuntu:latest
MAINTAINER Michael Kelly <m@michaelkelly.org>

RUN apt-get update
RUN apt-get install -y supervisor transmission-daemon
RUN mkdir -p /torrent/incomplete

COPY ./supervisord.conf /etc/supervisord.conf
COPY ./transmission-daemon-config /etc/transmission

VOLUME /torrent

EXPOSE 49164 9091
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
