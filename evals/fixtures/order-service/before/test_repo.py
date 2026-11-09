import sqlite3
import tempfile
import unittest
from pathlib import Path

from repo import OrderRepo, connect


class OrderRepoTest(unittest.TestCase):
    def setUp(self):
        conn = connect()
        self.addCleanup(conn.close)
        self.repo = OrderRepo(conn)

    def test_created_order_reads_back_open(self):
        order_id = self.repo.create("ada@example.com", 1500)
        self.assertEqual(
            self.repo.get(order_id),
            {"id": order_id, "customer_email": "ada@example.com", "amount_cents": 1500, "status": "open"},
        )

    def test_get_unknown_order_returns_none(self):
        self.assertIsNone(self.repo.get(999))

    def test_set_status_updates_the_order(self):
        order_id = self.repo.create("ada@example.com", 1500)
        self.repo.set_status(order_id, "canceled")
        self.assertEqual(self.repo.get(order_id)["status"], "canceled")

    def test_non_positive_amount_is_rejected_by_the_schema(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.create("ada@example.com", 0)

    def test_unknown_status_is_rejected_by_the_schema(self):
        order_id = self.repo.create("ada@example.com", 1500)
        with self.assertRaises(sqlite3.IntegrityError):
            self.repo.set_status(order_id, "shipped")


class MigrateTest(unittest.TestCase):
    def test_reconnecting_keeps_data_and_skips_applied_migrations(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "orders.db"
            first = connect(path)
            order_id = OrderRepo(first).create("ada@example.com", 1500)
            first.close()

            second = connect(path)
            self.assertEqual(OrderRepo(second).get(order_id)["amount_cents"], 1500)
            second.close()


if __name__ == "__main__":
    unittest.main()
