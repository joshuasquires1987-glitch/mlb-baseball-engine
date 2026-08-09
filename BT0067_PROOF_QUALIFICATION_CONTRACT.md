# BT-0067 Proof Qualification Gate

A successful blind probability calculation is not automatically a production-qualified betting probability.

A proof is qualified only when:
- prices were not seen before probability freeze
- probabilities are frozen
- starter integrity is green
- lineup integrity is green
- bullpen integrity is green
- weather integrity is green
- roster-news integrity is green
- park, weather, travel/rest, and platoon context values have verified/exact provenance

Yellow umpire status does not by itself block qualification because umpire is not a frozen v1.1 structural weight.

The first successful NYM@PIT artifact remains preserved as a pipeline proof. Its 57.6746% PIT production probability must not be passed to market/EV evaluation while lineup is yellow or required context remains unverified.

This gate changes no model weights and does not mutate the frozen probability.
