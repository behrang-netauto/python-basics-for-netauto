
#SingleـGET_SNMP

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


async def snmp_get_sysdescr(target_ip: str, oid_num: str) -> AsyncIterator[SnmpTupleResult]:
    transport = await UdpTransportTarget.create((target_ip, 161), timeout=2, retries=1)
    oid_type = ObjectType(ObjectIdentity(oid_num))

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
        oid_type,
        lookupMib=False,
    )

    yield SnmpTupleResult(*result)

def raise_snmp_error(errInd: Any, errStat: Any, errIdx: int, varBinds: Sequence):
    if errInd:
            raise SnmpEngineError(str(errInd))
    if errStat:
            bad_oid = varBinds[int(errIdx) - 1][0] if errIdx else "?"
            raise SnmpPduError(f"{errStat} at {bad_oid}")    
    
async def main() -> None:

    target_ip = "192.168.2.55"
    oid_num = "1.3.6.1.2.1.1.1.0"

    async for errInd, errStat, errIdx, varBinds in snmp_get_sysdescr(target_ip, oid_num):

        try:
            raise_snmp_error(errInd, errStat, errIdx, varBinds)
        except (SnmpEngineError, SnmpPduError) as e:
             print("SNMP failed:", e)
        else:
            for oid, val in varBinds:
                print(f"{oid.prettyPrint()} = {val.prettyPrint()}")
        
if __name__ == "__main__":
    asyncio.run(main())



    