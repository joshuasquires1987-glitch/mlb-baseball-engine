# Real Game-State Assembler Contract

The assembler bridges raw historical baseball tables and the model feature builder.

It:
- accepts target matchup metadata plus verified starter IDs
- extracts strictly prior starter histories
- extracts strictly prior team and relief histories
- calculates starter talent and expected depth
- calculates team/offense/defense and bullpen states
- builds `PregameFacts`
- forwards `PregameFacts` to the feature builder

No sportsbook odds are accepted in this layer.
Any starter change requires fresh assembly and a downstream rerun.
