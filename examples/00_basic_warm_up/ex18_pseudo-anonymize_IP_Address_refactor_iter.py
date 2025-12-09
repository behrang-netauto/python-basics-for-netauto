
import re

ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3})\.(\d{1,3})\.(\d{1,3})")

ts_pattern_line = re.compile(r"^\w{3}\s+\d+\s+\d+:\d+:\d+\s+\S+\s+")

def mask_ip(match: re.Match) -> str:
    first_two = match.group(1)
    return f"{first_two}.xxx.xxx"

def iter_masked_lines(log: str):
    for line in log.splitlines():
        yield ip_pattern.sub(mask_ip, line)

def iter_strip_lines(log: str):
    for line in log.splitlines():
        yield ts_pattern_line.sub("", line)

def main() -> None:
    log = """
Jan  1 10:00:01 R1 %SEC-3-ERROR: SSL handshake error from 10.1.2.3
Jan  1 10:00:05 R1 %SEC-3-INFO: Allowed connection from 192.168.10.200
"""
   
    for line in iter_masked_lines(log):
        print(line)
    
    log_no_ts = "\n".join(iter_strip_lines(log))
    print(log_no_ts)
    

    print(repr(log.splitlines()))

if __name__ == "__main__":
    main()

