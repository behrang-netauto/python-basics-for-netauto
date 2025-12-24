
#Batch_GET_SNMP_into_Dict_CSV_file

'''

results = {
  "transport_error": None,
  "oids": {
     "1.3.6...1.0": {"ok": True,  "value": "...", "error": None, "response_oid": "1.3.6...1.0"},
     "1.3.6...2.0": {"ok": False, "value": None, "error": "noAccess", "response_oid": "1.3.6...2.0"},
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
    USM_AUTH_HMAC96_SHA,
    USM_PRIV_CFB128_AES,
)
class SnmpTupleResult(NamedTuple):
    errInd: Any
    errStat: Any
    errIdx: int
    varBinds: Sequence[Tuple[Any, Any]]

class SnmpEngineError(RuntimeError): ...
class SnmpPduError(RuntimeError):
    def __init__(self, message: str, bad_oid: str | None = None):
        super().__init__(message)
        self.bad_oid = bad_oid

class OidStatus(TypedDict):
    ok: bool
    value: str | None
    error: str | None
    response_oid: str | None

class SnmpRunResult(TypedDict):
    transport_error: str | None
    oids: dict[str, OidStatus]

class SnmpCsvResult(TypedDict):
    ip: str | None
    sysName: str | None
    sysDescr: str | None
    sysUpTime: str | None

async def snmp_get_oids(target_ip: str, oid_nums: Sequence[str]) -> AsyncIterator[SnmpTupleResult]:
    transport = await UdpTransportTarget.create((target_ip, 161), timeout=5, retries=1)
    oid_types = [ObjectType(ObjectIdentity(oid_num)) for oid_num in oid_nums]

    result = await get_cmd(
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
        *oid_types,
        lookupMib=False,
    )

    yield SnmpTupleResult(*result)

def raise_snmp_error(errInd: Any, errStat: Any, errIdx: int, varBinds: Sequence, oid_nums: Sequence[str]) -> None:
    
    if errInd:
            raise SnmpEngineError(str(errInd))
    if errStat:
            idx0 = int(errIdx) - 1 if errIdx else None
            bad_oid = oid_nums[idx0] if (idx0 is not None and 0 <= idx0 < len(oid_nums)) else "?"
            raise SnmpPduError(str(errStat), bad_oid=bad_oid)   

def hex_to_text(s: str) -> str:
    if s.startswith("0x"):
        return bytes.fromhex(s[2:]).decode("utf-8", errors="replace")
    return s

async def main() -> SnmpRunResult:

    target_ip = "192.168.2.45"
    
    oid_nums = [
        "1.3.6.1.2.1.1.5.0", 
        "1.3.6.1.2.1.1.1.0", 
        "1.3.6.1.2.1.1.3.0",
    ]
    
    result: SnmpRunResult = {
        "transport_error": None,
        "oids": {
            oid: {"ok": False, "value": None, "error": None, "response_oid": None}
            for oid in oid_nums
        },
    }

    async for errInd, errStat, errIdx, varBinds in snmp_get_oids(target_ip, oid_nums):

        try:
            raise_snmp_error(errInd, errStat, errIdx, varBinds, oid_nums)
        
        except SnmpEngineError as e:
            print("SNMP failed/Transport error:", e)
            result["transport_error"] = str(e)
            return result
        
        except SnmpPduError as e:
            print("SNMP PDU error:", e, "| bad_oid =", e.bad_oid)

            for oid in oid_nums:
                async for errInd, errStat, errIdx, varBinds in snmp_get_oids(target_ip, [oid]):
                    try:
                        raise_snmp_error(errInd, errStat, errIdx, varBinds, [oid])
                    
                    except SnmpEngineError as te:
                        print("Transport error on", oid, ":", te)
                        result["oids"][oid]["ok"] = False
                        result["oids"][oid]["error"] = str(te)
                        result["oids"][oid]["response_oid"] = None
                    
                    except SnmpPduError as pe:
                        print("PDU error on", oid, ":", pe)
                        result["oids"][oid]["ok"] = False
                        result["oids"][oid]["error"] = str(pe)
                        result["oids"][oid]["response_oid"] = oid

                    else:
                        for responce_oid, val in varBinds:
                            print(f"{responce_oid.prettyPrint()} = {val.prettyPrint()}")
                            result["oids"][oid]["ok"] = True
                            v = val.prettyPrint()
                            result["oids"][oid]["value"] = hex_to_text(v)
                            result["oids"][oid]["error"] = None
                            result["oids"][oid]["response_oid"] = responce_oid.prettyPrint()

            return result
      
        else:
            resp_map = {response_oid.prettyPrint(): val.prettyPrint() for response_oid, val in varBinds}
            for oid in oid_nums:
                if oid in resp_map:
                    result["oids"][oid]["ok"] = True
                    v = resp_map[oid]
                    result["oids"][oid]["value"] = hex_to_text(v)
                    result["oids"][oid]["error"] = None
                    result["oids"][oid]["response_oid"] = oid
                else:
                    result["oids"][oid]["ok"] = False
                    result["oids"][oid]["value"] = None
                    result["oids"][oid]["error"] = "missing_in_response"
                    result["oids"][oid]["response_oid"] = None

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


    

