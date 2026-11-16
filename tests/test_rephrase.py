import json
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from generate_robust import check, variants_of  # noqa: E402

from msep.benchmark.parsing import ParseError  # noqa: E402
from msep.benchmark.rephrase import KINDS, _SentenceParser, say  # noqa: E402
from msep.controllers.extraction_v3 import INSTRUCTIONS_V3  # noqa: E402
from msep.controllers.llm_extractor import INSTRUCTIONS_V2  # noqa: E402
from msep.world.constraints import And, Iff, Implies, Not, Or, Var, evaluate  # noqa: E402


def _train(n=40):
    out = []
    with open(ROOT / "data" / "generated" / "pool_v3" / "instances.jsonl") as f:
        for line in f:
            r = json.loads(line)
            if r["split"] == "train":
                out.append(r)
    return random.Random(0).sample(out, n)


def test_variants_preserve_the_state():
    for rec in _train():
        vs = variants_of(rec)
        assert [v["robust"]["kind"] for v, _ in vs] == list(KINDS)
        for v, blocks in vs:
            c = check(rec, v, blocks)
            assert c["inverse_exact"] and c["names_present"] and c["differs_from_canonical"], (v["instance_id"], c)
            assert v["oracle"] == rec["oracle"] and v["state"] == rec["state"]
            assert c["benchmark_parser_exact"] == (v["robust"]["kind"] == "reorder")


def test_sentences_round_trip_random_formulas():
    rng = random.Random(1)
    names = {0: "Q", 1: "F1", 2: "F2", 3: "K1"}
    index = {v: k for k, v in names.items()}

    def rand(depth):
        if depth == 0 or rng.random() < 0.3:
            v = Var(rng.randrange(4))
            return Not(v) if rng.random() < 0.4 else v
        k = rng.randrange(5)
        if k == 0:
            return Not(rand(depth - 1))
        if k in (1, 2):
            return (And if k == 1 else Or)(tuple(rand(depth - 1) for _ in range(rng.randrange(2, 4))))
        return (Implies if k == 3 else Iff)(rand(depth - 1), rand(depth - 1))

    for _ in range(400):
        f = rand(3)
        for tv in (("is true", "is false"), ("holds", "does not hold")):
            g = _SentenceParser(say(f, names, rng, tv), index).parse()
            for bits in range(16):
                asg = {i: bool(bits >> i & 1) for i in range(4)}
                assert evaluate(f, asg) == evaluate(g, asg)


def test_sentence_parser_rejects_canonical_notation():
    with pytest.raises(ParseError):
        _SentenceParser("if F1 then not K1", {"F1": 1, "K1": 2}).parse()


def test_v3_prompt_keeps_the_v2_layout():
    layout = INSTRUCTIONS_V2[INSTRUCTIONS_V2.index("Use exactly this JSON layout"):]
    assert INSTRUCTIONS_V3.endswith(layout) and "translate it faithfully" in INSTRUCTIONS_V3


def test_robust_jobs_use_their_own_pools():
    import run_robust
    rec = _train(1)[0]
    items = [v for v, _ in variants_of(rec)]
    pools = {c: {j.pool for j in run_robust.jobs_for(items, c)} for c in ("a", "s1", "s3", "s3v2", "s3v3")}
    assert pools == {"a": {"plan_rb"}, "s1": {"plan_rbs1"}, "s3": {"extract_rb"}, "s3v2": {"extract_rbv2"}, "s3v3": {"extract_rbv3"}}
    assert all(j.prompt.startswith(i["prompt_text"]) for c in pools for j, i in zip(run_robust.jobs_for(items, c), items))
