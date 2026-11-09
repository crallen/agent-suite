"""Order rules. Knows nothing about HTTP or SQL; the repo is passed in."""


class OrderNotFound(Exception):
    pass


class OrderAlreadyCanceled(Exception):
    pass


class OrderService:
    def __init__(self, repo):
        self._repo = repo

    def place_order(self, customer_email, amount_cents):
        order_id = self._repo.create(customer_email, amount_cents)
        return self._repo.get(order_id)

    def get_order(self, order_id):
        order = self._repo.get(order_id)
        if order is None:
            raise OrderNotFound(order_id)
        return order

    def cancel_order(self, order_id):
        order = self.get_order(order_id)
        if order["status"] == "canceled":
            raise OrderAlreadyCanceled(order_id)
        self._repo.set_status(order_id, "canceled")
        return self._repo.get(order_id)
