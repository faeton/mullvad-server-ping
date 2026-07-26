#!/usr/bin/env python3
import argparse
import asyncio
import json
import math
import os
import re
import subprocess
import sys
import time
import urllib.request
from argparse import BooleanOptionalAction

API_URL = "https://api.mullvad.net/www/relays/all/"
CACHE_FILE = "api_cache.json"
CACHE_TTL = 24 * 3600


def get_host_list(country_code=None, country_name=None, active=None, owned=None,
                  network_port_speed=None, socks_only=False, server_type=None):
    fresh = os.path.exists(CACHE_FILE) and (time.time() - os.path.getmtime(CACHE_FILE) < CACHE_TTL)
    if fresh:
        with open(CACHE_FILE) as f:
            data = json.load(f)
    else:
        with urllib.request.urlopen(API_URL, timeout=15) as r:
            data = json.load(r)
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)

    def keep(h):
        if country_code and h["country_code"].lower() != country_code.lower(): return False
        if country_name and h["country_name"].lower() != country_name.lower(): return False
        if server_type and h["type"].lower() != server_type.lower(): return False
        if active is not None and h["active"] != active: return False
        if owned is not None and h["owned"] != owned: return False
        if network_port_speed is not None and h["network_port_speed"] != network_port_speed: return False
        if socks_only and not h.get("socks_name"): return False
        return True

    return [h for h in data if keep(h)]


_PING_RE = re.compile(r"time[=<]([\d.]+)\s*ms")


async def icmp_ping(host, timeout=2, count=1):
    ip = host["ipv4_addr_in"]
    if sys.platform == "darwin":
        cmd = ["ping", "-c", str(count), "-W", str(int(timeout * 1000)), ip]
    elif sys.platform.startswith("linux"):
        cmd = ["ping", "-c", str(count), "-W", str(max(1, int(timeout))), ip]
    else:
        cmd = ["ping", "-n", str(count), "-w", str(int(timeout * count * 1000)), ip]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
        )
        try:
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=(timeout + 1) * count)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()
            raise
        times = [float(t) for t in _PING_RE.findall(out.decode("utf-8", "ignore"))]
        delay = sum(times) / len(times) if times else math.inf
    except (OSError, asyncio.TimeoutError):
        delay = math.inf
    return (host["hostname"], ip, delay, host.get("socks_name", ""), host.get("socks_port", ""))


async def ping_all(hosts, concurrency, show_progress, count):
    sem = asyncio.Semaphore(concurrency)
    total = len(hosts)
    done = 0

    async def run(h):
        nonlocal done
        async with sem:
            res = await icmp_ping(h, count=count)
        done += 1
        if show_progress:
            print(f"\r{done}/{total}", end="", file=sys.stderr, flush=True)
        return res

    results = await asyncio.gather(*(run(h) for h in hosts))
    if show_progress:
        print("", file=sys.stderr)
    return results


def detect_vpn():
    try:
        if sys.platform == "darwin":
            out = subprocess.run(["route", "-n", "get", "default"], capture_output=True, text=True, timeout=2).stdout
            iface = re.search(r"interface:\s*(\S+)", out)
            gw = re.search(r"gateway:\s*(\S+)", out)
            if iface and re.match(r"(utun|tun|tap|ppp|wg)", iface.group(1)):
                return iface.group(1)
            if gw and re.match(r"(10\.|100\.6[4-9]\.|100\.[7-9]\d\.|100\.1[01]\d\.|100\.12[0-7]\.)", gw.group(1)):
                return gw.group(1)
        elif sys.platform.startswith("linux"):
            out = subprocess.run(["ip", "route", "show", "default"], capture_output=True, text=True, timeout=2).stdout
            m = re.search(r"dev\s+(\S+)", out)
            if m and re.match(r"(tun|tap|wg|ppp)", m.group(1)):
                return m.group(1)
    except Exception:
        pass
    return None


def main(args):
    hosts = get_host_list(country_code=args.country_code, country_name=args.country_name,
                          active=args.active, owned=args.owned,
                          network_port_speed=args.network_port_speed,
                          socks_only=args.socks, server_type=args.server_type)
    if not hosts:
        print("No hosts match filters.")
        sys.exit(0)

    vpn = detect_vpn()
    if vpn:
        print(f"WARNING: default route goes via {vpn} (looks like a VPN tunnel). "
              f"Latencies will be tunnel-routed and most relays will show 'No response'. "
              f"Disconnect your VPN for accurate results.", file=sys.stderr)
    if args.verbose:
        print(f"Pinging {len(hosts)} hosts...", file=sys.stderr)

    try:
        results = asyncio.run(ping_all(hosts, args.threads, args.progress, args.count))
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)

    results.sort(key=lambda x: x[2])
    if all(delay == math.inf for _, _, delay, _, _ in results):
        print("WARNING: no selected hosts replied to ICMP. Try lowering --threads, increasing --count, "
              "or checking whether your network blocks ping.", file=sys.stderr)
    if args.limit is not None and args.limit > -1:
        results = results[:args.limit]

    for hostname, ip, delay, socks_name, socks_port in results:
        d = "No response" if delay == math.inf else f"{delay:.2f} ms"
        if args.socks:
            print(f"{hostname:<20} {ip:<15} {d:<12} {socks_name}:{socks_port}")
        else:
            print(f"{hostname:<20} {ip:<15} {d}")


def cli():
    p = argparse.ArgumentParser(description="Ping Mullvad relays via ICMP and rank by latency.")
    p.add_argument("-cc", "--country-code", dest="country_code")
    p.add_argument("-cn", "--country-name", dest="country_name")
    p.add_argument("-a", "--active", action=BooleanOptionalAction, default=None)
    p.add_argument("-o", "--owned", action=BooleanOptionalAction, default=None)
    p.add_argument("--socks", action="store_true")
    p.add_argument("-sp", "--network-port-speed", dest="network_port_speed", type=int)
    p.add_argument("-t", "--threads", type=int, default=100, help="Concurrent connections (default 100).")
    p.add_argument("-n", "--count", type=int, default=1, help="ICMP packets per host (default 1).")
    p.add_argument("-p", "--progress", action=BooleanOptionalAction, default=True)
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("-l", "--limit", type=int, default=10, help="Top N fastest. -1 for all.")
    p.add_argument("--type", dest="server_type", help="wireguard, openvpn, etc.")
    args = p.parse_args()
    if args.threads < 1:
        p.error("--threads must be at least 1")
    if args.count < 1:
        p.error("--count must be at least 1")
    main(args)


if __name__ == "__main__":
    cli()
