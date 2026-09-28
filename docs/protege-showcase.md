# Protégé showcase walkthrough

Verified with Protégé 5.6.9 and its bundled ELK 0.6.0 on 28 September 2026. The [captured class view](protege-showcase.png) shows the ontology loaded and the reasoner active.

This is a short visual demonstration of the [reviewed ontology](../ontology/act-ontology.owl). Build and validate it first with `.venv/bin/python scripts/ontology.py all`; the GUI is not part of the test pipeline.

1. Open `ontology/act-ontology.owl` in Protégé. In **Classes**, expand `AISystem` to show `HighRiskAISystem` and `AnnexIIIListedAISystem` as separate branches. Expand `Article5ListedPractice` under `AIPractice` to show the Article 5 headings. Explain that the absence of a subclass link from Annex III to high-risk, and from listed practice to an unconditional prohibited class, preserves the Act's qualifications.
2. In **Individuals**, inspect `Rule_Article6_2` and `Rule_Article6_3`. Show their `appliesToSystemCategory` links, `hasCondition`, `hasException`, and `prov:wasDerivedFrom` links to Article 6 provisions. Then inspect `Prohibition_Article5_h` for its public-space scope and exception annotation.
3. Compare `Obligation_Article16_e` with `Obligation_Article_26_6_`. Both concern high-risk systems, but have different actor roles and retention wording. Follow each `prov:wasDerivedFrom` link to its provision individual and `inActVersion` link to the dated source.
4. Select **Reasoner → ELK → Start reasoner** if ELK is installed. Show the inferred hierarchy and consistency status. The equivalent programmatic checks, including the negative Annex III/high-risk entailment check, are in `reports/validation.json`.
5. Show the [entity–relation figure](../fig/conceptual-model.tex) beside Protégé. If asked for the four competency questions, run `.venv/bin/python scripts/query.py cq1` through `cq4` in a terminal. The saved SPARQL queries return the same records without a Protégé plugin.

The conditions and exceptions remain textual annotations. Neither Protégé nor the CLI decides whether a real-world system is legally high-risk or prohibited.
