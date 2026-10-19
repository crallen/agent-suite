import unittest

from pricing import invoice_total_cents, line_total_cents


class LineTotalTest(unittest.TestCase):
    def test_below_bulk_threshold_pays_full_price(self):
        self.assertEqual(line_total_cents(250, 9), 2250)

    def test_order_at_bulk_threshold_gets_discount(self):
        self.assertEqual(line_total_cents(250, 10), 2250)

    def test_order_above_bulk_threshold_gets_discount(self):
        self.assertEqual(line_total_cents(250, 12), 2700)


class InvoiceTotalTest(unittest.TestCase):
    def test_small_invoice_pays_flat_shipping(self):
        self.assertEqual(invoice_total_cents([(250, 2)]), 999)

    def test_large_invoice_ships_free(self):
        self.assertEqual(invoice_total_cents([(1000, 3), (2500, 1)]), 5500)


if __name__ == "__main__":
    unittest.main()
