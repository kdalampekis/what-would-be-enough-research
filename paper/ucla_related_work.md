# UCLA related work: Darwiche and Zamfirescu-Pereira

Checked on 2026-11-14. Every item in sections 1–5 was fetched at a primary source that day; section 6 lists the pages. "Record only" means the bibliographic record was confirmed but no abstract could be read. "Our reading" marks our own inference, which the cited papers do not state. Tables give authors, year, title and venue; section 5 adds pages and DOI.

## 1. Darwiche — relevant work

| Citation | What it establishes (from the abstract) | Relation to MSEP | Strength | Verified on |
|---|---|---|---|---|
| [U1] Darwiche, A., Hirth, A. (2020). On the Reasons Behind Decisions. ECAI 2020. Journal version [U2] (2023): On the (Complete) Reasons Behind Decisions. J. Logic, Language and Information. | Defines sufficient, necessary and complete reasons behind a Boolean classifier's decision. Evaluates statements such as "the decision will stick even if … because …". | Sufficient reason: a minimal part of a known instance that fixes the decision. Our minimal sufficient plan: a minimal set of unknown variables that fixes Q for every outcome (our reading). | direct formal relation | arXiv 2002.09284 (full text); doi 10.3233/FAIA200158; doi 10.1007/s10849-022-09377-8 |
| [U3] Darwiche, A., Ji, C. (2022). On the Computation of Necessary and Sufficient Explanations. AAAI 2022. | Sufficient reasons are the prime implicants of the complete reason. Necessary reasons are its prime implicates and correspond to contrastive explanations. | Necessary reason: a minimal part of the instance whose change can flip the decision. Our obligation: a minimal set of unknown variables on which a Q-true and a Q-false model differ (our reading). | direct formal relation | arXiv 2203.10451 (full text); doi 10.1609/aaai.v36i5.20498 |
| [U4] Shih, A., Choi, A., Darwiche, A. (2018). A Symbolic Approach to Explaining Bayesian Network Classifiers. IJCAI 2018. | Compiles such classifiers into tractable decision functions. One explanation type is a minimal set of features whose state is sufficient for the classification. | Earlier form of the sufficient reason. | direct formal relation | arXiv 1805.03364; doi 10.24963/ijcai.2018/708 |
| [U5] Darwiche, A. (2023). Logic for Explainable AI. LICS 2023. | Tutorial: necessary-and-sufficient, minimal sufficient and minimal necessary conditions for a decision. | Overview of [U1]–[U3]. | direct formal relation | arXiv 2305.05172; doi 10.1109/LICS56636.2023.10175757 |
| [U6] Chen, S. J., Choi, A., Darwiche, A. (2014). Algorithms and Applications for the Same-Decision Probability. JAIR. Earlier paper [U7] (record only): Choi, A., Xue, Y., Darwiche, A. (2012). Same-decision probability: A confidence measure for threshold-based decisions. IJAR. | The same-decision probability (SDP) is the probability that a threshold decision stays the same once hidden variables are observed. [U6] uses it as a stopping criterion and as a criterion for what to observe next, and gives an exact algorithm. | Matches our posterior-threshold rule, which is validated but not in the benchmark. Stopping and selection are the two questions MSEP asks. | direct formal relation (posterior rule only) | jair.org via doi 10.1613/jair.4218 (full text); Crossref 10.1016/j.ijar.2012.04.005 |
| [U8] Chen, S., Choi, A., Darwiche, A. (2015). Value of Information Based on Decision Robustness. AAAI 2015. [U9] Choi, Y., Darwiche, A., Van den Broeck, G. (2017). Optimal Feature Selection for Decision Robustness in Bayesian Networks. IJCAI 2017. | [U8]: a value-of-information criterion that prefers observations leading to decisions unlikely to change, with budgeted feature selection for naive Bayes. [U9]: the expected SDP of a feature set in general Bayesian network classifiers, and a search for the optimal subset. | Both choose a priced set of observations in advance so that the decision is settled. Probabilistic, not worst-case (our reading). | direct formal relation (probabilistic analogue) | Crossref 10.1609/aaai.v29i1.9684; Crossref 10.24963/ijcai.2017/215 |
| [U10] Chavira, M., Darwiche, A. (2008). On probabilistic inference by weighted model counting. Artificial Intelligence. | Record only. | Our posterior rule uses exact weighted model counting. | same toolbox | Crossref 10.1016/j.artint.2007.11.002 |
| [U11] Darwiche, A., Pipatsrisawat, K. (2009). Complete Algorithms. Handbook of Satisfiability. | Reviews complete SAT algorithms, including DPLL and clause-learning solvers. | The oracle's sufficiency check is a SAT query. | same toolbox | Crossref 10.3233/978-1-58603-929-5-99 |
| [U12] Darwiche, A., Marquis, P. (2002). A Knowledge Compilation Map. JAIR. [U13] Darwiche, A. (2001). Decomposable negation normal form. J. ACM. [U14] Darwiche, A. (2011). SDD: A New Canonical Representation of Propositional Knowledge Bases. IJCAI 2011. | [U12] compares target compilation languages by succinctness and polytime operations. [U13] and [U14] introduce DNNF and the Sentential Decision Diagram. | The repo does not use knowledge compilation. | background | jair.org via doi 10.1613/jair.989; Crossref 10.1145/502090.502091; ijcai.org PDF |
| [U15] Darwiche, A. (2009). Modeling and Reasoning with Bayesian Networks. Cambridge University Press. [U16] Darwiche, A. (2020). Three Modern Roles for Logic in AI. PODS 2020. | [U15]: textbook on building Bayesian networks and on exact and approximate inference. [U16]: logic for computation, for learning, and for reasoning about the behaviour of machine learning systems. | Context for the posterior rule and for [U1]–[U5]. | background | Crossref 10.1017/CBO9780511811357; arXiv 2004.08599 |

**How the closest concepts relate.** In [U1], a sufficient reason is a minimal subset of a fully known instance that keeps the decision whatever the other features are. In [U3], a necessary reason (contrastive explanation) is a minimal subset of the instance whose states must all change for the decision to change. Our reading: the obligation is the counterpart of the necessary reason, and the minimal sufficient plan is the counterpart of the sufficient reason, both moved from the known values of one instance to the variables still unknown. So the obligation is not the dual of a sufficient reason; it is dual to the plan. SDP [U6, U7] is the probability that a threshold decision survives further observations. Logical sufficiency is the case where no outcome can change the decision: the worst-case analogue (our reading). [U9] already scores observation sets chosen in advance, so "plan-level" is not unique to MSEP.

## 2. Zamfirescu-Pereira — relevant work

| Citation | What it establishes (from the abstract) | Relation to MSEP | Strength | Verified on |
|---|---|---|---|---|
| [U17] Zamfirescu-Pereira, J.D., Wei, H., Xiao, A., Gu, K., Jung, G., Lee, M. G., Hartmann, B., Yang, Q. (2023). Herding AI Cats: Lessons from Designing a Chatbot by Prompting GPT-3. DIS 2023. | A case study of designing a chatbot by prompting GPT-3/4 alone. No prompt made GPT reliably say "I don't know" when it should, so conversations had no guardrails after a breakdown. | Motivation only: a model that does not signal the limits of what it knows. | background (motivation) | Crossref 10.1145/3563657.3596138; Semantic Scholar (abstract) |
| [U18] Zamfirescu-Pereira, J.D., Wong, R. Y., Hartmann, B., Yang, Q. (2023). Why Johnny Can't Prompt: How Non-AI Experts Try (and Fail) to Design LLM Prompts. CHI 2023. | Non-experts explored prompt designs opportunistically, not systematically, and over-generalised. | Weak: relevant only to our finding that wording and format change results. | background | Crossref 10.1145/3544548.3581388; Semantic Scholar (abstract) |

**Sycophancy: what was and was not found.** We found no paper on sycophancy authored or co-authored by J.D. Zamfirescu-Pereira. We checked the arXiv author listing (16 papers), the Semantic Scholar author record (38 papers), Crossref, zamfi.net (publications, teaching page, CV, research and teaching statements), his Google Scholar profile (20 most recent titles) and his UCLA faculty page. No title or abstract read mentions sycophancy, flattery or deference to users. The nearest content is the "I don't know" finding in [U17]. A UCLA Samueli Q&A says he is prototyping a course, "AI for Human Interaction". We found no public syllabus or reading list for any UCLA course of his, so no course-list papers are reported.

## 3. Sycophancy — primary sources

Not associated with either professor. Citation counts are from Semantic Scholar on 2026-11-14; we did not run an exhaustive ranking.

| Citation | What it establishes (from the abstract) | Verified on |
|---|---|---|
| [U19] Sharma, M., and 18 others (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548; ICLR 2024. 1,669 citations. | Five AI assistants show sycophancy on four free-form text-generation tasks. In human preference data, responses that match a user's views are more likely to be preferred. | arXiv 2310.13548; proceedings.iclr.cc |
| [U20] Perez, E., and 62 others (2023). Discovering Language Model Behaviors with Model-Written Evaluations. Findings of ACL 2023. 1,218 citations. | Generates 154 evaluation datasets with language models. Larger models repeat back a dialogue user's preferred answer ("sycophancy"). | arXiv 2212.09251; aclanthology.org/2023.findings-acl.847 |
| [U21] Wei, J., Huang, D., Lu, Y., Zhou, D., Le, Q. V. (2023). Simple synthetic data reduces sycophancy in large language models. arXiv:2308.03958. 228 citations. | Scaling and instruction tuning increase sycophancy in PaLM models. Models agree with objectively wrong addition statements when the user does. Synthetic-data fine-tuning reduces this. | arXiv 2308.03958 |

## 4. Proposed sentences

**(a) Related Work, "builds on"** (only if the author confirms the project followed this work):
> The oracle builds on the logical theory of the reasons behind decisions [U1, U3]: a minimal sufficient plan plays the role of a sufficient reason (a minimal set of values that fixes a decision) and an obligation plays the role of a necessary reason (a minimal set of values whose change can flip it), with unknown variables in place of the known values of one instance.

**(a) Related Work, "is related to":**
> The oracle is related to the logical theory of the reasons behind decisions [U1, U3]: a minimal sufficient plan resembles a sufficient reason (a minimal set of values that fixes a decision) and an obligation resembles a necessary reason (a minimal set of values whose change can flip it), with unknown variables in place of the known values of one instance. The posterior-threshold rule, which the benchmark does not use, is related to the same-decision probability [U6, U7].

**(b) Introduction (motivation only):**
> Assistants have been reported to match their answers to a user's stated views instead of the truth [U19], and designers have found that no prompt made a model reliably say "I don't know" when it should [U17]; MSEP does not test deference to a user, and asks instead whether a model can tell what evidence would settle a question.

**(c) Acknowledgement:**
> This work was done independently. It was informed by the published work of Adnan Darwiche and co-authors on the logic of decisions and of J.D. Zamfirescu-Pereira and co-authors on prompting language models; neither professor was involved in this work or reviewed it.

## 5. Reference list

- [U1] Darwiche, A., Hirth, A. (2020). On the Reasons Behind Decisions. ECAI 2020, IOS Press. https://doi.org/10.3233/FAIA200158 (arXiv:2002.09284)
- [U2] Darwiche, A., Hirth, A. (2023). On the (Complete) Reasons Behind Decisions. Journal of Logic, Language and Information 32(1), 63–88. https://doi.org/10.1007/s10849-022-09377-8
- [U3] Darwiche, A., Ji, C. (2022). On the Computation of Necessary and Sufficient Explanations. AAAI 2022, 36(5), 5582–5591. https://doi.org/10.1609/aaai.v36i5.20498 (arXiv:2203.10451)
- [U4] Shih, A., Choi, A., Darwiche, A. (2018). A Symbolic Approach to Explaining Bayesian Network Classifiers. IJCAI 2018, 5103–5111. https://doi.org/10.24963/ijcai.2018/708 (arXiv:1805.03364)
- [U5] Darwiche, A. (2023). Logic for Explainable AI. LICS 2023, 1–11. https://doi.org/10.1109/LICS56636.2023.10175757 (arXiv:2305.05172)
- [U6] Chen, S. J., Choi, A., Darwiche, A. (2014). Algorithms and Applications for the Same-Decision Probability. Journal of Artificial Intelligence Research 49, 601–633. https://doi.org/10.1613/jair.4218
- [U7] Choi, A., Xue, Y., Darwiche, A. (2012). Same-decision probability: A confidence measure for threshold-based decisions. International Journal of Approximate Reasoning 53(9), 1415–1428. https://doi.org/10.1016/j.ijar.2012.04.005
- [U8] Chen, S., Choi, A., Darwiche, A. (2015). Value of Information Based on Decision Robustness. AAAI 2015, 29(1). https://doi.org/10.1609/aaai.v29i1.9684
- [U9] Choi, Y., Darwiche, A., Van den Broeck, G. (2017). Optimal Feature Selection for Decision Robustness in Bayesian Networks. IJCAI 2017, 1554–1560. https://doi.org/10.24963/ijcai.2017/215
- [U10] Chavira, M., Darwiche, A. (2008). On probabilistic inference by weighted model counting. Artificial Intelligence 172(6–7), 772–799. https://doi.org/10.1016/j.artint.2007.11.002
- [U11] Darwiche, A., Pipatsrisawat, K. (2009). Complete Algorithms. In Handbook of Satisfiability, IOS Press. https://doi.org/10.3233/978-1-58603-929-5-99
- [U12] Darwiche, A., Marquis, P. (2002). A Knowledge Compilation Map. Journal of Artificial Intelligence Research 17, 229–264. https://doi.org/10.1613/jair.989
- [U13] Darwiche, A. (2001). Decomposable negation normal form. Journal of the ACM 48(4), 608–647. https://doi.org/10.1145/502090.502091
- [U14] Darwiche, A. (2011). SDD: A New Canonical Representation of Propositional Knowledge Bases. IJCAI 2011, 819–826. https://www.ijcai.org/Proceedings/11/Papers/143.pdf
- [U15] Darwiche, A. (2009). Modeling and Reasoning with Bayesian Networks. Cambridge University Press. https://doi.org/10.1017/CBO9780511811357
- [U16] Darwiche, A. (2020). Three Modern Roles for Logic in AI. PODS 2020, 229–243. https://doi.org/10.1145/3375395.3389131 (arXiv:2004.08599)
- [U17] Zamfirescu-Pereira, J.D., Wei, H., Xiao, A., Gu, K., Jung, G., Lee, M. G., Hartmann, B., Yang, Q. (2023). Herding AI Cats: Lessons from Designing a Chatbot by Prompting GPT-3. DIS 2023, 2206–2220. https://doi.org/10.1145/3563657.3596138
- [U18] Zamfirescu-Pereira, J.D., Wong, R. Y., Hartmann, B., Yang, Q. (2023). Why Johnny Can't Prompt: How Non-AI Experts Try (and Fail) to Design LLM Prompts. CHI 2023, 1–21. https://doi.org/10.1145/3544548.3581388
- [U19] Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S. R., Kravec, S., Maxwell, T., McCandlish, S., Ndousse, K., Rausch, O., Schiefer, N., Yan, D., Zhang, M., Perez, E. (2023). Towards Understanding Sycophancy in Language Models. arXiv:2310.13548; ICLR 2024. https://arxiv.org/abs/2310.13548
- [U20] Perez, E., Ringer, S., Lukošiūtė, K., Nguyen, K., Chen, E., Heiner, S., Pettit, C., Olsson, C., Kundu, S., Kadavath, S., and 53 others (2023). Discovering Language Model Behaviors with Model-Written Evaluations. Findings of ACL 2023, 13387–13434. https://doi.org/10.18653/v1/2023.findings-acl.847 (arXiv:2212.09251)
- [U21] Wei, J., Huang, D., Lu, Y., Zhou, D., Le, Q. V. (2023). Simple synthetic data reduces sycophancy in large language models. arXiv:2308.03958. https://arxiv.org/abs/2308.03958

## 6. Verification log

All fetches on 2026-11-14. "arXiv API" is export.arxiv.org, which returns the same title, authors and abstract as the abstract page; for the items marked † the abstract page arxiv.org/abs/… was also fetched and the title matched.

### Sources that failed

| Source | Result |
|---|---|
| dblp.org/pid/d/AdnanDarwiche (HTML and XML), dblp.org author search API | Blocked by a bot check (Anubis page, HTTP 202 or access denied). DBLP was not used. |
| reasoning.cs.ucla.edu | Connection refused (one attempt). |
| arxiv.org/a/darwiche_a_1 | HTTP 404. The arXiv API author query was used instead (59 entries). |
| sciencedirect.com (IJAR 2012), doi.org → linkinghub.elsevier.com (AIJ 2008) | HTTP 403 / redirect not readable. Abstracts of [U7] and [U10] not read. OpenAlex also has no abstract for either. |
| scholar.google.com search (author + sycophancy) | Redirected to a sync page; not followed. The profile page loaded partly (20 most recent titles). |
| Semantic Scholar DOI:10.3233/FAIA200158 | HTTP 404. [U1] verified on arXiv and Crossref instead. |

### Darwiche candidates

| Candidate | Page fetched | Status | Notes and corrections |
|---|---|---|---|
| On the Reasons Behind Decisions | arXiv API and abs page† 2002.09284; arXiv PDF (Definitions 1–3 read); Crossref 10.3233/FAIA200158 | verified [U1] | Crossref gives no pages. arXiv title has capital "The". |
| On the (Complete) Reasons Behind Decisions | Crossref 10.1007/s10849-022-09377-8 (abstract) | verified [U2] | Online 2022-08-18; print issue 2023-03, vol. 32(1). Year given as 2023. |
| On the Computation of Necessary and Sufficient Explanations | arXiv API and abs page† 2203.10451; arXiv PDF (Definition 5 and Proposition 10 read); Crossref 10.1609/aaai.v36i5.20498 | verified [U3] | The paper attributes contrastive explanations to Ignatiev et al. (2020); that paper was not checked and is not cited here. |
| A Symbolic Approach to Explaining Bayesian Network Classifiers | arXiv API and abs page† 1805.03364; Crossref 10.24963/ijcai.2018/708 | verified [U4] | — |
| Logic for Explainable AI | arXiv API and abs page† 2305.05172; Crossref 10.1109/LICS56636.2023.10175757 | verified [U5] | Crossref has no abstract; abstract read on arXiv. |
| Algorithms and Applications for the Same-Decision Probability | jair.org article page via doi 10.1613/jair.4218; JAIR PDF (Definition 1 and §4.1 read); Crossref | verified [U6] | JAIR and Crossref list initials only (S. J. Chen, A. Choi, A. Darwiche). |
| Same-decision probability: A confidence measure for threshold-based decisions | Crossref 10.1016/j.ijar.2012.04.005; Semantic Scholar | record only [U7] | Semantic Scholar spells the second author "Ye-Xiang Xue"; Crossref's "Yexiang Xue" is used. Definition read only as restated in [U6]. |
| Value of Information Based on Decision Robustness | Crossref 10.1609/aaai.v29i1.9684 (abstract) | verified [U8] | Crossref gives no pages. Crossref date 2015-03-04. |
| Optimal Feature Selection for Decision Robustness in Bayesian Networks | Crossref 10.24963/ijcai.2017/215 (abstract) | verified [U9] | Found during the search; not in the candidate list. |
| On probabilistic inference by weighted model counting | Crossref 10.1016/j.artint.2007.11.002; Semantic Scholar | record only [U10] | OpenAlex gives year 2007 (online); Crossref print date 2008-04 is used. |
| Complete Algorithms (Handbook of Satisfiability) | Crossref 10.3233/978-1-58603-929-5-99 (abstract) | verified [U11] | Crossref gives no pages or chapter number for the 2009 record. A second record, 10.3233/FAIA200986 (2021, second edition), is titled "Chapter 3. Complete Algorithms"; the chapter number comes from that record. The abstract spells "Davis-Putnum" and "Stalmarck". |
| A Knowledge Compilation Map | jair.org article page via doi 10.1613/jair.989; Crossref | verified [U12] | JAIR lists initials only. |
| Decomposable negation normal form | Crossref 10.1145/502090.502091 (abstract) | verified [U13] | — |
| SDD: A New Canonical Representation of Propositional Knowledge Bases | ijcai.org/Proceedings/11/Papers/143.pdf (first page and page numbers read) | verified [U14] | No Crossref record found. Pages 819–826 read from the PDF footers. |
| Modeling and Reasoning with Bayesian Networks | Crossref 10.1017/CBO9780511811357 (publisher abstract) | verified [U15] | Book not read. |
| Three Modern Roles for Logic in AI | arXiv API and abs page† 2004.08599; Crossref 10.1145/3375395.3389131 | verified [U16] | A second Crossref record exists (EPTCS 326, 10.4204/eptcs.326.0.2); the PODS record is used. |
| On Quantifying Literals in Boolean Logic and its Applications to Explainable AI (Darwiche, Marquis; JAIR 72, 285–328, 2021) | jair.org page via doi 10.1613/jair.1.12756; arXiv API 2108.09876 | verified, not listed | Peripheral: the quantification operator behind complete reasons. |
| On the power of clause-learning SAT solvers as resolution engines (Pipatsrisawat, Darwiche; Artificial Intelligence 175(2), 512–525, 2011) | Crossref 10.1016/j.artint.2010.10.002; Semantic Scholar | record only, not listed | No abstract available. |
| A New Class of Explanations for Classifiers with Non-Binary Features (Ji, Darwiche; arXiv:2304.14760, JELIA 2023 per arXiv comment) | arXiv API | verified on arXiv only, not listed | Its abstract states that sufficient reasons are also called abductive or PI-explanations and necessary reasons contrastive or counterfactual explanations. |
| Circuit Representations of Random Forests with Applications to XAI (Ji, Darwiche; arXiv:2602.08362) | arXiv API | verified on arXiv only, not listed | Computes decision robustness and all shortest ways to flip a decision for random forests. |
| On Tractable Representations of Binary Neural Networks (Shi, Shih, Darwiche, Choi; KR 2020) | arXiv API 2004.02082; Crossref 10.24963/kr.2020/91 | verified, not listed | Verification of robustness; peripheral. |
| Compiling Bayesian Network Classifiers into Decision Graphs (Shih, Choi, Darwiche; AAAI 2019) | Crossref 10.1609/aaai.v33i01.33017966 | verified, not listed | Peripheral. |
| Verifying Binarized Neural Networks by Angluin-Style Learning (Shih, Darwiche, Choi; SAT 2019) | Crossref 10.1007/978-3-030-24258-9_25 | record only, not listed | No abstract. |
| On the tractable counting of theory models… (Darwiche; arXiv cs/0003044, 2000) | arXiv API and abs page† | verified on arXiv only, not listed | Introduces d-DNNF and model counting on it. Journal version not checked. |
| An Exhaustive DPLL Algorithm for Model Counting (Oztok, Darwiche; JAIR 62, 2018) | Crossref 10.1613/jair.1.11201 | verified, not listed | Peripheral. |
| Which Actions Are Always Necessary in Fully-Observable Non-Deterministic Planning? (Zhang, Darwiche; FLAIRS 2024) | Crossref 10.32473/flairs.37.1.135595 (abstract) | verified, not listed | About explaining action choices in a trace, not about information sufficiency. |
| Dsat: A Native SAT Solver for Discrete Logic (Zhang, Zhou, Darwiche; arXiv:2605.09347) | arXiv API | verified on arXiv only, not listed | Peripheral. |
| "Formal Verification of Bayesian Network Classifiers" | Crossref query | not found | The query returned other papers. Not cited. |
| "An exact algorithm for computing the same-decision probability" (conference paper) | Crossref query | not found | The query returned [U6] and [U7] only. Not cited. |
| "Same-decision probability … under noisy sensors" (2010 paper cited inside [U6]) | Crossref query | not found | Seen only as a citation in [U6]. Not cited. |

### Zamfirescu-Pereira candidates and searches

| Candidate or search | Page fetched | Result |
|---|---|---|
| Herding AI Cats | Crossref 10.1145/3563657.3596138; Semantic Scholar (abstract); zamfi.net summary | verified [U17]. Crossref has no abstract; it was read in the Semantic Scholar record. Semantic Scholar abbreviates two author names; Crossref names are used. |
| Why Johnny Can't Prompt | Crossref 10.1145/3544548.3581388; Semantic Scholar (abstract) | verified [U18]. |
| arXiv API, author "Zamfirescu-Pereira" | 16 entries; abstracts scanned for sycophan-, flatter-, defer-, reliance, "don't know", honest, overconfid-, uncertain-, hallucin- | No relevant hit. Neither [U17] nor [U18] is on arXiv. |
| Semantic Scholar author record 1412561558 | 38 papers, titles read | No sycophancy title. Abstracts read for "Un-default" Behavior Tuning (IUI 2026) and Spotting AI Missteps (SIGCSE TS 2025): neither is about sycophancy. |
| zamfi.net (home, /teaching, CV, research statement, teaching statement) | All fetched; PDFs searched as text | No mention of sycophancy, flattery, deference or reliance. The teaching page lists no UCLA course. The CV PDF was created on 2025-06-07, so it may predate recent work. |
| Google Scholar profile (user CUlYaZ8AAAAJ) | 20 most recent titles loaded | No sycophancy title. The rest of the list did not load. |
| samueli.ucla.edu faculty page | fetched | No courses listed. No sycophancy mention. |
| samueli.ucla.edu "Q&A with Professor J.D. Zamfirescu-Pereira" | fetched | Mentions a course he is prototyping, "AI for Human Interaction", and over-reliance on model statements. No reading list, no course number, no date. Not a publication; not cited. |
| Web searches: name + sycophancy; name + sycophantic / over-reliance; name + UCLA course syllabus (four variants, one restricted to ucla.edu) | search results | No sycophancy paper by him. No public UCLA syllabus or reading list. One search hit (a Google Doc) was a Carnegie Mellon course syllabus with other instructors; discarded. |

### Sycophancy sources

| Candidate | Page fetched | Status | Notes |
|---|---|---|---|
| Towards Understanding Sycophancy in Language Models | arXiv API and abs page† 2310.13548; proceedings.iclr.cc 2024 abstract page; Semantic Scholar | verified [U19] | arXiv v4 lists 19 authors. The ICLR proceedings page lists 18: Newton Cheng is absent and Korbak's first name is "Tomek". The arXiv list is used. |
| Discovering Language Model Behaviors with Model-Written Evaluations | arXiv API and abs page† 2212.09251; aclanthology.org/2023.findings-acl.847.bib; Semantic Scholar | verified [U20] | 63 authors in both records; the reference lists the first ten. The Anthology record spells "Lukosiute" and "Mercado" without diacritics. |
| Simple synthetic data reduces sycophancy in large language models | arXiv API and abs page† 2308.03958; Semantic Scholar | verified [U21] | arXiv only; no proceedings record found. |

### Open points for the author

1. No sycophancy paper is linked to J.D. Zamfirescu-Pereira by any source checked. If the papers came from a course of his, the reading list is not public; the author should supply it.
2. "Builds on" in sentence (a) needs the author's confirmation. The repo does not use knowledge compilation, and no repo document cites Darwiche's work.
3. The correspondences in section 1 are our reading. The duality between sufficient plans and obligations is proved in Appendix D of the report; its link to the duality of sufficient and necessary reasons is not stated in the papers read.
4. [U7] and [U10] are confirmed as records only.
5. Sections 1–5 are about 2,200 words by `wc`, above the 1,500 target. The reference list (about 500 words) repeats the table citations because both were asked for.
