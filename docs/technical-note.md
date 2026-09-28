# EU AI Act ontology: proof-of-concept technical note

**Scope and source.** The prototype uses the English EU AI Act consolidated text dated 27 July 2026 (CELEX `02024R1689-20260727`). It records all ten Article 5(1) practice headings, eight Annex III areas, and both Article 6 high-risk routes. It also records provider obligations in Article 16, selected deployer duties in Article 26, transparency duties in Article 50, general-purpose AI model duties in Article 53(1), and one authority-governance provision in Article 70. The dated consolidation documents amendments; the original Official Journal act provides the authentic base text. The ontology supports navigation through cited rules. It does not decide whether a real-world case falls under them.

**AI-assisted pipeline.** I sent bounded Article and Annex passages to a locally served Qwen3.8-27B model through Pi. The prompts asked for candidate categories and statements with actors, targets, provisions, short evidence excerpts, conditions and exceptions. The repository retains the exact [prompts](../prompts/pi-qwen/) and [raw responses](../intermediate/pi-qwen/). I reviewed the candidates against the Act and saved accepted records in `ontology/reviewed-records.json`. The mOWL OWLAPI builder reads only that file. Review replaced a non-contiguous evidence excerpt, added four Article 5 headings absent from the first model batch, and preserved the qualifications in Article 5(1a), Article 6(3) and other provisions. The [source-to-query traces](trace-examples.md) show four checks. An automated test locates each evidence excerpt within its cited Article. A legal expert has not reviewed every paraphrase and exception.

**Modelling decisions.** The ontology represents `AISystem`, `AIPractice`, `ActorRole` and their categories as OWL classes. It represents each obligation, prohibition and classification rule as an individual of a legal statement class. Queryable annotations link statements to actor and category class IRIs and record conditions, exceptions and evidence. `prov:wasDerivedFrom` links each statement to a provision individual; `inActVersion` links that provision to the dated Act via an ELI IRI. These PROV-O and ELI terms record provenance. The logical core fits OWL 2 EL, while SPARQL retrieves the annotations. Article 6(3) allows an Annex III derogation, so the ontology does not assert `AnnexIIIListedAISystem` as a subclass of `HighRiskAISystem`. Article 5 practice headings are `Article5ListedPractice` classes because their prohibition statements carry conditions and exceptions.

**Competency questions.** The four saved queries ask: (1) Which Article 5 practices have prohibition statements, qualifications and source points? (2) Which Annex III areas appear in the high-risk route, and what qualifies that route? (3) Which high-risk duties concern providers or deployers, and which provisions support them? (4) Which statements record conditions or exceptions? Two executable examples follow. The saved files in `queries/` add labels and ordering.

```sparql
PREFIX act: <https://github.com/ferzcam/act_ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?practice ?article WHERE {
  ?s a act:Prohibition; act:concernsPractice ?practice;
     prov:wasDerivedFrom ?p.
  ?p dct:identifier ?article.
}
```

```sparql
PREFIX act: <https://github.com/ferzcam/act_ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?actor ?article WHERE {
  ?s a act:Obligation; act:appliesToActorRole ?actor;
     act:appliesToSystemCategory act:HighRiskAISystem;
     prov:wasDerivedFrom ?p.
  ?p dct:identifier ?article.
}
```

**Validation and evaluation.** Run `.venv/bin/python scripts/ontology.py all` to build and reload RDF/XML through mOWL/OWLAPI. The command checks the OWL 2 EL profile, ELK consistency, Annex III non-entailment, the source PDF hash, cited-Article evidence excerpts and four SPARQL queries. The current report records 41 classes, 42 statements, 41 cited provisions, 42/42 matched evidence excerpts, four passing query fixtures and zero unsatisfiable named classes. Protégé 5.6.9 loaded the file with ELK active; see the [screenshot and walkthrough](protege-showcase.md). For further evaluation, ask experts to annotate a sample of provisions across chapters. Measure category and actor coverage, statement precision and recall, citation and condition accuracy, and agreement on competency-question answers against that reference set. Repeat consistency and query checks after each revision.

**Limitations.** Coverage outside the named Articles is selective. Conditions remain text. Neither ELK nor SPARQL decides whether a particular system is legally high-risk or prohibited. A legal specialist should review the 2026 amendments and all paraphrases before authoritative use.
