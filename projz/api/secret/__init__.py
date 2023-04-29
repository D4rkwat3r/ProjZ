from marshal import load
from types import ModuleType
from os import sep
from os import path

secret_functions = ModuleType("secret_functions")

with open(f"{path.dirname(__file__)}{sep}secret.pyc", "rb") as file:
    file.seek(16)
    exec(load(file), secret_functions.__dict__)
