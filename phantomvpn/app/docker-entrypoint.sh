#!/usr/bin/env bash
CONFIG=/config/phantom_vpn.json
set -e
unregister() {
  wg-quick down tun0
  wait ${!}
}
trap 'kill ${!} || :; unregister' SIGTERM SIGINT EXIT
if [ ! -f "$CONFIG" ]; then
echo "login..."
  pvpn.py -a "$CONFIG" -l "$phantomvpn_user:$phantomvpn_pass"
fi
echo "grab server..."
pvpn.py -a "$CONFIG" -q "$SERVER" > /etc/wireguard/tun0.conf
echo "starting wireguard..."
wg-quick up tun0
ping -W 1 -c 1 185.123.227.250
while true
do
    tail -f /dev/null & wait ${!}
done
