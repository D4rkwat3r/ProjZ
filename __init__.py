from .client import ZClient
from .internal.api.z_api_request import ZApiRequest
from .internal.models.message import Message
from .internal.exceptions.objects.captcha_caught import CaptchaCaught
from httpx import Client

__version__ = "1.8.3"

__latest_version__ = Client().get("https://pypi.org/pypi/ProjZ.py/json").json()["info"]["version"]

if __latest_version__ != __version__:
    print(f"ProjZ.py updated to: {__latest_version__}, your version: {__version__}. Use 'pip install ProjZ.py -U'")
