from marshal import load
from types import ModuleType

secret_functions = ModuleType("secret_functions")

with open("projz/api/secret/secret.pyc", "rb") as file:
    file.seek(16)
    exec(load(file), secret_functions.__dict__)
