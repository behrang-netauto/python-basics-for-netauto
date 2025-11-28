
def main() -> None:
    hostname = "DCI-CORE-1"
    loopback_ip = "10.100.0.1"
    location = "London"
    
    msg1 = "Hostname: " + hostname + " | Loopback: " + loopback_ip + " | Site: " + location
    print(msg1)

    msg2 = "Device {} is in {}, loopback {}".format(hostname, location, loopback_ip)
    print(msg2)

    msg3 = f"Device {hostname} is in Location {location}, loopback {loopback_ip}"
    print(msg3)

    msg4 = f"Device {hostname} ist bereit für Dienst"
    print(msg4)
    
if __name__ == "__main__":
    main()
 