import dataclasses
import orjson
import typing
import struct
import uuid

@dataclasses.dataclass
class NetUser:
    name : str
    passw : str

@dataclasses.dataclass
class NetMessage:
    client_id : str
    main_data : str
    user : NetUser

res = orjson.dumps(NetMessage(client_id=str(uuid.uuid4()), main_data="dataa", user=NetUser("guy", "guy123")))
res = orjson.loads(res)
res = struct.pack(">I", len(res)) + res
print(s)