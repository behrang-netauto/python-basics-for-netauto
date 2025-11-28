
def main() -> None:
    hostname = "R1"
    loopback_ip = "10.0.0.1"
    vlans = [10, 20, 30]
    is_core_switch = True
    cost = 0.75
    MAX_SESSIONS = 100
    ospf_areas = {0: "backbone", 10: "branch"}
    print(hostname, type(hostname))
    print(loopback_ip, type(loopback_ip))
    print(vlans, type(vlans))
    print(is_core_switch, type(is_core_switch))
    print(cost, type(cost))
    print(f"MAX_SESSIONS: {MAX_SESSIONS}", type(MAX_SESSIONS))
    print(ospf_areas, type(ospf_areas))

if __name__ == "__main__":
    main()



