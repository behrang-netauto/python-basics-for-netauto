
#SNMP_GET_CPU_Usage_SSH_NETMIKO

import getpass
from netmiko import ConnectHandler
from netmiko.exceptions import (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException)
from pathlib import Path
import asyncio
from datetime import datetime
from typing import Any, Sequence, Tuple, NamedTuple, TypedDict
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    USM_AUTH_HMAC96_SHA,
    USM_PRIV_CFB128_AES,
)
class SnmpTupleResult(NamedTuple):
    errInd: Any
    errStat: Any
    errIdx: int
    varBinds: Sequence[Tuple[Any, Any]]

class SnmpEngineError(RuntimeError): ...
class SnmpPduError(RuntimeError): ...

TARGET_IP = "192.168.2.45"
REQUESTED_OID = "1.3.6.1.4.1.9.2.1.56.0"

def cmd_show(TARGET_IP: str, username: str, password: str, secret: str | None = None) -> None:
    cmds = [
        "show processes cpu sorted | ex 0.00"
    ]
    devices = [
    {"device_type": "cisco_ios", "ip": TARGET_IP, "username": username, "password": password},
    ]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    home_dir = Path.home()
    base_dir = home_dir / "Documents" / "Python" / "Code/netauto_example_01" / "python-basics-for-netauto" / "examples" / "05_snmp_paramiko_netmiko"
    logs_dir = base_dir / "debug"
    logs_dir.mkdir(parents=True, exist_ok=True)
        
    out_file = logs_dir / f"{timestamp}_{TARGET_IP}_cpu_debug.txt"

    for device in devices:
        if secret:
            device["secret"] = secret

        conn = None
        log_block = "default_text"
        try:
            conn = ConnectHandler(**device)
            
            if not conn.check_enable_mode():
                if secret:
                    conn.enable()
                else:
                    raise RuntimeError("thers is neither secret nor pri 15!!!!")
            
            conn.send_command("terminal length 0")
            outs = {c: conn.send_command(c, read_timeout=15, expect_string=r"#") for c in cmds}
            log_block = f"\n-----success-----\n\n{outs}\n"

        except (ReadTimeout, NetmikoAuthenticationException, NetmikoTimeoutException) as error:
            log_block = f"\n-----failed-----\n\n{type(error).__name__}: {error}\n"
            
        except Exception as error:
            log_block = f"\n-----failed-----\n\nUnexpected error: {error}\n"

        finally:
            if conn is not None:
                conn.disconnect()

            with open(out_file, "a", encoding="utf-8") as f:
                f.write(log_block)
        
            print("\nlogs written, we are good, continuing monitoring...\n")

async def snmp_get_cpu(REQUESTED_OID: str, transport: UdpTransportTarget, eng: SnmpEngine) -> SnmpTupleResult:
    
    oid_type = ObjectType(ObjectIdentity(REQUESTED_OID))

    result = await get_cmd(
        eng,
        UsmUserData(
            userName="SNMPUser1",
            authKey="AUTHPass1",
            privKey="PRIVPass1",
            authProtocol=USM_AUTH_HMAC96_SHA,
            privProtocol=USM_PRIV_CFB128_AES,
        ),
        transport,
        ContextData(),
        oid_type,
        lookupMib=False,
    )

    return SnmpTupleResult(*result)

def raise_snmp_error(errInd: Any, errStat: Any, REQUESTED_OID: str) -> None:
    if errInd:
            raise SnmpEngineError(str(errInd))
    if errStat:
            raise SnmpPduError(f"{errStat.prettyPrint()} at {REQUESTED_OID}")    
    
async def main() -> None:

    print(f"user/pass for {TARGET_IP}:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    secret = getpass.getpass("Enable secret (blank if none): ").strip()

    transport = await UdpTransportTarget.create((TARGET_IP, 161), timeout=2, retries=1)
    eng = SnmpEngine()

    iterations: int = 4 * 60 * 2
    threshold: int = 2

    try:
            for _ in range(iterations):

                errInd, errStat, errIdx, varBinds = await snmp_get_cpu(REQUESTED_OID, transport, eng)
                try:
                    raise_snmp_error(errInd, errStat, REQUESTED_OID)
                except (SnmpEngineError, SnmpPduError) as e:
                    print("SNMP failed:", e)
                else:
                    for response_oid, val in varBinds:
                        text = val.prettyPrint()
                        if text.startswith("No Such Instance") or text.startswith("No Such Object"):
                            text = None
                        if text in (None, "None"):
                            continue
                        try:
                            value_cpu = int(text)
                        except ValueError:
                            continue
                        if value_cpu >= threshold:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            print(f"WARNING: CPU USAGE is: {value_cpu} at {timestamp}!!!!")
                            await asyncio.to_thread(cmd_show, TARGET_IP, username, password, secret= secret or None)

                await asyncio.sleep(30)

    except OSError as error:
        print(f"error opening CSV: {error}")        
           
if __name__ == "__main__":
    asyncio.run(main())
