def is_core(hostname: str) -> bool:
    return hostname.lower().startswith("core")

def extract_hostname(config_text: str) -> str | None:
    for line in config_text.splitlines():
        line = line.strip()
        if line.startswith("hostname "):
            parts = line.split()
            if len(parts) == 2 and parts[1]:
                return parts[1]
            return ""
        return None

def make_description(interface: str, purpose: str) -> str:
    return f"description {purpose} {interface}"
