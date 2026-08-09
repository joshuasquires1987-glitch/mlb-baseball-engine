import json, pandas as pd
from matchup_definition import MatchupDefinition
from run_nym_pit_backfill import run as run_backfill
from run_end_to_end_proof import run as run_proof
def main():
    bundle=run_backfill("nym_pit_exact_history_bundle.json")
    matchup=MatchupDefinition("NYM@PIT-2026-08-09",pd.Timestamp("2026-08-09"),"PIT","NYM","683003","640455",True,True,False,True,True,True,.10,0.,0.,0.,0.,False)
    proof=run_proof(bundle,matchup,"nym_pit_probability_proof.json",repo_root=".")
    print(json.dumps(proof,indent=2))
    if proof["prices_seen"]: raise RuntimeError("Market leakage detected.")
    return proof
if __name__=="__main__": main()
