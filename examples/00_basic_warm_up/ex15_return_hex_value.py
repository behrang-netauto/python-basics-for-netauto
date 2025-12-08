
import re

text = "MAC address: 145400865868218"

pattern = re.compile(r"\d+")

def hex_replace(match):
    value = int(match.group())
    return hex(value)

result = pattern.sub(hex_replace, text)
print(result)

m = re.search(r"\d+", "abc123xyz")
print(m.group(0), type(m))



