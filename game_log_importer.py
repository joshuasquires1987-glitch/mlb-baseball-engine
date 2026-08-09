from history_provenance import HistoryField,PitchingHistoryRow

def innings_to_outs(ip):
    # Baseball notation: 5.2 = 5 innings + 2 outs, not 5.2 decimal innings.
    s=str(ip)
    if "." in s:
        whole,frac=s.split(".",1)
        frac=int(frac)
    else:
        whole,frac=s,0
    if frac not in (0,1,2):
        raise ValueError(f"Invalid baseball innings notation: {ip}")
    return int(whole)*3+frac

def import_pitching_row(date,ip,runs_allowed,batters_faced=None,
                        source_name="unknown",source_url=None):
    outs=HistoryField(float(innings_to_outs(ip)),"exact",source_name,source_url)
    runs=HistoryField(float(runs_allowed),"exact",source_name,source_url)
    if batters_faced is None:
        bf=HistoryField(float("nan"),"estimated",source_name,source_url)
    else:
        bf=HistoryField(float(batters_faced),"exact",source_name,source_url)
    return PitchingHistoryRow(str(date),outs,runs,bf)
