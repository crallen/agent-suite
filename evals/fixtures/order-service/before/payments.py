"""Client for the payment provider's HTTP API."""

import json
import urllib.request


class PaymentsClient:
    def __init__(self, base_url, api_key):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key

    def refund(self, order_id, amount, timeout=None):
        """Refund `amount` cents of an order. Returns the provider's refund record."""
        request = urllib.request.Request(
            f"{self._base_url}/refunds",
            data=json.dumps({"order_id": order_id, "amount": amount}).encode(),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
