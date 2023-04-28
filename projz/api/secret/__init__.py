from marshal import load
from types import ModuleType
from sys import version_info


secret_functions = ModuleType("secret_functions")

with open("projz/api/secret/secret.pyc", "rb") as file:
    file.seek(16 if version_info.major == 3 and version_info.minor >= 7 else 12)
    exec(load(file), secret_functions.__dict__)
