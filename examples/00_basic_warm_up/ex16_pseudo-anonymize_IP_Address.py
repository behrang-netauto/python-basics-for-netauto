
import re

def mask_ip(match: re.Match) -> str:
    first_two = match.group(1)
    return f"{first_two}.xxx.xxx"

def main() -> None:
    log = """
Jan  1 10:00:01 R1 %SEC-3-ERROR: SSL handshake error from 10.1.2.3
Jan  1 10:00:05 R1 %SEC-3-INFO: Allowed connection from 192.168.10.200
"""

    ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3})\.(\d{1,3})\.(\d{1,3})")

    ts_pattern = re.compile(r"^\w{3}\s+\d+\s+\d+:\d+:\d+\s+\S+\s+", re.M)

    masked_log = ip_pattern.sub(mask_ip, log)
    print("-----original log-----")
    print(log)
    print("-----masked log-----")
    print(masked_log)

    log_no_ts = ts_pattern.sub("", log)
    print(log_no_ts)
    


if __name__ == "__main__":
    main()

