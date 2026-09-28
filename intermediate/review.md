# Extraction review log

The raw `pi`/Qwen responses in this directory contain candidate extractions. The OWL builder reads only `ontology/reviewed-records.json`.

- Article 16: We retained all twelve points (a)–(l) and checked their evidence excerpts against the dated consolidated PDF. The raw point (k) excerpt contained a PDF line-break soft hyphen, which text normalization handles.
- Article 26: We retained seven representative paragraphs. The raw paragraph 7 excerpt omitted text between “inform” and “that”, so we replaced it with a contiguous source excerpt.
- Article 5: The first model batch covered six of ten headings. We read points (e)–(h) in the PDF and added them manually. We retained points (ba) and (bb) from the 2026 consolidation and recorded the qualifications in Article 5(1a) and (1b). Practice classes describe listed activities; the linked statements retain legal conditions and exceptions.
- Article 6: We recorded both high-risk routes and the Article 6(3) derogation as cited classification statements. Annex III classes sit under `AnnexIIIListedAISystem`; Article 6 conditions determine high-risk status.
- Annex III: We retained all eight top-level areas and labelled them as listed use-case areas. Each class represents specified use cases within a sector.
- Articles 50 and 53: We retained selected duties and their prominent exceptions after checking the consolidated text. For Article 70(1), we assigned the obligation to `MemberState`, correcting the raw model output's authority-role conflation.

The automated evidence check finds every short excerpt within its cited Article in the exact-hash PDF. Expert review remains necessary for the paraphrases and exceptions.

## Targeted source-to-query audit

The [four traced examples](../docs/trace-examples.md) led to three corrections. We moved Article 5 headings to `Article5ListedPractice` because each prohibition has its own qualifications. We recorded the Article 6(1b) and 6(4) qualifications and clarified the Article 26(6) retention period and Article 5(1)(h) public-space scope. The validator checks that ELK does not infer high-risk status from Annex III listing alone.

Protégé 5.6.9 loaded the generated OWL file in a temporary virtual display. Its bundled ELK 0.6.0 reasoner remained active. The [screenshot](../docs/protege-showcase.png) shows separate `Article5ListedPractice`, `AnnexIIIListedAISystem` and `HighRiskAISystem` branches. The automated checks provide repeatable validation.
