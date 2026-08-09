import json
from pathlib import Path
from proof_qualification import qualify_probability

def attach_qualification(proof_path, context, output_path=None):
    proof=json.loads(Path(proof_path).read_text())
    proof["qualification"]=qualify_probability(proof,context)
    out=Path(output_path or proof_path)
    out.write_text(json.dumps(proof,indent=2))
    return proof
