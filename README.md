# Ping Mullvad Servers

Mullvad Server Ping is a Python command-line tool that pings a list of hosts and displays the results. It retrieves a list of hosts from an API endpoint, pings each host concurrently, and then sorts and displays the results.

## Requirements

* Python 3.x
* `ping3`, `requests`, `argparse`, and `tqdm` Python libraries (can be installed using pip)

## Installation

1. Make sure you have Python 3 installed. You can download it from the [official Python website](https://www.python.org/). 

2. Install the required Python libraries. You can do this by running the following command in your terminal:
```
pip install -r requirements.txt
```

Note: You might need to use `pip3` instead of `pip` if you have both Python 2 and Python 3 installed on your computer.

## Usage

```
python ping_mullvad.py [-h] [--country-code COUNTRY_CODE]
                    [--country-name COUNTRY_NAME] [-a [ACTIVE]]
                    [-o [OWNED]] [-s [SOCKS]] [--network-port-speed NETWORK_PORT_SPEED]
                    [-t THREADS] [-p] [-v] [-l LIMIT]
```

## Arguments

* `-h, --help`: show the help message and exit.
* `--country-code COUNTRY_CODE`: filter by country code
* `--country-name COUNTRY_NAME`: filter by country name
* `-a, --active`: filter by active status
* `-o, --owned`: filter by owned status
* `--socks [SOCKS]`: filter to only hosts with non-empty `socks_name` parameter
* `--network-port-speed NETWORK_PORT_SPEED`: filter by network port speed (in GBits - 1 or 10)
* `-t THREADS, --threads THREADS`: number of worker threads. Default is 25.
* `-p, --progress`: display progress bar. Default is True.
* `-v, --verbose`: display verbose output. Default is False.
* `-l LIMIT, --limit LIMIT`: limit the number of results. Default is 10. Set to -1 to display all results.

## Examples

Ping hosts with default options:

```
python ping_mullvad.py
```

Ping hosts in Canada with a network port speed of 10 Gbps, display verbose output, and limit results to 5:

```
python ping_mullvad.py --country-name Canada --network-port-speed 10 -v -l 5
```

Ping hosts that support SOCKS and are located in Europe, display progress bar, and limit results to 20:

```
python ping_mullvad.py --socks --country-name Europe -p -l 20
```

## Output

The script outputs a table with the following columns:

* `Hostname`: the hostname of the pinged host.
* `IP`: the IP address of the pinged host.
* `Delay`: the delay in milliseconds between sending and receiving the ping response. If the ping fails, the delay is shown as "No response".

## TODO List

- [x] Cache API request.
  - [ ] Make it slightly more complex? Expiry?
- [x] Add filters to the `ping_hosts.py` script:
  - [x] Filter by country code or name
  - [x] Filter by active status
  - [x] Filter by owned status
  - [x] Filter by network port speed
  - [x] Filter only hosts with `socks_name`
  - [ ] By type (openvpn, wireguard, bridge)
- [ ] Choose server list from API
  - [ ] Wireguard
  - [ ] OpenVPN
  - [ ] Bridge
- [ ] Prioritize IPv6 if it is available

## Data Format Returned by the Mullvad API Endpoint

The API endpoint https://api.mullvad.net/www/relays/all/ returns data in the following format:

{"hostname":"al-tia-ovpn-001","country_code":"al","country_name":"Albania","city_code":"tia","city_name":"Tirana","active":true,"owned":false,"provider":"iRegister","ipv4_addr_in":"31.171.154.50","ipv6_addr_in":"2a04:27c0:0:4::a01f","network_port_speed":1,"stboot":true,"type":"openvpn","status_messages":[]}

This data includes information about the hostname, country code and name, city code and name, IP addresses, network port speed, and other relevant details about the server. This information will be used by the `ping_hosts.py` script to ping each server and display the results in a user-friendly table.

## License

This script is licensed under the MIT License.
