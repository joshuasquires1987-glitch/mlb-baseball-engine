from dataclasses import dataclass,field
from validation_metrics import brier,log_loss
from segmentation import edge_bucket,price_band,favorite_underdog,uncertainty_band

@dataclass
class ValidationTracker:
    rows:list=field(default_factory=list)

    def add_game(self,game_id,model_version,model_prob,outcome,decimal_odds=None,
                 selected_side="home",home_away="home",confidence=0.0,
                 starter_context="unknown",clv_pp_value=None,stake_cad=None,pnl_cad=None):
        row={
            "game_id":game_id,
            "model_version":model_version,
            "model_prob":float(model_prob),
            "outcome":int(outcome),
            "brier":brier(model_prob,outcome),
            "log_loss":log_loss(model_prob,outcome),
            "selected_side":selected_side,
            "home_away":home_away,
            "confidence":float(confidence),
            "uncertainty_band":uncertainty_band(confidence),
            "starter_context":starter_context,
            "decimal_odds":decimal_odds,
            "clv_pp":clv_pp_value,
            "stake_cad":stake_cad,
            "pnl_cad":pnl_cad,
        }
        if decimal_odds is not None:
            from validation_metrics import predicted_edge_pp
            edge=predicted_edge_pp(model_prob,decimal_odds)
            row.update({
                "predicted_edge_pp":edge,
                "edge_bucket":edge_bucket(edge),
                "price_band":price_band(decimal_odds),
                "favorite_underdog":favorite_underdog(decimal_odds),
            })
        self.rows.append(row)
        return row

    def summary(self,model_version=None):
        rows=[r for r in self.rows if model_version is None or r["model_version"]==model_version]
        if not rows:
            return {"n":0}
        out={
            "n":len(rows),
            "brier":sum(r["brier"] for r in rows)/len(rows),
            "log_loss":sum(r["log_loss"] for r in rows)/len(rows),
            "wins":sum(r["outcome"] for r in rows),
            "win_rate":sum(r["outcome"] for r in rows)/len(rows),
            "avg_model_probability":sum(r["model_prob"] for r in rows)/len(rows),
        }
        odds_rows=[r for r in rows if r.get("decimal_odds") is not None]
        if odds_rows:
            from validation_metrics import intact_implied_probability
            out["avg_posted_implied_probability"]=sum(intact_implied_probability(r["decimal_odds"]) for r in odds_rows)/len(odds_rows)
            out["avg_predicted_edge_pp"]=sum(r["predicted_edge_pp"] for r in odds_rows)/len(odds_rows)
        clv=[r["clv_pp"] for r in rows if r.get("clv_pp") is not None]
        if clv: out["avg_clv_pp"]=sum(clv)/len(clv)
        wager_rows=[r for r in rows if r.get("stake_cad") is not None and r.get("pnl_cad") is not None]
        if wager_rows:
            st=sum(float(r["stake_cad"]) for r in wager_rows)
            pnl=sum(float(r["pnl_cad"]) for r in wager_rows)
            out["dollars_staked"]=st
            out["pnl_cad"]=pnl
            out["roi"]=pnl/st if st else None
        return out

    def segment(self,key,model_version=None):
        groups={}
        rows=[r for r in self.rows if model_version is None or r["model_version"]==model_version]
        for r in rows:
            val=r.get(key,"unknown")
            groups.setdefault(val,[]).append(r)
        return {k:{
            "n":len(v),
            "brier":sum(x["brier"] for x in v)/len(v),
            "log_loss":sum(x["log_loss"] for x in v)/len(v),
            "win_rate":sum(x["outcome"] for x in v)/len(v)
        } for k,v in groups.items()}
