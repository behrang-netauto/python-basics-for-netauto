
#WALK_SNMP_ifDescr_ifAlias_CSV_file

'''
ifDescr_results = {
  "transport_error": None,
  "snmp_error": None,
  "items": {
    "1": "Ethernet0/0",
    "2": "Ethernet0/1"
    }
}

ifAlias_results = {
  "transport_error": None,
  "snmp_error": None,
  "items": {
    "1": "Uplink to Core",
    "2": Null
    }
}

final_results = {
    "transport_error": None,
    "snmp_error": None,
    "items": {
    "1": {"ifDescr": "Ethernet0/0", "ifAlias": "Uplink to Core"},
    "2": {"ifDescr": "Ethernet0/1", "ifAlias": None}
    }
}
'''

import csv
import json
import asyncio
from datetime import datetime
from typing import Any, Sequence, Tuple, NamedTuple, AsyncIterator, TypedDict
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
    walk_cmd,
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

class ifResults(TypedDict):
    transport_error: str | None
    snmp_error: str | None
    items: dict | None

class SnmpBulkRunResult(TypedDict):
    transport_error: str | None
    snmp_error: str | None
    items: dict[str, dict] | None

class SnmpCsvResult(TypedDict):
    ip: str | None
    ifIndex: str | None
    ifName: str | None
    ifAlias: str | None

IFDESCR = "1.3.6.1.2.1.2.2.1.2"
IFALIAS = "1.3.6.1.2.1.31.1.1.1.18"

async def snmp_walk_if(target_ip: str, bulk_oid: str) -> AsyncIterator[SnmpTupleResult]:
    transport = await UdpTransportTarget.create((target_ip, 161), timeout=5, retries=1)
    oid_type = ObjectType(ObjectIdentity(bulk_oid))

    result = await walk_cmd(
        SnmpEngine(),
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
        lexicographicMode=False,
        maxRows=1,
        maxcalls=1,
    )

    yield SnmpTupleResult(result)

def raise_snmp_error(errInd: Any, errStat: Any, errIdx: int, varBinds: Sequence, bulk_oid: str) -> None:
    
    if errInd:
            raise SnmpEngineError(str(errInd))
    if errStat:
            raise SnmpPduError (f"{errStat} at {bulk_oid}")

async def walk(targt_ip, bulk_oid) -> ifResults:
    
    result: ifResults = {
        "transport_error": None,
        "snmp_error": None,
        "items": {},
    }

    async for errInd, errStat, errIdx, varBinds in snmp_walk_if(target_ip, bulk_oid):

        try:
            raise_snmp_error(errInd, errStat, errIdx, varBinds, bulk_oid)
        
        except SnmpEngineError as e:
            print("SNMP failed/Transport error:", e)
            result["transport_error"] = str(e)
            return result
        
        except SnmpPduError as e:
            print("SNMP PDU error:", e)
            result["snmp_error"] = str(e)
            return result
      
        else:
            resp_map = {response_oid.prettyPrint(): val.prettyPrint() for response_oid, val in varBinds}
            index = int(k.split(".", 1)[-1] for k in resp_map.keys())
            
            result["items"][0] = index
            result["items"][1] = resp_map.get()
         
            return result

if __name__ == "__main__":
    
    out = asyncio.run(main())
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    result_csv:SnmpCsvResult = {
        "ip": "192.168.2.45",
        "sysName": out["oids"]["1.3.6.1.2.1.1.5.0"].get("value"),
        "sysDescr": out["oids"]["1.3.6.1.2.1.1.1.0"].get("value"),
        "sysUpTime": out["oids"]["1.3.6.1.2.1.1.3.0"].get("value"),
    }

    fieldnames = ["ip", "sysName", "sysDescr", "sysUpTime"]
    
    try:
        with open(f"{timestamp}_snmp_basic.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerow(result_csv)

        print("snmp_basic.csv written successfully!!!")
    
    except OSError as error:
        print(f"error writing CSV: {error}")

    print(json.dumps(out, indent=2))
    
    with open(f"{timestamp}_snmp_out.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


     target_ip = "192.168.2.45"
   

