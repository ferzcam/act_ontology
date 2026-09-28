# Four source-to-query traces

We checked these examples against the [English consolidated Act dated 27 July 2026](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02024R1689-20260727). The README records the source PDF's exact hash. The saved SPARQL files retrieve reviewed statements. They do not decide whether a real-world system meets a legal test.

| Question | Example and source check | Query result and modelling decision |
| --- | --- | --- |
| CQ1: prohibited practices | Article 5(1)(h) addresses real-time remote biometric identification in publicly accessible spaces for law enforcement. Article 5(1)(h) lists permitted objectives; Article 5(2)–(5) adds conditions. | `cq1.rq` returns the prohibition statement with its scope and exception text. We place the practice under `Article5ListedPractice` and attach its qualifications to the statement. |
| CQ2: high-risk categories | Article 6(2) covers Annex III-listed systems. Article 6(3) allows a derogation when the listed conditions hold; profiling of natural persons remains high-risk. Under Article 6(4), a provider invoking the derogation must document its assessment and register. | `cq2.rq` returns all eight Annex III areas and the qualification. ELK confirms that `AnnexIIIListedAISystem` is an `AISystem` and does not infer that every such system is `HighRiskAISystem`. |
| CQ3: actor duties | Article 16(e) tells providers to keep automatically generated logs under their control. Article 26(6) tells deployers to keep controlled logs for at least six months, unless applicable law provides otherwise. | `cq3.rq` returns separate provider and deployer records, each linked to `HighRiskAISystem` and its own provision. The records preserve their different retention terms. |
| CQ4: conditions and exceptions | Article 26(6) qualifies the deployer duty by control, intended purpose, minimum retention period and applicable law. Article 6(3) sets out the high-risk derogation. | `cq4.rq` returns these statement annotations with source references. The exceptions remain text that readers can inspect. |

The [validation report](../reports/validation.json) records the OWL profile, ELK entailment and consistency checks, cited-Article evidence matches and query results. These four traces test selected records. Expert legal review remains necessary for the Act's full provisions and their interactions.
