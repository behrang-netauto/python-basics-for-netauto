
#Batch_GET_SNMP

import asyncio
from typing import Any, Sequence, Tuple, NamedTuple, AsyncIterator
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    UsmUserData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd,
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
class SnmpPduError(RuntimeError): ...


async def snmp_get_sysdescr(target_ip: str, oids: Sequence[str]) -> AsyncIterator[SnmpTupleResult]:
    transport = await UdpTransportTarget.create((target_ip, 161), timeout=5, retries=1)
    oid_types = [ObjectType(ObjectIdentity(oid_num)) for oid_num in oids]

    result = await get_cmd(
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

def raise_snmp_error(errInd: Any, errStat: Any, errIdx: int, varBinds: Sequence, oids: Sequence[str]):
    if errInd:
            raise SnmpEngineError(str(errInd))
    if errStat:
            idx0 = int(errIdx) - 1 if errIdx else None
            bad_oid = oids[idx0] if (idx0 is not None and 0 <= idx0 < len(oids)) else "?"
            raise SnmpPduError(f"{errStat} at {bad_oid}")    
    
async def main() -> None:

    target_ip = "192.168.2.55"
    oids = ["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.2.0", "1.3.6.1.2.1.1.3.0"]

    async for errInd, errStat, errIdx, varBinds in snmp_get_sysdescr(target_ip, oids):

        try:
            raise_snmp_error(errInd, errStat, errIdx, varBinds, oids)
        except SnmpEngineError as e:
            print("SNMP failed/Transport error:", e)
            return
        except SnmpPduError as e:
            for oid in oids:
                async for errInd, errStat, errIdx, varBinds in snmp_get_sysdescr(target_ip, [oid]):
                    try:
                        raise_snmp_error(errInd, errStat, errIdx, varBinds, [oid])
                    except SnmpPduError as e:
                        print("PDU error:", e)
                    except SnmpEngineError as e:
                        print("SNMP failed/Transport error:", e)
                    else:
                        for resp_oid, val in varBinds:
                            print(f"{resp_oid.prettyPrint()} = {val.prettyPrint()}")
        else:
            for resp_oid, val in varBinds:
                print(f"{resp_oid.prettyPrint()} = {val.prettyPrint()}")
        
if __name__ == "__main__":
    asyncio.run(main())



    
