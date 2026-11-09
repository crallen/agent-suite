"""HTTP routes: check the request shape, call the service, map the result to a response."""

import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler

from allowlist import is_allowed_ip
from service import OrderAlreadyCanceled, OrderNotFound

ORDER_PATH = re.compile(r"^/orders/(\d+)$")
CANCEL_PATH = re.compile(r"^/orders/(\d+)/cancel$")


def route(service, method, path, body, client_ip):
    if method == "POST" and path == "/orders":
        return create_order(service, body)
    if method == "GET" and (match := ORDER_PATH.match(path)):
        return get_order(service, int(match[1]))
    if method == "POST" and (match := CANCEL_PATH.match(path)):
        return cancel_order(service, int(match[1]), client_ip)
    return HTTPStatus.NOT_FOUND, {"error": "not found"}


def create_order(service, body):
    customer_email = body.get("customer_email")
    amount_cents = body.get("amount_cents")
    if not isinstance(customer_email, str) or "@" not in customer_email:
        return HTTPStatus.BAD_REQUEST, {"error": "customer_email must be an email address"}
    if not isinstance(amount_cents, int) or amount_cents <= 0:
        return HTTPStatus.BAD_REQUEST, {"error": "amount_cents must be a positive integer"}
    return HTTPStatus.CREATED, service.place_order(customer_email, amount_cents)


def get_order(service, order_id):
    try:
        return HTTPStatus.OK, service.get_order(order_id)
    except OrderNotFound:
        return HTTPStatus.NOT_FOUND, {"error": "order not found"}


def cancel_order(service, order_id, client_ip):
    if not is_allowed_ip(client_ip):
        return HTTPStatus.FORBIDDEN, {"error": "forbidden"}
    try:
        return HTTPStatus.OK, service.cancel_order(order_id)
    except OrderNotFound:
        return HTTPStatus.NOT_FOUND, {"error": "order not found"}
    except OrderAlreadyCanceled:
        return HTTPStatus.CONFLICT, {"error": "order already canceled"}


def make_request_handler(service):
    class OrderRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self._dispatch()

        def do_POST(self):
            self._dispatch()

        def _dispatch(self):
            length = int(self.headers.get("Content-Length") or 0)
            try:
                body = json.loads(self.rfile.read(length) or b"{}")
            except json.JSONDecodeError:
                body = None
            if not isinstance(body, dict):
                return self._send(HTTPStatus.BAD_REQUEST, {"error": "body must be a JSON object"})
            status, payload = route(service, self.command, self.path, body, self.client_address[0])
            self._send(status, payload)

        def _send(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return OrderRequestHandler
