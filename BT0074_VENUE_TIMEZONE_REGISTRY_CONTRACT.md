# BT-0074 Venue Timezone Registry Builder

Purpose:
Populate `venue_timezone_registry.json` directly from MLB venue metadata.

Rules:
- venue IDs come from the audited historical schedule
- timezone offsets come from MLB's venue object
- no hand-entered stadium offsets
- no default timezone
- missing MLB timezone metadata is an error
- every used venue must be registered before the registry is considered complete
- source provenance is stored
- this is data infrastructure only and does not alter model weights

Expected audit impact:
- `venue_timezone` missing count should fall from 2463 toward zero
- once venue offsets exist, prior schedule travel-state reconstruction can begin working after each team's first observed game
- the first observed game for each team may still lack prior-state history by design
