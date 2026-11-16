# LITERATURE_TIMELINE.md
# Από το «πόσο σίγουρο είναι το μοντέλο;» στο «τι ακριβώς θα ήταν αρκετό;»
## Χρονική ιστορία του research area σε απλή γλώσσα

**Cutoff:** 2 Νοεμβρίου 2026

Αυτό το αρχείο δεν ξεκινά από τη δική μας ιδέα. Ξεκινά από το πώς εξελίχθηκε το πεδίο και ποια ερώτηση προσπαθούσε να απαντήσει κάθε κύμα δουλειάς.

---

# 1. Πριν τα LLMs: το βασικό πρόβλημα του metareasoning

Πολύ πριν τα σημερινά language models, η AI και η decision theory είχαν ήδη ένα σημαντικό ερώτημα:

> Αν ένας agent μπορεί να συνεχίσει να σκέφτεται, να συλλέξει πληροφορία ή να πάρει απόφαση τώρα, πότε αξίζει να κάνει το καθένα;

Αυτό είναι **metareasoning**: reasoning για το ίδιο το reasoning.

Υπάρχουν δύο κλασικές ιδέες:

- **Value of Information (VOI):** πόσο αξίζει να μάθω κάτι νέο πριν αποφασίσω;
- **Value of Computation (VOC):** πόσο αξίζει να ξοδέψω επιπλέον computation πριν αποφασίσω;

Άρα η γενική θεωρία «σκέψου αν αξίζει να ρωτήσεις ή να υπολογίσεις» δεν είναι καινούργια.

Το καινούργιο πρόβλημα με τα LLMs είναι αν τα ίδια τα μοντέλα μπορούν να κάνουν αυτή τη διαδικασία αξιόπιστα.

---

# 2. 2022–2024: «Ξέρει το μοντέλο πότε μπορεί να είναι λάθος;»

Με τα μεγάλα language models, η πρώτη μεγάλη ερώτηση έγινε:

> Μπορεί το model να καταλάβει πόσο σίγουρο πρέπει να είναι για την απάντησή του;

Εδώ εμφανίζονται έννοιες όπως:

### Calibration
Αν το model λέει «είμαι 80% σίγουρο» σε πολλές ερωτήσεις, θα θέλαμε περίπου 80% αυτών των απαντήσεων να είναι σωστές.

### Uncertainty estimation
Προσπαθούμε να μετρήσουμε πόσο uncertain είναι το model.

Μέθοδοι:
- token probabilities;
- entropy;
- verbal confidence;
- multiple samples / self-consistency;
- semantic uncertainty.

Το βασικό συμπέρασμα της literature είναι ότι τα LLMs έχουν κάποια χρήσιμα uncertainty signals, αλλά δεν είναι τέλεια calibrated και συχνά είναι overconfident.

Άρα:

> **Το ότι ένα model είναι λάθος δεν σημαίνει ότι ξέρει ότι είναι λάθος.**

---

# 3. 2024: «Αν μπορώ να σκεφτώ περισσότερο, πότε αξίζει;»

Με chain-of-thought και reasoning models, εμφανίζεται άλλο πρόβλημα:

> Πρέπει κάθε ερώτηση να παίρνει πολύ computation;

Όχι.

Το paper **Rational Metareasoning for Large Language Models** (2024) χρησιμοποιεί Value of Computation ώστε το model να μαθαίνει πότε αξίζει να ξοδεύει επιπλέον reasoning.

Reference:
https://arxiv.org/abs/2410.05563

Η σημαντική ιδέα:

> More reasoning has a cost, άρα πρέπει να χρησιμοποιείται όταν έχει αναμενόμενο όφελος.

Αυτό σημαίνει ότι το «πότε πρέπει να σκεφτώ περισσότερο;» έχει ήδη σοβαρή βιβλιογραφία.

---

# 4. 2025: «Αν δεν είμαι σίγουρος, μήπως πρέπει να μην απαντήσω;»

Το επόμενο κύμα κοιτάζει **abstention / selective prediction**.

Η ερώτηση γίνεται:

> Αν το model δεν έχει αρκετή βεβαιότητα, πρέπει να απαντήσει ή να πει “δεν ξέρω”;

Εδώ εμφανίζεται το utility.

Για παράδειγμα:
- σωστή απάντηση: +1
- λάθος απάντηση: -10
- abstain: 0

Τότε δεν αρκεί να ξέρουμε confidence. Πρέπει να το μετατρέψουμε σε action.

Άρα:

> **Uncertainty estimation και decision policy είναι διαφορετικά προβλήματα.**

---

# 5. 2025–2026: «Αν λείπει κάτι, πρέπει να κάνω retrieval ή να ρωτήσω;»

Με RAG και agents, η ερώτηση μετακινείται:

> Ξέρει το model πότε χρειάζεται περισσότερη εξωτερική πληροφορία;

Εδώ έχουμε:
- adaptive retrieval;
- clarification questions;
- active information seeking;
- human-agent information acquisition.

Το model δεν πρέπει απλώς να κάνει retrieval πάντα. Πρέπει να καταλάβει πότε το current context δεν είναι αρκετό.

---

# 6. 2026: «Δεν αρκεί να ξέρεις ότι λείπει information — πρέπει να ξέρεις ποιο information»

Το **MT-InfoSeek** (Αύγουστος 2026) κάνει το πρόβλημα πολύ πιο αυστηρό.

Reference:
https://www.microsoft.com/en-us/research/publication/do-llms-know-what-to-ask-and-when-evaluating-multi-turn-information-seeking/

Δεν ρωτά απλώς:
> χρειάζεται extra information;

Ρωτά:
> ποια ακριβώς variables πρέπει να μάθεις ώστε η απάντηση να γίνει uniquely determined;

Το paper formalizes ένα **minimal sufficient set of queries**.

Σημαντικό finding:
τα models συχνά καταλαβαίνουν ότι λείπει information, αλλά:
- υποεκτιμούν πόσο information λείπει,
- η λάθος σειρά ερωτήσεων μειώνει την ακρίβεια (διόρθωση 2026-11-03: το abstract δεν λέει ότι «ρωτάνε λάθος variables»),
- σταματούν πολύ νωρίς.

Άρα:

> **“Need information” δεν σημαίνει “know what information is enough”.**

---

# 7. 2026: «More compute δεν σημαίνει ότι το compute θα βοηθήσει»

Το **Same Signal, Opposite Meaning / DIAL** (Μάιος 2026) μελετά adaptive test-time compute.

Reference:
https://arxiv.org/abs/2605.06908

Δείχνει κάτι πολύ σημαντικό:

> Ένα uncertainty signal μπορεί σε ένα setting να σημαίνει “extra compute helps” και σε άλλο “extra compute hurts”.

Άρα πρέπει να ξεχωρίζουμε:

- **compute need**
- **compute suitability**

Το ότι ένα state είναι δύσκολο δεν σημαίνει ότι περισσότερο reasoning είναι η σωστή intervention.

---

# 8. 2026: «Relevance δεν σημαίνει sufficiency»

Σε tool use, retrieval και evidence evaluation, η literature αρχίζει να διαχωρίζει:

- ένα action/tool/evidence είναι **relevant**;
- ή είναι πραγματικά **sufficient** ώστε να λυθεί το decision;

Αυτό είναι σημαντική αλλαγή.

Ένα tool μπορεί να σχετίζεται με το task, αλλά να μην καλύπτει το blocking requirement.

Ένα retrieved passage μπορεί να είναι topical, αλλά να μην περιέχει το decisive fact.

Άρα:

> **Το σωστό action δεν είναι απλώς το πιο σχετικό action.**

---

# 9. 2026: «Πότε πρέπει να ρωτήσεις, πότε να αλλάξεις constraints, πότε να δράσεις;»

Το **Ask, Relax, or Act?** (2 Οκτωβρίου 2026) δημιουργεί solver-grounded benchmark.

Reference:
https://arxiv.org/abs/2610.03102

Το model πρέπει να αποφασίσει αν:
- μπορεί να ACT;
- χρειάζεται CLARIFICATION;
- πρέπει να γίνει constraint repair.

Σημαντικό αποτέλεσμα:
ένα model μπορεί να βρει το σωστό high-level label αλλά να παράγει λάθος concrete question ή repair.

Άρα:

> **Correct action type != correct usable intervention.**

---

# 10. 2026: «Τι θα γινόταν αν δοκίμαζα κάθε διαφορετική action;»

Το **Agents' Last Doubt / SURE-Act** (16 Οκτωβρίου 2026) κάνει counterfactual evaluation διαφορετικών agent actions.

Reference:
https://arxiv.org/abs/2610.24194

> **Μη επιβεβαιωμένο (2026-11-03):** καμία αναζήτηση δεν βρήκε αυτό το paper, τον τίτλο ή το όνομα SURE-Act, και το arXiv ID φαίνεται πολύ υψηλό για υποβολή στις 16 Οκτωβρίου. Να επιβεβαιωθεί πριν χρησιμοποιηθεί.

Σε κάθε decision point εκτελεί τις legal actions και μετρά:
- task success;
- interaction cost;
- irreversible errors.

Μετά εκπαιδεύει controller.

Άρα ούτε το:
> “compare the counterfactual value of multiple actions”

είναι από μόνο του καινούργιο.

---

# 11. 2026: «Πρώτα diagnosis του epistemic state, μετά action»

Το **EPRAG** (25 Οκτωβρίου 2026) χωρίζει:

1. evidence-state diagnosis;
2. response/action selection.

Reference:
https://www.sciencedirect.com/science/article/abs/pii/S0950705126016552

Χρησιμοποιεί επίσης **counterfactual answerability**:
> υπάρχει clarification που, αν απαντηθεί, θα κάνει το query answerable;

Αυτό πλησιάζει πολύ στη λογική του “what would be enough?”.

Αλλά είναι RAG-specific και χρησιμοποιεί approximate LLM/NLI answerability, όχι exact mixed information+computation planning.

---

# 12. Τι έχει λοιπόν ήδη μελετηθεί;

Μέχρι τον Νοέμβριο 2026 έχουμε σημαντική δουλειά πάνω σε:

- uncertainty detection;
- calibration;
- abstention;
- adaptive retrieval;
- clarification;
- minimal sufficient information;
- adaptive compute;
- Value of Computation;
- evidence sufficiency;
- relevant vs sufficient tools/evidence;
- action routing;
- solver-grounded action selection;
- counterfactual action outcomes.

Άρα δεν μπορούμε να πούμε ότι οποιοδήποτε από αυτά είναι «δικό μας νέο problem».

---

# 13. Τι φαίνεται να λείπει ακόμα;

Το κενό που δεν βρήκαμε να καλύπτεται ως ενιαίο exact benchmark είναι:

> Ένα state όπου το model μπορεί να χρειάζεται:
> - μόνο information,
> - μόνο computation,
> - και τα δύο,
> - ή κανένα διαθέσιμο intervention να μην αρκεί,
> και όπου υπάρχει exact oracle που ξέρει ποιο **minimal plan** είναι πραγματικά sufficient.

Αυτό είναι πιο γενικό από:
- “should I ask?”
- “should I think?”
- “which query should I ask?”
- “does extra compute help?”

---

# 14. Η νέα ερώτησή μας

> **When an AI agent lacks sufficient grounds for a reliable decision, can it determine whether the minimal sufficient epistemic plan requires additional information, additional computation, both, or neither — and can it construct that plan correctly?**

Στα ελληνικά:

> Όταν ένα AI δεν έχει ακόμα αρκετή βάση για να πάρει αξιόπιστη απόφαση, μπορεί να καταλάβει αν χρειάζεται επιπλέον πληροφορία, επιπλέον computation, και τα δύο, ή αν τίποτα από τα διαθέσιμα resources δεν αρκεί — και μπορεί να βρει το ελάχιστο sufficient plan;

---

# 15. Γιατί έχουμε 3 evaluation modes;

Υπάρχει ένα πολύ σημαντικό confound:

> Το model μπορεί να μη φτάσει ποτέ στο “τι χρειάζομαι;” επειδή δεν κατάλαβε καν ότι υπάρχει insufficiency.

Γι' αυτό δεν αρκεί ένα end-to-end experiment.

### Mode A — End-to-End
Το model πρέπει μόνο του να:
- καταλάβει ότι κάτι λείπει;
- διαγνώσει τι;
- φτιάξει plan.

### Mode B — Detection-Controlled
Του λέμε:
> “The current state is insufficient.”

Τώρα μετράμε:
- diagnosis;
- plan.

### Mode C — Diagnosis-Controlled
Του λέμε και τη σωστή resource class:
> “This case requires BOTH information and computation.”

Τώρα μετράμε καθαρά:
- μπορεί να βρει **ποια** information;
- **ποιο** computation;
- σε ποια σειρά;
- και να σταματήσει όταν αρκούν;

Αυτό μας αποτρέπει από λάθος conclusion.

---

# 16. Τι benchmark θέλουμε να φτιάξουμε;

Για κάθε formal state, θα ξέρουμε:

- αν είναι ήδη sufficient;
- ποια information actions υπάρχουν;
- ποια computation actions υπάρχουν;
- ποια είναι irrelevant;
- ποια είναι relevant αλλά insufficient;
- ποια είναι sufficient;
- ποιο minimal combination είναι sufficient;
- αν χρειάζεται sequence;
- αν τίποτα δεν αρκεί.

Το gold label δεν είναι μόνο:
> ASK

αλλά μπορεί να είναι:

```text
ASK(A)
then
VERIFY(P2)
then STOP
```

---

# 17. Τι θέλουμε να βρούμε;

Πιθανά findings:

1. Models detect insufficiency αλλά δεν ξέρουν τι resource χρειάζεται.
2. Ξέρουν το σωστό resource type αλλά επιλέγουν λάθος concrete action.
3. Μπερδεύουν relevance με sufficiency.
4. Αποτυγχάνουν κυρίως σε BOTH cases.
5. Σταματούν πριν το plan γίνει sufficient.
6. Συνεχίζουν να ξοδεύουν resources αφού η απόφαση είναι ήδη justified.

Όλα αυτά είναι πιο informative από ένα απλό “accuracy dropped”.

---

# 18. Ποια solution προτείνουμε;

## Epistemic Obligation Planner

Αν το model δεν μπορεί μόνο του να βρει τι ακριβώς λείπει, μπορούμε να κάνουμε explicit τα unresolved obligations.

Παράδειγμα:

```text
Decision q unresolved

O1: truth(A) unknown
O2: proof step B -> C unverified
```

Actions:

```text
ASK(A)          -> resolves O1
VERIFY(B -> C)  -> resolves O2
```

Ο planner:
1. βρίσκει τα unresolved obligations;
2. βλέπει ποια actions τα λύνουν;
3. βρίσκει το minimum-cost sufficient plan;
4. το εκτελεί;
5. ξαναελέγχει sufficiency;
6. σταματά όταν δεν χρειάζεται άλλο resource.

---

# 19. Τι value δίνει αν δουλέψει;

Αν λύσουμε αυτό το problem, δεν «λύνουμε calibration» ή «λύνουμε retrieval» γενικά.

Δίνουμε όμως ένα **decision layer** που μπορεί να χρησιμοποιήσει αυτές τις δυνατότητες σωστά.

Πρακτικά:

### Λιγότερα άχρηστα searches
Ο agent δεν κάνει retrieval επειδή απλώς είναι uncertain.

### Λιγότερο wasted reasoning
Δεν κάνει 20 reasoning loops όταν λείπει external fact.

### Καλύτερες ερωτήσεις προς ανθρώπους
Δεν λέει “can you provide more context?” γενικά. Ζητά το decisive missing information.

### Καλύτερη tool use
Δεν επιλέγει απλώς relevant tools. Επιλέγει actions που πραγματικά discharge unresolved obligations.

### Καλύτερο stopping
Ξέρει πότε έχει αρκετά.

### Περισσότερη auditability
Μπορούμε να δούμε:
- τι έλειπε;
- ποια action το κάλυψε;
- γιατί σταμάτησε;

### Καλύτερη decision quality
Το ultimate value είναι ένας agent που δεν ξέρει μόνο «πόσο uncertain είναι», αλλά:

> **τι ακριβώς θα χρειαζόταν για να γίνει justified η απόφαση.**

---

# 20. Η μία πρόταση που συνοψίζει όλο το project

> **Existing work increasingly measures whether AI knows that it needs help; we study whether it knows exactly what would be enough.**

---

# Σημείωση ελέγχου πηγών (2026-11-03)

- Το MT-InfoSeek επιβεβαιώθηκε από τη σελίδα της Microsoft (arXiv 2608.14808).
- Τα Rational Metareasoning (2410.05563) και DIAL (2605.06908) υπάρχουν και ταιριάζουν με την περιγραφή.
- Το Ask, Relax, or Act? (2610.03102) βρέθηκε μόνο σε aggregator.
- Το EPRAG υπάρχει, αλλά η ημερομηνία μπορεί να είναι τέλη Αυγούστου.
- Το SURE-Act δεν βρέθηκε.
- Νέο σχετικό paper: **Active Epistemic Control for Query-Efficient Verified Planning** (2026, arXiv 2602.03974). Επιλέγει ανάμεσα σε query στο περιβάλλον και simulation, αλλά δεν είναι benchmark με exact minimal plans ή BOTH/NEITHER. Πρέπει να αναφερθεί.
- Λεπτομέρειες: `NOVELTY_MAP.md`, ενότητα 9.
