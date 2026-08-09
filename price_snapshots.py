from dataclasses import asdict
class DailyPriceStore:
    def __init__(self): self._games={}
    def add(self,game_id,price):
        row=asdict(price)
        if game_id not in self._games: self._games[game_id]={"first":row,"latest":row}
        else: self._games[game_id]["latest"]=row
    def get(self,game_id): return self._games[game_id]
    def export_rows(self):
        rows=[]
        for gid,s in self._games.items():
            rows.append({"game_id":gid,"snapshot":"first",**s["first"]})
            if s["latest"]!=s["first"]: rows.append({"game_id":gid,"snapshot":"latest",**s["latest"]})
        return rows
