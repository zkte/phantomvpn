#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess
import requests
from base64 import b64encode
from uuid import uuid4
from hashlib import sha1

APP = "avira/android_vpn"
TOKEN = "f5902d4bf294bb4b28a5895c54b7f720dfed572bfb07e2ea8a1989e32a03751d"


class PhantomVPN:
    def __init__(self, auth={}):
        self.sess = requests.Session()
        self.sess.headers["user-agent"] = "Dart/2.16 (dart:io)"
        if auth:
            self.auth = auth
        else:
            self.login()

    def get_auth(self):
        if "access_token" in self.auth:
            return f"Bearer {self.auth['access_token']}"
        else:
            client = b64encode(f"{APP}:{TOKEN}".encode("utf-8")).decode("utf-8")
            return f"Basic {client}"

    def device_id_gen(self):
        _id = sha1(uuid4().hex.encode("utf-8")).hexdigest()
        return f"0111-{_id}"

    def api_req(self, url, params={}, data={}):
        self.sess.headers["authorization"] = self.get_auth()
        if data:
            r = self.sess.post(url, json=data, timeout=10)
        else:
            r = self.sess.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()

    def login(self, username="", password=""):
        self.auth = {}
        if password:
            data = {"username": username, "password": password, "grant_type": "password"}
        else:
            data = {"grant_type": "client_credentials"}
        self.auth = self.api_req("https://api.my.avira.com/v2/oauth", data=data)
        self.auth["device_token"] = self.device_id_gen()

    def refresh(self):
        if self.auth.get("refresh_token"):
            device = self.auth["device_token"]
            client = b64encode(f"{APP}:{TOKEN}".encode("utf-8")).decode("utf-8")
            headers = {"OAuthRefresh": "true", "authorization": f"Basic {client}"}
            data = {
                "grant_type": "refresh_token",
                "client_id": "mobile",
                "refresh_token": self.auth.get("refresh_token"),
            }
            r = self.sess.post("https://api.my.avira.com/v2/oauth", headers=headers, json=data, timeout=10)
            r.raise_for_status()
            self.auth = r.json()
            self.auth["device_token"] = device
        else:
            self.login()

    def licence(self):
        params = {"device_id": self.auth.get("device_token")}
        licence = self.api_req("https://api.phantom.avira-vpn.com/v1/license", params=params)
        if licence.get("error") == "unauthorized":
            self.refresh()
        return self.api_req("https://api.phantom.avira-vpn.com/v1/license", params=params)

    def traffic(self):
        params = {"device_id": self.auth.get("device_token")}
        return self.api_req("https://api.phantom.avira-vpn.com/v1/traffic", params=params)

    def servers(self):
        params = {"device_id": self.auth.get("device_token"), "type": "wg", "lang": "en"}
        return self.api_req("https://api.phantom.avira-vpn.com/v1/regions", params=params)

    def get_host(self, region):
        for reg in self.servers().get("regions"):
            if reg["id"] == region:
                return reg["host"]

    def register(self, region):
        print(self.licence(), file=sys.stderr)
        print(self.traffic(), file=sys.stderr)
        wg_auth_url = f"https://{self.get_host(region)}:8443/v1/wg/auth"
        genkey = subprocess.run(["wg", "genkey"], capture_output=True)
        private_key = genkey.stdout.decode("utf-8")[:-1]
        pubkey = subprocess.run(["wg", "pubkey"], input=private_key.encode("utf-8"), capture_output=True)
        public_key = pubkey.stdout.decode("utf-8")[:-1]
        data = {"device_id": self.auth.get("device_token"), "pubkey": public_key}
        headers = {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Nexus 5)"}
        if self.auth.get("refresh_token"):
            headers["authorization"] = self.auth['access_token']
        r = requests.post(wg_auth_url, headers=headers, json=data, timeout=10)
        r.raise_for_status()
        wg_auth = r.json()
        return (private_key, public_key, wg_auth)


parser = argparse.ArgumentParser(description="Avira Phantom VPN")
parser.add_argument("-s", "--servers", type=bool, const=True, default=False, nargs="?", help="List Servers")
parser.add_argument("-c", "--client", type=bool, const=True, default=False, nargs="?", help="client_credentials")
parser.add_argument("-l", "--login", help="email:password")
parser.add_argument("-a", "--auth", help="saved auth")
parser.add_argument("-p", "--wireproxy", help="wireproxy conf")
parser.add_argument("-q", "--quick", help="wg-quick conf")
args = parser.parse_args()

config = {}
if args.auth:
    if os.path.exists(args.auth):
        with open(args.auth) as f:
            config = json.loads(f.read())

pvpn = PhantomVPN(config)
if args.login:
    username, password = args.login.split(":")
    pvpn.login(username, password)
elif args.client:
    pvpn.login()
elif args.servers:
    for region in pvpn.servers().get("regions"):
        print(f"{region['id']: <10.10} {region['name']}")
elif args.wireproxy:
    private_key, public_key, wg_auth = pvpn.register(args.wireproxy)
    wireproxy_conf = []
    wireproxy_conf.append("[Interface]")
    wireproxy_conf.append(f"PrivateKey = {private_key}")
    wireproxy_conf.append(f"Address = {wg_auth['client_ipv4']}/32")
    wireproxy_conf.append(f"Address = {wg_auth['client_ipv6']}/128")
    wireproxy_conf.append(f"DNS = {wg_auth['dns_ipv4'][0]}")
    wireproxy_conf.append(f"DNS = {wg_auth['dns_ipv6'][0]}")
    wireproxy_conf.append("[Peer]")
    wireproxy_conf.append(f"PublicKey = {wg_auth['pubkey']}")
    wireproxy_conf.append("AllowedIPs = 0.0.0.0/0")
    wireproxy_conf.append("AllowedIPs = ::/0")
    wireproxy_conf.append("PersistentKeepalive = 180")
    wireproxy_conf.append(f"Endpoint = {wg_auth['server']}:{wg_auth['port']}")
    wireproxy_conf.append("[Socks5]")
    wireproxy_conf.append("BindAddress = 127.0.0.2:11080")
    print("\n".join(wireproxy_conf))
elif args.quick:
    private_key, public_key, wg_auth = pvpn.register(args.quick)
    wg_quick = []
    wg_quick.append("[Interface]")
    wg_quick.append(f"PrivateKey = {private_key}")
    wg_quick.append(f"Address = {wg_auth['client_ipv4']}")
    wg_quick.append(f"Address = {wg_auth['client_ipv6']}")
    for a in wg_auth["dns_ipv4"]:
        wg_quick.append(f"DNS = {a}")
    for a in wg_auth["dns_ipv6"]:
        wg_quick.append(f"DNS = {a}")
    wg_quick.append("")
    wg_quick.append("[Peer]")
    wg_quick.append(f"PublicKey = {wg_auth['pubkey']}")
    wg_quick.append(f"Endpoint = {wg_auth['server']}:{wg_auth['port']}")
    wg_quick.append("AllowedIPs = 0.0.0.0/0, ::/0")
    wg_quick.append("PersistentKeepalive = 180")
    print("\n".join(wg_quick))

if pvpn.auth and args.auth:
    with open(args.auth, "w+", encoding="utf-8") as f:
        f.write(json.dumps(pvpn.auth, indent=2))
    print(f"saved {args.auth}", file=sys.stderr)
