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
def get_host_list():
    url = "https://api.mullvad.net/www/relays/wireguard/"
    response = requests.get(url)
    data = json.loads(response.text)
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

    # Retrieve the list of hosts from the API endpoint
    # TODO: Add a file cache with 1month expiry
    host_list = get_host_list()

    # Display a message if verbose output is enabled
    if args.verbose:
        print(f"Loaded {len(host_list)} hosts. Starting to ping...")

    # Use ThreadPoolExecutor for concurrent pinging.
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        try:
            if args.progress:
                results = list(tqdm(executor.map(ping_host, host_list), total=len(host_list)))
            else:
                results = list(executor.map(ping_host, host_list))
        except KeyboardInterrupt:
            print("\nInterrupted by user. Canceling pings...")
            executor.shutdown(wait=False)
            print("Ping cancellation completed. Exiting...")
            sys.exit(0)

    # Sort the result based on delay.
    results.sort(key=lambda x: x[2], reverse=True)  # reverse sort

    # Limit the results if requested.
    if args.limit is not None and args.limit > -1:
        results = results[-args.limit:]

    # Print the result in a good looking way.
    print('{:<20} {:<15} {}'.format('Hostname', 'IP', 'Delay'))
    for result in results:
        print('{:<20} {:<15} {}'.format(result[0], result[1], 'No response' if result[2] == math.inf else f'{result[2]} ms'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping a list of hosts and display the results.")
    parser.add_argument('-t', '--threads', type=int, default=25, help="Number of worker threads. Default is 25.")
    parser.add_argument('-p', '--progress', action='store_true', default=True, help="Display progress bar. Default is True.")
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help="Display verbose output. Default is False.")
    parser.add_argument('-l', '--limit', type=int, default=10, help="Limit the number of results. Default is 10. Set to -1 to display all results.")
    args = parser.parse_args()

    main(args)
