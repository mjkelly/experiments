# Prometheus
#
# This is a small layer on top of the official Prometheus Dockerfile that sets
# up a volume to hold configuration and data.
FROM       prom/prometheus
MAINTAINER Michael Kelly <michael@michaelkely.org>

VOLUME     [ "/data" ]
VOLUME     [ "/conf" ]
WORKDIR    /prometheus
ENTRYPOINT [ "/go/src/github.com/prometheus/prometheus/prometheus" ]
CMD        [ "-logtostderr", "-config.file=/conf/prometheus.conf", \
             "-storage.local.path=/data/metrics", \
             "-web.console.libraries=/go/src/github.com/prometheus/prometheus/console_libraries", \
             "-web.console.templates=/go/src/github.com/prometheus/prometheus/consoles" ]
