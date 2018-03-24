FROM ubuntu:xenial

RUN apt-get update && apt-get install -y nano locate
RUN apt-get update && apt-get install -y wget python-pip locales
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

ENV TERM linux
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8

RUN python -c 'import urllib; print urllib.urlopen("https://bootstrap.saltstack.com").read()' > /root/bootstrap-salt.sh
RUN sh /root/bootstrap-salt.sh -X -d -i localdev -g https://github.com/mnieber/salt.git git develop

ADD salt_master /etc/salt/master
