
#SNMP_GET_CPU_Usage

import asyncio
import csv
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

class SnmpCsvResult(TypedDict):
    timestamp: str | None
    ip: str | None
    cpu_percent: str | None

TARGET_IP = "192.168.2.45"
REQUESTED_OID = "1.3.6.1.4.1.9.2.1.56.0"

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

    transport = await UdpTransportTarget.create((TARGET_IP, 161), timeout=2, retries=1)
    eng = SnmpEngine()

    iterations: int = 4 * 60 * 2
    threshold: int = 80

    fieldnames: list[set] = ["timestamp", "ip", "cpu_percent"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        with open(f"{timestamp}_snmp_cpucpm_CPUTotal5sec.csv", "a", newline="", encoding="utf-8") as f:
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)     
            writer.writeheader()

            for _ in range(iterations):

                errInd, errStat, errIdx, varBinds = await snmp_get_cpu(REQUESTED_OID, transport, eng)

                try:
                    raise_snmp_error(errInd, errStat, REQUESTED_OID)

                except (SnmpEngineError, SnmpPduError) as e:
                    print("SNMP failed:", e)

                else:
                    for response_oid, val in varBinds:
                        full_oid = response_oid.prettyPrint()
                        text = val.prettyPrint()
                        if text.startswith("No Such Instance") or text.startswith("No Such Object"):
                            text = None
                        print(f"{full_oid} = {text}")
                                                
                        result_csv: SnmpCsvResult = {
                            "timestamp": timestamp,
                            "ip": TARGET_IP,
                            "cpu_percent": text,
                        }
                        try:
                            writer.writerow(result_csv)
                        except OSError as error:
                            print(f"error writing CSV: {error}")
                        
                        if text in (None, "None"):
                            continue
                        value_cpu = int(text)
                        if value_cpu >= threshold:
                            print(f"WARNING: CPU USAGE is: {value_cpu}")
                            continue

                await asyncio.sleep(30)

    except OSError as error:
        print(f"error opening CSV: {error}")        
           
if __name__ == "__main__":
    asyncio.run(main())
