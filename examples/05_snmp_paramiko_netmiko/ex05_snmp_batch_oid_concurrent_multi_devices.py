
#Batch_GET_SNMP_Concurrent_Multi_Devices_JSON(output)

'''

MultiDeviceRunResult = {
  "192.168.2.55": {...SnmpRunResult...},
  "192.168.2.56": {...SnmpRunResult...},
}

SnmpRunResult = {
  "transport_error": None,
  "oids": {
     "1.3.6...1.0": {"ok": True,  "value": "...", "error": None, "response_oid": "1.3.6...1.0"},
     "1.3.6...2.0": {"ok": False, "value": None, "error": "noAccess", "response_oid": "1.3.6...2.0"},
  }
}

'''
import json
import asyncio
from typing import Any, Sequence, Tuple, NamedTuple, AsyncIterator, TypedDict, TypeAlias
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd as pysnmp_get_cmd,
    walk_cmd,
    USM_AUTH_HMAC96_MD5,
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

MultiDeviceRunResult: TypeAlias = dict[str, SnmpRunResult]


async def get_cmd(ip: str, oid_nums: Sequence[str]) -> AsyncIterator[SnmpTupleResult]:
    transport = await UdpTransportTarget.create((ip, 161), timeout=5, retries=1)
    oid_types = [ObjectType(ObjectIdentity(oid_num)) for oid_num in oid_nums]

    result = await pysnmp_get_cmd(
        SnmpEngine(),
        UsmUserData(
            userName="SNMPUser1",
            authKey="AUTHPass1",
            privKey="PRIVPass1",
            authProtocol=USM_AUTH_HMAC96_MD5,
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
    
async def snmp_get_device(ip: str, oid_nums: Sequence[str]) -> SnmpRunResult:

    result: SnmpRunResult = {
        "transport_error": None,
        "oids": {oid: {"ok": False, "value": None, "error": None, "response_oid": None} for oid in oid_nums},
    }

    async for errInd, errStat, errIdx, varBinds in get_cmd(ip, oid_nums):

        try:
            raise_snmp_error(errInd, errStat, errIdx, varBinds, oid_nums)
        
        except SnmpEngineError as e:
            print("SNMP failed/Transport error:", e)
            result["transport_error"] = str(e)
            return result
        
        except SnmpPduError as e:
            print("Bath PDU error:", e, "| bad_oid =", e.bad_oid)

            for oid in oid_nums:
                async for errInd, errStat, errIdx, varBinds in get_cmd(ip, [oid]):
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
                            result["oids"][oid]["value"] = val.prettyPrint()
                            result["oids"][oid]["error"] = None
                            result["oids"][oid]["response_oid"] = responce_oid.prettyPrint()

            return result
      
        else:
            resp_map = {responce_oid.prettyPrint(): val.prettyPrint() for responce_oid, val in varBinds}
            for oid in oid_nums:
                if oid in resp_map:
                    result["oids"][oid]["ok"] = True
                    result["oids"][oid]["value"] = resp_map[oid]
                    result["oids"][oid]["error"] = None
                    result["oids"][oid]["response_oid"] = oid
                else:
                    result["oids"][oid]["ok"] = False
                    result["oids"][oid]["value"] = None
                    result["oids"][oid]["error"] = "missing_in_response"
                    result["oids"][oid]["response_oid"] = None

            return result
    
async def run_concurrent(
        target_ips: Sequence[str], 
        oid_nums: Sequence[str], 
        limit: int=50
    ) -> MultiDeviceRunResult:

    sem = asyncio.Semaphore(limit)

    async def bounded(ip: str) -> tuple[str, SnmpRunResult]:
        async with sem:
            try:    
                return ip, await snmp_get_device(ip, oid_nums)
            except Exception as e:
                return ip, {"transport_error" : str(e),
                            "oids": {oid: {"ok": False, "value": None, "error": str(e), "response_oid": None} for oid in oid_nums}}

    #pairs = await asyncio.gather(*(bounded(ip) for ip in target_ips))
    tasks = [asyncio.create_task(bounded(ip)) for ip in target_ips]
    pairs = await asyncio.gather(*tasks)
    return {ip: res for ip, res in pairs}
'''
pairs = 
[
  ("192.168.2.55", {"transport_error": None, "oids": {...}}),
  ("192.168.2.56", {"transport_error": "timeout", "oids": {...}}),
  ....
]
return = 
{
  "192.168.2.55": {...},
  "192.168.2.56": {...},
}
'''
async def main() -> MultiDeviceRunResult:
    target_ips = [
        "192.168.2.55",
        "192.168.2.56",
    ]
    oid_nums = [
        "1.3.6.1.2.1.1.1.0", 
        "1.3.6.1.2.1.1.2.0", 
        "1.3.6.1.2.1.1.3.0"
    ]
    return await run_concurrent(target_ips, oid_nums)

if __name__ == "__main__":
    out = asyncio.run(main())
    print(json.dumps(out, indent=2))
    with open("snmp_concurrent_devices.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)




    
