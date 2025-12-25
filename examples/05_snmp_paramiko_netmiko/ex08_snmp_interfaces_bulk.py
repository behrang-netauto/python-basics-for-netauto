
#WALK_SNMP_ifDescr_ifAlias_CSV_file

'''
ifDescr_results = {
  "transport_error": None,
  "items": {
    "1": "Ethernet0/0",
    "2": "Ethernet0/1"
    }
}

ifAlias_results = {
  "transport_error": None,
  "items": {
    "1": "Uplink to Core",
    "2": Null
    }
}

final_results = {
    "transport_error": None,
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

class ifResults(TypedDict):
    transport_error: str | None
    items: dict | None

class SnmpBulkRunResult(TypedDict):
    transport_error: str | None
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

    async for errInd, errStat, errIdx, varBinds in walk_cmd(
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
    ):
        yield SnmpTupleResult(errInd, errStat, errIdx, varBinds)

def raise_snmp_error(errInd: Any) -> None:
    
    if errInd:
            raise SnmpEngineError(str(errInd))

async def walk(target_ip, bulk_oid) -> ifResults:
    
    result: ifResults = {
        "transport_error": None,
        "items": {},
    }

    async for errInd, errStat, errIdx, varBinds in snmp_walk_if(target_ip, bulk_oid):

        try:
            raise_snmp_error(errInd)
        
        except SnmpEngineError as e:
            print("SNMP failed/Transport error:", e)
            result["transport_error"] = f"'{bulk_oid}': '{str(e)}'"
            return result
        
        if errStat:
            return result
      
        else:
            for response_oid, val in varBinds:
                full_oid = response_oid.prettyPrint()
                index = int(full_oid.rsplit(".", 1)[-1])
                text = val.prettyPrint()
                if text.startswith("No Such Instance") or text.startswith("No Such Object"):
                    text = None
                result["items"][index] = text

    return result

async def main() -> None:

    final_result: SnmpBulkRunResult = {
        "transport_error": None,
        "items": {},
    }

    target_ip = "192.168.2.45"
    ifDescr_results: ifResults = await walk(target_ip, IFDESCR)
    ifAlias_results: ifResults = await walk(target_ip, IFALIAS)

    if ifDescr_results["transport_error"] or ifAlias_results["transport_error"]:
        final_result["transport_error"] = (
            ifDescr_results["transport_error"] or ifAlias_results["transport_error"]
        )
        return final_result
    #ifDescr_results["items"] = {"1": "Ethernet0/0", ...}
    #ifAlias_results["items"] = {"1": "Uplink", ...}

    descr_items = ifDescr_results["items"] or {}
    alias_items = ifAlias_results["items"] or {}

    all_indexes = set(descr_items) | set(alias_items)

    for index in sorted(all_indexes, key=int):
        final_result["items"][index] = {
            "ifDescr": descr_items.get(index),
            "ifAlias": alias_items.get(index),
        }

    final_result["items"] = {
        index: row
        for index, row in final_result["items"].items()
        if row.get("ifAlias") not in (None, "", " ")
    }
    return final_result

if __name__ == "__main__":
    
    out = asyncio.run(main())
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    fieldnames = ["ip", "ifIndex", "ifName", "ifAlias"]
    
    try:
        with open(f"{timestamp}_snmp_ifdesc.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()

            for index, row in out["items"].items():

                result_csv: SnmpCsvResult = {
                    "ip": "192.168.2.45",
                    "ifIndex": str(index),
                    "ifName": row.get("ifDescr"),
                    "ifAlias": row.get("ifAlias"),
                }
                writer.writerow(result_csv)

        print("snmp_basic.csv written successfully!!!")
    
    except OSError as error:
        print(f"error writing CSV: {error}")

    print(json.dumps(out, indent=2))
    
    with open(f"{timestamp}_snmp_ifdesc.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


     
   

