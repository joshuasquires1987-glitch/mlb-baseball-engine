OFFICIAL_MLB_SOURCES = {
    "schedule": "https://www.mlb.com/schedule/{date}",
    "probable_pitchers": "https://www.mlb.com/probable-pitchers/{date}",
    "starting_lineups": "https://www.mlb.com/starting-lineups/{date}",
    "injuries": "https://www.mlb.com/injury-report",
}

TEAM_CODES = {
    "ATH":"ATH","AZ":"AZ","ATL":"ATL","BAL":"BAL","BOS":"BOS","CHC":"CHC",
    "CIN":"CIN","CLE":"CLE","COL":"COL","CWS":"CWS","DET":"DET","HOU":"HOU",
    "KC":"KC","LAA":"LAA","LAD":"LAD","MIA":"MIA","MIL":"MIL","MIN":"MIN",
    "NYM":"NYM","NYY":"NYY","PHI":"PHI","PIT":"PIT","SD":"SD","SEA":"SEA",
    "SF":"SF","STL":"STL","TB":"TB","TEX":"TEX","TOR":"TOR","WSH":"WSH",
}

def normalize_team_code(code):
    c = str(code).strip().upper()
    if c not in TEAM_CODES:
        raise ValueError(f"Unknown MLB team code: {code}")
    return TEAM_CODES[c]
