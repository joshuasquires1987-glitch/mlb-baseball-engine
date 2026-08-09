# BT-0062 Canonical Backfill + CI Proof

Execution upgrade:
- exact backfill now emits canonical home/away game rows and team-perspective rows
- the NYM-PIT proof command performs backfill -> readiness -> blind probability proof
- GitHub Actions runs the proof with network access and uploads the history/proof artifacts

The run fails closed on incomplete exact history, missing canonical rows, red integrity, or market leakage.
