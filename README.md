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

## License

This script is licensed under the MIT License.
