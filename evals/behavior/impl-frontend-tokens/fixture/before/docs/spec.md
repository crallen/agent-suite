# Dashboard: sync status

## Tasks

1. **Sync status badge on Home.** People cannot tell whether the dashboard's
   numbers are current. Add a status badge to Home, under the heading: "Synced" in
   the accent color when the last sync succeeded, and an error variant reading
   "Sync failed" when it did not. Home takes a `syncStatus` prop, `"synced"` or
   `"error"`; App passes `"synced"` until the sync API exists.
