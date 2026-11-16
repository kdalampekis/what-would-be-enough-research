"""Generate benchmark families as JSONL records (formal state, latent world, oracle labels, rendering).

    python experiments/generate_benchmark.py --families 100 --out data/generated/pilot_v0

Deterministic in --seed-offset. Splits are assigned per family. No model calls.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from pathlib import Path

from msep.benchmark.families import generate_family
from msep.benchmark.template_v3 import generate_family_v3
from msep.benchmark.rendering import make_rendering, render_state
from msep.benchmark.schemas import instance_record
from msep.benchmark.splits import split_of

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", type=int, default=100)
    ap.add_argument("--seed-offset", type=int, default=0)
    ap.add_argument("--out", default=str(ROOT / "data" / "generated" / "pilot_v0"))
    ap.add_argument("--sample-out", default=None, help="also write the first 2 families here (small, committable)")
    ap.add_argument("--template", choices=("v2", "v3"), default="v2")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    counts, splits, classes = Counter(), Counter(), Counter()
    sample = []
    with open(out / "instances.jsonl", "w") as fh:
        for k in range(args.families):
            seed = args.seed_offset + k
            fam = generate_family(seed) if args.template == "v2" else generate_family_v3(seed)
            split = split_of(fam.family_id)
            rendering = make_rendering(fam.siblings[0].instance.state, random.Random(f"render:{seed}"),
                                       shuffle_rules=args.template == "v3")
            for j, sib in enumerate(fam.siblings, 1):
                text = render_state(sib.instance.state, rendering)
                rec = instance_record(
                    family_id=fam.family_id, instance_id=f"{fam.family_id}-S{j:02d}", sibling_type=sib.sibling_type,
                    split=split, instance=sib.instance, oracle=sib.oracle, transformation=sib.transformation,
                    rendering={**rendering.to_json(), "action_alias": dict(rendering.action_alias)},
                    prompt_text=text, notes=sib.notes)
                rec["base_params"] = {k2: v for k2, v in fam.base_params.items() if k2 != "rejections"}
                fh.write(json.dumps(rec) + "\n")
                counts[sib.sibling_type] += 1
                classes[rec["oracle"]["resource_class"]] += 1
                if k < 2:
                    sample.append(rec)
            splits[split] += 1
    manifest = {"template": args.template, "families": args.families, "seed_offset": args.seed_offset,
                "instances": sum(counts.values()), "sibling_types": dict(counts),
                "resource_classes": dict(classes), "families_per_split": dict(splits)}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    if args.sample_out:
        sp = Path(args.sample_out)
        sp.mkdir(parents=True, exist_ok=True)
        with open(sp / "sample_instances.jsonl", "w") as fh:
            for rec in sample:
                fh.write(json.dumps(rec) + "\n")
        (sp / "sample_prompt.txt").write_text(sample[3]["prompt_text"] + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
