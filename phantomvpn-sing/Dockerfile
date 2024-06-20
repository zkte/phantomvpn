FROM ghcr.io/sagernet/sing-box
RUN apk add jq iproute2
COPY app /app
WORKDIR /app
ENV PATH="$PATH:/app"
ENTRYPOINT ["docker-entrypoint.sh"]
