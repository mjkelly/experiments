FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y supervisor apache2
RUN rm -r /etc/apache2/sites-enabled/*

ADD supervisord.conf /etc/supervisord.conf
COPY apache2.conf /etc/apache2/apache2.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
