FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y wireguard-tools python3-requests iproute2 openresolv iptables procps inetutils-ping && rm -rf /var/lib/apt/lists/*
COPY app/ /app
RUN chmod +x /app/docker-entrypoint.sh /app/pvpn.py
WORKDIR /app
ENV PATH="$PATH:/app"
ENTRYPOINT ["docker-entrypoint.sh"]
