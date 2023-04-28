#!/usr/bin/env python3
import json
import requests
from ping3 import ping
import concurrent.futures
from tqdm import tqdm
import argparse
import math
import sys
import os

# Define a function to retrieve the list of hosts from the API endpoint
def get_host_list(country_code=None, country_name=None, active=None, owned=None, network_port_speed=None):
    url = "https://api.mullvad.net/www/relays/wireguard/"
    response = requests.get(url)
    data = json.loads(response.text)

    # Filter the list based on the provided parameters
    if country_code is not None:
        data = [d for d in data if d['country_code'].lower() == country_code.lower()]
    if country_name is not None:
        data = [d for d in data if d['country_name'].lower() == country_name.lower()]
    if active is not None:
        data = [d for d in data if d['active'] == active]
    if owned is not None:
        data = [d for d in data if d['owned'] == owned]
    if network_port_speed is not None:
        data = [d for d in data if d['network_port_speed'] == network_port_speed]

    return data

# Define a function to ping a single host and return the hostname, IP, and delay in milliseconds
def ping_host(host):
    ip = host['ipv4_addr_in']
    hostname = host['hostname']
    try:
        delay = ping(ip)
        if delay is None:
            result = (hostname, ip, math.inf)
        else:
            result = (hostname, ip, round(delay * 1000, 2))  # convert seconds to milliseconds
    except Exception as e:
        result = (hostname, ip, math.inf)
    return result

# Define the main function
def main(args):
    # Retrieve the list of hosts from the API endpoint, filtered by country code or name if specified
    host_list = get_host_list(country_code=args.country_code, country_name=args.country_name,
                              active=args.active, owned=args.owned, network_port_speed=args.network_port_speed)

    # Display a message if verbose output is enabled
    if args.verbose:
        print(f"Loaded {len(host_list)} hosts. Starting to ping...")

   # If the filtered list is empty, display a message and exit
    if not host_list:
        print("No hosts found that match the specified filters. Exiting...")
        sys.exit(0)

     # Use ThreadPoolExecutor for concurrent pinging
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        try:
            # Ping hosts concurrently and display progress bar if requested
            if args.progress:
                results = list(tqdm(executor.map(ping_host, host_list), total=len(host_list)))
            else:
                results = list(executor.map(ping_host, host_list))
        except KeyboardInterrupt:
            # Handle user interrupt gracefully
            print("\nInterrupted by user. Canceling pings...")
            executor.shutdown(wait=False)
            print("Ping cancellation completed. Exiting...")
            sys.exit(0)

    # Sort the result based on delay
    results.sort(key=lambda x: x[2], reverse=True)  # reverse sort

    # Limit the results if requested
    if args.limit is not None and args.limit > -1:
        results = results[-args.limit:]

    # Print the result in a formatted table
    print('{:<20} {:<15} {}'.format('Hostname', 'IP', 'Delay'))
    for result in results:
        print('{:<20} {:<15} {}'.format(result[0], result[1], 'No response' if result[2] == math.inf else f'{result[2]} ms'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping a list of hosts and display the results.")
    parser.add_argument('--country-code', '-cc', dest='country_code', type=str, help="Filter by country code")
    parser.add_argument('--country-name', '-cn', dest='country_name', type=str, help="Filter by country name")
    parser.add_argument('--active', '-a', dest='active', const=True, nargs='?', type=bool, help="Filter by active status (default is True)")
    parser.add_argument('--owned', '-o', dest='owned', const=True, nargs='?', type=bool, help="Filter by owned status (default is True)")
    parser.add_argument('--network-port-speed', '-sp', dest='network_port_speed', type=int, help="Filter by network port speed")
    parser.add_argument('-t', '--threads', type=int, default=25, help="Number of worker threads. Default is 25.")
    parser.add_argument('-p', '--progress', action='store_true', default=True, help="Display progress bar. Default is True.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Display verbose output. Default is False.")
    parser.add_argument('-l', '--limit', type=int, default=10, help="Limit the number of results. Default is 10. Set to -1 to display all results.")
    args = parser.parse_args()

    main(args)
