import base64
import bson
import struct
import msgpack


# Base64 encoded string from user
encoded_str = """
CoIECv8DCvwDCgwKAjEyEgZGb3RiYWwYvwYi6AMKGAoDeDQ0Eg1NZXppbsOhcm9kbsOtGgIxMhLLAwrIAwoGeHgxMjc4EhhLdmFsaWZpa2Fj
ZSBNUywgQ09OTUVCT0waA3g0NCqeAwjat4wBEhNCb2zDrXZpZSAtIEtvbHVtYmllIgcIgJSRwKcyKgg1MzYyNDY0NTLhAgg7Eg5IbGF2bsOt
IHPDoXpreRprCgsyZDIyMzUyODc5NRIGWsOhcGFzMlAI247LahIGWsOhcGFzGLGAASITCgk0ODgzOTA3OTUSATEdcT1KQCITCgk0ODgzOTA3
OTYSATAdSOFKQCITCgk0ODgzOTA3OTcSATIdUrgOQFgCYAIacAoLM2QyMjM1Mjg3OTYSB0R2b2p0aXAyVAjcjstqEgdEdm9qdGlwGLOAASIU
Cgk0ODgzOTA3OTESAjEwHRSuxz8iFAoJNDg4MzkwNzkyEgIxMh3D9ag/IhQKCTQ4ODM5MDc5MxICMDIdw/WoP1gBYAIabgoLNGQyMjM1Mjg3
OTcSElPDoXprYSBiZXogcmVtw616eTJHCN2Oy2oSElPDoXprYSBiZXogcmVtw616eRjPgAEiEwoJNDg4MzkwNzk0EgExHc3MDEAiEwoJNDg4
MzkwNzk4EgEyHXE9yj9YAWACOgZ4eDEyNzhQA2C/Bg==
"""

# Decode base64 string to binary data
decoded_bytes = base64.b64decode(encoded_str)

# Decode MessagePack data
unpacked_data = msgpack.unpackb(decoded_bytes)

print(unpacked_data)