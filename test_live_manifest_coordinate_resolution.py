from live_manifest_generator import resolve_venue_coordinates


def test_coordinate_fallback_uses_live_feed_when_venue_endpoint_missing():
    feed = {
        "gameData": {
            "venue": {
                "location": {
                    "defaultCoordinates": {
                        "latitude": 40.8296,
                        "longitude": -73.9262,
                    }
                }
            }
        }
    }
    coords, source = resolve_venue_coordinates(
        {"venue_id": "3313"},
        feed,
        {"venues": [{"id": 3313, "name": "Yankee Stadium"}]},
    )
    assert coords == (40.8296, -73.9262)
    assert source == "mlb_live_feed"
