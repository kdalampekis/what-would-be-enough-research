"""Family-level splits. Every sibling of a family lands in the same split.

The split is a deterministic function of the family id alone, so it cannot
depend on row order and siblings cannot be separated.
"""

from __future__ import annotations

import hashlib

SPLITS = (("train", 0.6), ("dev", 0.2), ("test", 0.2))


def split_of(family_id: str, salt: str = "msep-split-v1") -> str:
    h = int(hashlib.sha256(f"{salt}:{family_id}".encode()).hexdigest()[:12], 16) / float(16 ** 12)
    acc = 0.0
    for name, share in SPLITS:
        acc += share
        if h < acc:
            return name
    return SPLITS[-1][0]
