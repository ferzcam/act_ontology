# Extraction review log

The raw `pi`/Qwen responses in this directory are candidate extractions. The OWL builder reads only `ontology/reviewed-records.json`.

- Article 16: retained the twelve points (a)–(l), and checked their short evidence spans against the dated consolidated PDF. The raw point (k) excerpt had a PDF line-break soft hyphen; text normalization handles it.
- Article 26: retained seven representative paragraphs. The raw paragraph 7 evidence elided text between “inform” and “that”; the reviewed anchor was replaced with a contiguous source span.
- Article 5: the first raw batch covered six of ten headings. Points (e)–(h) were read from the PDF and added manually. Points (ba)/(bb) are present in the 2026 consolidation; qualifications in Article 5(1a)/(1b) were added to the reviewed records. Article 5 practices are descriptive classes and statements, not unconditional case decisions.
- Article 6: encoded the two routes and Article 6(3) derogation as cited classification statements. Annex III classes sit under `AnnexIIIListedAISystem`, not `HighRiskAISystem`.
- Annex III: retained the eight top-level areas, labelled as listed use-case areas so they are not mistaken for all systems in a sector.
- Articles 50 and 53: retained selected/point-level duties and their prominent exceptions; checked against the consolidated passage. Article 70(1) was represented with `MemberState` as obligated actor, correcting the raw output's authority-role conflation.

The automated evidence-match check confirms that each short excerpt occurs within its cited Article in the exact-hash PDF; expert review is still needed to assess every paraphrase and exception.

## Targeted source-to-query audit

The [four traced examples](../docs/trace-examples.md) led to three corrections: Article 5 headings moved from an unconditional `ProhibitedPractice` hierarchy to `Article5ListedPractice`; Article 6(1b)/(4) qualifications were made explicit; and the Article 26(6) retention period and Article 5(1)(h) public-space scope were clarified. The validator now checks that ELK does not infer Annex III listing to be universally high-risk.

Protégé 5.6.9 loaded the generated OWL file in a temporary virtual display. The bundled ELK 0.6.0 reasoner started and remained active; a cropped [screenshot](../docs/protege-showcase.png) records the separate `Article5ListedPractice`, `AnnexIIIListedAISystem`, and `HighRiskAISystem` branches. The equivalent automated checks remain the authoritative repeatable validation.
