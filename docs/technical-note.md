# EU AI Act ontology: proof-of-concept technical note

**Scope and source.** This prototype uses the English EU AI Act consolidated text dated 27 July 2026 (CELEX `02024R1689-20260727`). It records all ten Article 5(1) practice headings, the eight Annex III areas and Article 6 high-risk routes, provider obligations in Article 16, selected deployer duties in Article 26, transparency duties in Article 50, general-purpose AI model duties in Article 53(1), and one authority-governance provision in Article 70. The dated consolidation is a documentation aid; the original Official Journal act is retained locally for comparison. The model is a navigational catalogue, not a legal applicability decision system.

**AI-assisted pipeline.** I supplied bounded Article/Annex passages to a locally served Qwen3.8-27B model through Pi, asking for candidate categories and statements with actor, target, provision, short evidence excerpt, condition and exception. The exact prompts and raw responses are retained in `prompts/pi-qwen/` and `intermediate/pi-qwen/`. Candidate outputs were curated into `ontology/reviewed-records.json`; the mOWL OWLAPI builder consumes only that reviewed file. Review corrected non-contiguous evidence, added four Article 5 headings missing from the first model batch, and retained Article 5(1a), Article 6(3) and other qualifications. Four source-to-query traces are documented separately. Every evidence anchor is checked within its cited Article, but the paraphrases and exceptions are not fully expert-validated.

**Modelling decisions.** `AISystem`, `AIPractice`, `ActorRole`, and their categories are OWL classes. `Obligation`, `Prohibition`, and `ClassificationRule` are classes of *legal statement individuals*. Queryable annotations link those individuals to actor and category class IRIs and store conditions, exceptions and evidence; `prov:wasDerivedFrom` links them to provision individuals, which link to the dated Act version using an ELI IRI. These PROV-O and ELI terms provide lightweight provenance reuse. This is an OWL 2 EL logical core with SPARQL retrieval over annotations. Annex III-listed systems are *not* subclasses of `HighRiskAISystem`, because Article 6(3) allows a derogation. Similarly, Article 5 headings are `Article5ListedPractice` classes, not unconditional prohibited-practice subclasses.

**Competency questions.** The saved queries `queries/cq1.rq`–`cq4.rq` answer: (1) Which Article 5 practices have prohibition statements, with what qualifications and source points? (2) Which Annex III areas appear in the high-risk route, and what is its qualification? (3) Which high-risk duties concern providers versus deployers, and which provisions support them? (4) Which recorded statements have conditions or exceptions? Two abbreviated, executable query examples follow; the saved files add labels and ordering.

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

**Validation and evaluation.** One command, `.venv/bin/python scripts/ontology.py all`, builds RDF/XML via mOWL/OWLAPI, reloads it, checks the OWL 2 EL profile and ELK consistency, tests that Annex III listing does not entail high-risk status, checks the exact source PDF hash and cited-Article evidence anchors, and runs all four SPARQL queries against reviewed examples. Current results: 41 classes, 42 statements, 41 cited provisions, 42/42 evidence anchors matched, four query fixtures passed, zero unsatisfiable named classes. Protégé 5.6.9 also loaded the file with ELK active; the screenshot and walkthrough are in `docs/`. For further evaluation, sample provisions across chapters for expert annotation, then measure category and actor coverage, statement-level precision/recall, citation and condition accuracy, and competency-question answer agreement against that gold set. Recheck logical consistency and query fixtures after every revision.

**Limitations.** Coverage outside the named Articles is selective. Conditions remain text, so neither ELK nor SPARQL determines whether a particular real-world system is legally high-risk or prohibited. A specialist should review the 2026 amendments and all paraphrases before authoritative use.
