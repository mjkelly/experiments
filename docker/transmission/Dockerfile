FROM ubuntu:latest
MAINTAINER Michael Kelly <m@michaelkelly.org>

RUN apt-get update
RUN apt-get install -y supervisor transmission-daemon

COPY ./supervisord.conf /etc/supervisord.conf

VOLUME /transmission/data
VOLUME /transmission/config

EXPOSE 49164 9091
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
