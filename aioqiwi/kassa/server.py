import typing
import logging
import ipaddress

from aiohttp import web

from .types import updates
from .crypto import hmac_key
from ..server import BaseWebHookView
from ..requests import deserialize

logger = logging.getLogger("aioqiwi")

logger.info(f"Deserialization tool: {deserialize.__name__}")

DEFAULT_QIWI_BILLS_WEBHOOK_PATH = "/webhooks/qiwi/bills/"
DEFAULT_QIWI_ROUTER_NAME = "QIWI_BILLS"

RESPONSE_TIMEOUT = 55

QIWI_IP_1 = ipaddress.IPv4Network("79.142.16.0/20")
QIWI_IP_2 = ipaddress.IPv4Network("91.232.230.0/23")
QIWI_IP_3 = ipaddress.IPv4Network("195.189.100.0/22")

allowed_ips = {QIWI_IP_1, QIWI_IP_2, QIWI_IP_3}


def _check_ip(ip: str) -> bool:
    address = ipaddress.IPv4Address(ip)
    return address in allowed_ips


def allow_ip(*ips: typing.Union[str, ipaddress.IPv4Network, ipaddress.IPv4Address]):
    for ip in ips:
        if isinstance(ip, ipaddress.IPv4Address):
            allowed_ips.add(ip)
        elif isinstance(ip, str):
            allowed_ips.add(ipaddress.IPv4Address(ip))
        elif isinstance(ip, ipaddress.IPv4Network):
            allowed_ips.update(ip.hosts())
        else:
            raise ValueError


allow_ip(*allowed_ips)


class QiwiBillServerWebView(BaseWebHookView):
    _check_ip = staticmethod(_check_ip)

    def hash_validator(self, update):
        sha256 = self.request.headers.get("X-Api-Signature-SHA256")
        secret = self.request.app.get("_secret_key")

        if (
            hmac_key(
                secret,
                update.bill.Amount,
                update.bill.Status,
                update.bill.bill_id,
                update.bill.site_id,
            )
            != sha256
        ):
            raise web.HTTPBadRequest()

    async def parse_update(self) -> updates.Notification:
        """
        Deserialize update and create new update class
        :return: :class:`updated.QiwiUpdate`
        """
        data = await self.request.json()
        return updates.Notification(**deserialize(data))

    async def post(self):
        """
        Process POST request with validating and further deserialization and resolving
        """
        self.validate_ip()

        update = await self.parse_update()

        self.hash_validator(update)

        await self._resolve_update(update)

        return web.json_response(data={"error": "0"}, status=200)

    _app_key_check_ip = "_qiwi_kassa_check_ip"
    _app_key_dispatcher = "_qiwi_kassa_dispatcher"


def setup(secret_key, dispatcher, app: web.Application, path=None):
    app["_secret_key"] = secret_key
    app[QiwiBillServerWebView._app_key_check_ip] = _check_ip
    app[QiwiBillServerWebView._app_key_dispatcher] = dispatcher
    app.router.add_view(
        path or DEFAULT_QIWI_BILLS_WEBHOOK_PATH,
        QiwiBillServerWebView,
        name=DEFAULT_QIWI_ROUTER_NAME,
    )
