# Consolidated literature list supplied by the author (2026-11-14)

**Status: a list of candidate references, not a verified bibliography.** It consolidates the 24 entries of
`LITERATURE_TIMELINE.md` (cutoff 2026-11-02), 2 more from the six-paper review of 2026-11-13 and 2 from
earlier calibration notes. An entry may be cited in the report only after its title, authors, year and
venue were checked at the source (`paper/literature_review.md`, verification log). It is not a systematic
literature search.

## 1. Foundations: metareasoning and epistemic action
1. Horvitz (1988). Reasoning Under Varying and Uncertain Resource Constraints. https://www.microsoft.com/en-us/research/publication/reasoning-under-varying-and-uncertain-resource-constraints/
2. Russell & Wefald (1991). Principles of metareasoning. Artificial Intelligence. DOI 10.1016/0004-3702(91)90015-C
3. Kirsh & Maglio (1994). On Distinguishing Epistemic from Pragmatic Action. Cognitive Science. https://doi.org/10.1207/s15516709cog1804_1

## 2. Self-knowledge, uncertainty, calibration, clarification
4. Kadavath et al. (2022). Language Models (Mostly) Know What They Know. https://arxiv.org/abs/2207.05221
5. Zhu et al. (2023). On the Calibration of Large Language Models and Alignment. https://aclanthology.org/2023.findings-emnlp.654/
6. Farquhar et al. (2024). Detecting hallucinations in large language models using semantic entropy. https://www.nature.com/articles/s41586-024-07421-0
7. Zhang et al. (2024). CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in Large Language Models. https://aclanthology.org/2024.acl-long.578/
8. De Sabbata et al. (2024). Rational Metareasoning for Large Language Models. https://arxiv.org/abs/2410.05563

## 3. Abstention, uncertainty diagnosis, adaptive retrieval
9. Kirichenko et al. (2025). AbstentionBench: Reasoning LLMs Fail on Unanswerable Questions. https://papers.nips.cc/paper_files/paper/2025/hash/fb122bfc3f0127a94ded048b5b03496f-Abstract-Datasets_and_Benchmarks_Track.html
10. Moskvoretskii et al. (2025). Adaptive Retrieval Without Self-Knowledge? Bringing Uncertainty Back Home. https://aclanthology.org/2025.acl-long.319/
11. Yao et al. (2025). SeaKR: Self-aware Knowledge Retrieval for Adaptive Retrieval Augmented Generation. https://aclanthology.org/2025.acl-long.1312/
12. Liu et al. (2025). Do not Abstain! Identify and Solve the Uncertainty. https://aclanthology.org/2025.acl-long.840/

## 4. 2026: information, computation, sufficiency, epistemic action
13. Kim et al. (2026). Understanding Reasoning in LLMs through Strategic Information Allocation under Uncertainty. https://arxiv.org/abs/2603.15500
14. Li et al. (2026). Same Signal, Opposite Meaning: Direction-Informed Adaptive Learning for LLM Agents (DIAL). https://arxiv.org/abs/2605.06908
15. Babu & Iyer (2026). ToolChoiceConfusion: Causal Minimal Tool Filtering for Reliable LLM Agents. https://arxiv.org/abs/2606.06284
16. Wang et al. (2026). SuCo: Sufficiency-guided Continuous Adaptive Reasoning. https://proceedings.mlr.press/v306/wang26dz.html
17. Dong et al. (2026). Value of Information: A Framework for Human–Agent Communication. https://aclanthology.org/2026.acl-long.1987/
18. Huang et al. (2026). Do LLMs Know What to Ask and When? Evaluating Multi-Turn Information Seeking (MT-InfoSeek). https://arxiv.org/abs/2608.14808
19. Chen, Hua & Xiao (2026). Relevance Is Not Sufficient Evidence: Detecting Evidence Gaps Before Generation in RAG (RINSE). https://arxiv.org/abs/2609.37469
20. Liu, Padmanabhan & Viswanathan (2026). Before Agents Decide: Epistemic Action in LLM-Based Systems. https://arxiv.org/abs/2610.00511
21. Yin & Zhang (2026). Failure-mode-aware uncertainty intervention routing for large language models. Knowledge-Based Systems. https://www.sciencedirect.com/science/article/pii/S0950705126014115
22. Liu et al. (2026). Agents' Last Doubt: Knowing When to Act and When to Step Back in Tool-Using Agents (SURE-Act). https://arxiv.org/abs/2610.24194
23. Kinalioglu (2026). EPRAG: An epistemic policy framework for action selection in multi-source enterprise retrieval-augmented generation. Knowledge-Based Systems. https://www.sciencedirect.com/science/article/pii/S0950705126016552
24. Chen et al. (2026). To Retrieve or To Think? Cross-Boundary Context Evolution for Multi-hop Complex Reasoning. https://aclanthology.org/2026.findings-emnlp.2385/

## 5. From the six-paper review (2026-11-13)
25. Li et al. (2026). Ask, Relax, or Act? Evaluating Actionable Indeterminacy in LLM Preference Reasoning. https://arxiv.org/abs/2610.03102
26. Qu (2026). Active Epistemic Control for Query-Efficient Verified Planning. https://arxiv.org/abs/2602.03974

## 6. From earlier calibration notes
27. Mei et al. (2026). Reasoning about Uncertainty: Do Reasoning Models Know When They Don't Know? https://aclanthology.org/2026.findings-eacl.178/
28. Lacombe et al. (2025). Don't Think Twice! Over-Reasoning Impairs Confidence Calibration. https://arxiv.org/abs/2508.15050

Caveats carried over from the review: SURE-Act's generalisation to unseen families cannot be described as
uniformly absent; Active Epistemic Control's "2→9" figure is not a count; ToolChoiceConfusion's one-tool
filtering may make its benchmark partly circular with its method; MT-InfoSeek's order findings are not a
forced-order causal test; output format changes behaviour in "Ask, Relax, or Act?".
