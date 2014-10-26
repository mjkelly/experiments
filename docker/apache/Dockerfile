FROM ubuntu:latest
MAINTAINER Michael Kelly <m@michaelkelly.org>

RUN apt-get update
RUN apt-get install -y supervisor apache2

# Not necessary, but reduces possibility of confusion.
RUN rm -r /etc/apache2/sites-enabled/*

COPY ./supervisord.conf /etc/supervisord.conf
COPY ./apache2.conf /etc/apache2/apache2.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
