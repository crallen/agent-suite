"""Entry point: wire storage, service, and routes, then serve."""

import os
from http.server import HTTPServer

from handlers import make_request_handler
from repo import OrderRepo, connect
from service import OrderService


def main():
    conn = connect(os.environ.get("ORDERS_DB", "orders.db"))
    service = OrderService(OrderRepo(conn))
    server = HTTPServer(("localhost", 8000), make_request_handler(service))
    server.serve_forever()


if __name__ == "__main__":
    main()
