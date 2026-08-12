from live_manifest_sources import (
    feed_venue_coordinates,
    venue_coordinates,
)


def test_venue_coordinates_from_default_coordinates():
    payload = {
        "venues": [{
            "location": {
                "defaultCoordinates": {
                    "latitude": 40.1,
                    "longitude": -73.9,
                }
            }
        }]
    }
    assert venue_coordinates(payload) == (40.1, -73.9)


def test_feed_venue_coordinates_from_location():
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
    assert feed_venue_coordinates(feed) == (40.8296, -73.9262)
