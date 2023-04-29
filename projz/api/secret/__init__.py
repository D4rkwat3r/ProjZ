from dill import loads
from types import ModuleType
from os import sep
from os import path
from base64 import b85decode

secret_functions = ModuleType("secret_functions")
local_secrets_initialized = False

with open(f"{path.dirname(__file__)}{sep}data.txt", "r") as file:
    try:
        exec(loads(b85decode(bytes())), secret_functions.__dict__)
        local_secrets_initialized = True
    except: print(f"ProjZ.py warning: Failed to initialize the local signature and device id generators, "
                  f"the library will use RPC functions. Perhaps your Python version "
                  f"does not meet the recommended 3.9.\n")
