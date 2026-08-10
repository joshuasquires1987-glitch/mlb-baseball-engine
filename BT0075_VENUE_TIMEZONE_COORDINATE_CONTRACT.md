# BT-0075 Venue Timezone by Coordinates

BT-0074 proved that MLB's plain venue records do not reliably expose
a timezone offset.

BT-0075 replaces that assumption.

Pipeline:
1. Fetch venue with MLB location hydration.
2. Read MLB latitude/longitude.
3. Convert coordinates to an IANA timezone using `timezonefinder`.
4. Store the IANA timezone in the registry, not a fixed UTC offset.
5. At each historical game timestamp, resolve the correct UTC offset
   using Python `zoneinfo`.

Why this is necessary:
A fixed offset is seasonally wrong for venues observing daylight saving
time. `America/New_York` is UTC-4 in summer and UTC-5 in winter.

No model weights are changed.
No timezone is guessed manually.
Missing coordinates or failed timezone lookup remain hard errors.
