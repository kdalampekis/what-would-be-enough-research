# Linguistic robustness (dev, 18 families, 137 states, End-to-End)

All attempted; unparsed, invalid or failed = incorrect. Optimal-plan rate on resolvable states; `state` = extracted state exactly equal to the canonical state.

## adaption-qwen3.5-397b (frozen extraction: s3v2)

| wording | A native | B structured | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P parser optimal | EOP − A | EOP variant − canonical |
|---|---|---|---|---|---|---|---|---|---|
| canonical | 0.98 | 0.71 | 1.00 | 1.00 | | | 1.00 | | |
| lexical | 1.00 | 0.76 | 0.99 | 0.99 | 1.00 | 1.00 | 0.00 | -0.01 [-0.03, +0.00] | -0.01 [-0.03, +0.00] |
| syntax | 0.98 | 0.72 | 1.00 | 1.00 | 1.00 | 0.99 | 0.00 | +0.02 [+0.00, +0.05] | +0.00 [+0.00, +0.00] |
| reorder | 0.97 | 0.74 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.03 [+0.00, +0.08] | +0.00 [+0.00, +0.00] |
| prose | 0.99 | 0.73 | 1.00 | 1.00 | 0.99 | 0.99 | 0.00 | +0.01 [+0.00, +0.03] | +0.00 [+0.00, +0.00] |

Pooled over the four wordings: EOP − A +0.01 [-0.00, +0.03], one-sided p 0.0771, Holm p 0.1542; EOP-N − A +0.01 [-0.00, +0.03]; EOP − P +0.75 [+0.74, +0.75].

## adaption-qwen3.8-27b (frozen extraction: s3v2)

| wording | A native | B structured | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P parser optimal | EOP − A | EOP variant − canonical |
|---|---|---|---|---|---|---|---|---|---|
| canonical | 0.96 | 0.98 | 1.00 | 1.00 | | | 1.00 | | |
| lexical | 0.98 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | +0.02 [+0.00, +0.05] | +0.00 [+0.00, +0.00] |
| syntax | 0.98 | 0.97 | 1.00 | 0.99 | 1.00 | 0.99 | 0.00 | +0.02 [+0.00, +0.05] | +0.00 [+0.00, +0.00] |
| reorder | 0.96 | 0.97 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | +0.04 [+0.00, +0.11] | +0.00 [+0.00, +0.00] |
| prose | 0.95 | 0.99 | 0.99 | 0.99 | 1.00 | 0.99 | 0.00 | +0.04 [-0.01, +0.09] | -0.01 [-0.03, +0.00] |

Pooled over the four wordings: EOP − A +0.03 [+0.01, +0.06], one-sided p 0.0047, Holm p 0.014100000000000001; EOP-N − A +0.03 [+0.01, +0.06]; EOP − P +0.75 [+0.74, +0.75].

## adaption-deepseek-v4-flash (frozen extraction: s3v2)

| wording | A native | B structured | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P parser optimal | EOP − A | EOP variant − canonical |
|---|---|---|---|---|---|---|---|---|---|
| canonical | 0.97 | 0.92 | 1.00 | 1.00 | | | 1.00 | | |
| lexical | 0.96 | 0.88 | 0.99 | 0.98 | 0.88 | 0.87 | 0.00 | +0.03 [-0.01, +0.07] | -0.01 [-0.03, +0.00] |
| syntax | 0.98 | 0.98 | 0.81 | 0.81 | 0.97 | 0.98 | 0.00 | -0.17 [-0.25, -0.09] | -0.19 [-0.28, -0.11] |
| reorder | 0.93 | 0.97 | 1.00 | 1.00 | 0.99 | 0.97 | 1.00 | +0.07 [+0.03, +0.12] | +0.00 [+0.00, +0.00] |
| prose | 0.98 | 0.90 | 0.92 | 0.92 | 0.88 | 0.88 | 0.00 | -0.06 [-0.12, -0.01] | -0.08 [-0.14, -0.03] |

Pooled over the four wordings: EOP − A -0.03 [-0.06, +0.00], one-sided p 0.9836, Holm p 0.9836; EOP-N − A -0.03 [-0.07, +0.01]; EOP − P +0.68 [+0.65, +0.71].

## adaption-gemma-4-26b-a4b-it-schema (frozen extraction: s3)

| wording | A native | B structured | EOP optimal | EOP state | EOP-N optimal | EOP-N state | P parser optimal | EOP − A | EOP variant − canonical |
|---|---|---|---|---|---|---|---|---|---|
| canonical | 0.37 | 0.49 | 0.99 | 0.98 | | | 1.00 | | |
| lexical | 0.17 | 0.50 | 0.93 | 0.93 | 0.05 | 0.05 | 0.00 | +0.76 [+0.65, +0.87] | -0.06 [-0.11, -0.02] |
| syntax | 0.35 | 0.37 | 0.05 | 0.07 | 0.05 | 0.04 | 0.00 | -0.30 [-0.44, -0.17] | -0.94 [-0.98, -0.90] |
| reorder | 0.43 | 0.25 | 0.99 | 0.99 | 0.25 | 0.26 | 1.00 | +0.56 [+0.44, +0.68] | +0.00 [-0.03, +0.03] |
| prose | 0.20 | 0.50 | 0.61 | 0.46 | 0.26 | 0.19 | 0.00 | +0.42 [+0.29, +0.53] | -0.38 [-0.49, -0.26] |

Pooled over the four wordings: EOP − A +0.36 [+0.29, +0.43], one-sided p 0.0, Holm p 0.0; EOP-N − A -0.13 [-0.21, -0.05]; EOP − P +0.40 [+0.36, +0.43].

