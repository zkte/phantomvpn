#!/usr/bin/env bash
set -e
IPv4=$(ip -j -4 address show dev eth0 scope global | jq -r '.[0].addr_info[0].local')
jq --arg ipv4 "$IPv4" '.inbounds[0].listen=$ipv4' /app/config.json > /tmp/config.json
exec sing-box run -c /tmp/config.json
