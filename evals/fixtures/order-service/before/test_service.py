import unittest

from repo import OrderRepo, connect
from service import OrderAlreadyCanceled, OrderNotFound, OrderService


class OrderServiceTest(unittest.TestCase):
    def setUp(self):
        conn = connect()
        self.addCleanup(conn.close)
        self.service = OrderService(OrderRepo(conn))

    def test_placed_order_is_open(self):
        order = self.service.place_order("ada@example.com", 1500)
        self.assertEqual(order["status"], "open")
        self.assertEqual(order["amount_cents"], 1500)

    def test_get_unknown_order_raises_order_not_found(self):
        with self.assertRaises(OrderNotFound):
            self.service.get_order(999)

    def test_cancel_marks_order_canceled(self):
        order = self.service.place_order("ada@example.com", 1500)
        canceled = self.service.cancel_order(order["id"])
        self.assertEqual(canceled["status"], "canceled")

    def test_cancel_twice_raises_order_already_canceled(self):
        order = self.service.place_order("ada@example.com", 1500)
        self.service.cancel_order(order["id"])
        with self.assertRaises(OrderAlreadyCanceled):
            self.service.cancel_order(order["id"])

    def test_cancel_unknown_order_raises_order_not_found(self):
        with self.assertRaises(OrderNotFound):
            self.service.cancel_order(999)


if __name__ == "__main__":
    unittest.main()
