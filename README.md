# Ping Hosts

Ping Hosts is a Python command-line tool that pings a list of hosts and displays the results. It retrieves a list of hosts from an API endpoint, pings each host concurrently, and then sorts and displays the results.

## Requirements

* Python 3.x
* `ping3`, `requests`, and `tqdm` Python libraries (can be installed using pip)

## Usage

```
python ping_hosts.py [-h] [-t THREADS] [-p] [-v] [-l LIMIT]
```

## Arguments

* `-h, --help`: show the help message and exit.
* `-t THREADS, --threads THREADS`: number of worker threads. Default is 25.
* `-p, --progress`: display progress bar. Default is True.
* `-v, --verbose`: display verbose output. Default is False.
* `-l LIMIT, --limit LIMIT`: limit the number of results. Default is 10. Set to -1 to display all results.

## Examples

Ping hosts with default options:

```
python ping_hosts.py
```

Ping hosts with 50 worker threads, display verbose output, and limit results to 5:

```
python ping_hosts.py -t 50 -v -l 5
```

## Output

The script outputs a table with the following columns:

* `Hostname`: the hostname of the pinged host.
* `IP`: the IP address of the pinged host.
* `Delay`: the delay in milliseconds between sending and receiving the ping response. If the ping fails, the delay is shown as "No response".

## TODO List

- [x] Add filters to the `ping_hosts.py` script:
  - [x] Filter by country code or name
  - [x] Filter by active status
  - [x] Filter by owned status
  - [x] Filter by network port speed
  - [ ] Filter only hosts with socks_name
- [ ] Prioritize IPv6 if it is available

## Data Format Returned by the Mullvad API Endpoint

The API endpoint https://api.mullvad.net/www/relays/wireguard/ returns data in the following format:

{
    "hostname":"al-tia-wg-001",
    "**country_code**":"al",
    "**country_name**":"Albania",
    "city_code":"tia",
    "city_name":"Tirana",
    "**active**":true,
    "**owned**":false,
    "provider":"iRegister",
    "ipv4_addr_in":"31.171.153.66",
    "ipv6_addr_in":"2a04:27c0:0:3::a01f",
    "**network_port_speed**":1,
    "stboot":true,
    "pubkey":"bPfJDdgBXlY4w3ACs68zOMMhLUbbzktCKnLOFHqbxl4=",
    "multihop_port":3155,
    "**socks_name**":"al-tia-wg-socks5-001.relays.mullvad.net",
    "socks_port":1080
}

This data includes information about the hostname, country code and name, city code and name, IP addresses, network port speed, and other relevant details about the server. This information will be used by the `ping_hosts.py` script to ping each server and display the results in a user-friendly table.

## License

This script is licensed under the MIT License.
