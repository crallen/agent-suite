# Order service: refunds, allowlist tests, email rename

Three independent tasks. Each can ship on its own.

## Tasks

1. **Refund canceled orders.** Canceling an order only flips its status today, and
   support refunds the customer by hand in the payment provider's dashboard. When
   an order is canceled, refund its full amount through `PaymentsClient`
   (`payments.py`). If the refund fails, the order stays open and the cancel
   request returns an error, so support can retry it. `app.py` builds the client
   from the `PAYMENTS_URL` and `PAYMENTS_API_KEY` environment variables.

2. **Test the cancel allowlist.** `POST /orders/<id>/cancel` only accepts callers
   from the networks in `ALLOWED_NETWORKS`, and `is_allowed_ip` (`allowlist.py`)
   has no tests. Add tests for it: one address it blocks and one it allows.

3. **Rename `customer_email` to `email`.** Every other service calls this field
   `email`, and the mismatch keeps causing mapping bugs. Rename `customer_email`
   to `email` on orders: the stored column, the repo and service, and the field
   the API accepts and returns.
