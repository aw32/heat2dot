FROM ubuntu:xenial

RUN apt-get update && apt-get install -y python3 python3-yaml python3-flask graphviz

RUN mkdir /heat2dot

ADD *py /heat2dot/

ADD docker-entrypoint.sh /

CMD /docker-entrypoint.sh

EXPOSE 1111
