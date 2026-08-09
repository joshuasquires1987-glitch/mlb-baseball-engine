from dataclasses import dataclass

@dataclass(frozen=True)
class PromotionGate:
    minimum_shadow_games:int=500
    require_zero_unresolved_integrity_failures:bool=True
    require_rc1_brier_no_worse:bool=True
    require_acceptable_calibration:bool=True
    require_no_catastrophic_segments:bool=True
    require_explicit_human_approval:bool=True

def review_status(shadow_games,unresolved_integrity_failures,
                  rc1_brier,v11_brier,calibration_ok,
                  catastrophic_segment_failure=False,
                  explicit_human_approval=False,
                  gate=PromotionGate()):
    checks={
        "sample_size":shadow_games>=gate.minimum_shadow_games,
        "integrity":unresolved_integrity_failures==0,
        "brier":rc1_brier<=v11_brier,
        "calibration":bool(calibration_ok),
        "segments":not catastrophic_segment_failure,
        "explicit_human_approval":bool(explicit_human_approval),
    }
    review_eligible=all(v for k,v in checks.items() if k!="explicit_human_approval")
    promoted=review_eligible and checks["explicit_human_approval"]
    return {
        "checks":checks,
        "review_eligible":review_eligible,
        "promoted":promoted,
        "automatic_promotion":False,
        "status":"PROMOTED" if promoted else ("ELIGIBLE_FOR_REVIEW" if review_eligible else "SHADOW_CONTINUES"),
    }
