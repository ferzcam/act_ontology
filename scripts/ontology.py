"""Build and validate the EU AI Act proof-of-concept ontology.

The reviewed JSON records are the only inputs to the OWL builder. Raw local-LLM
outputs are retained separately for audit and never consumed by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import mowl
from rdflib import Graph, URIRef

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "ontology" / "reviewed-records.json"
OWL = ROOT / "ontology" / "act-ontology.owl"
QUERIES = ROOT / "queries"
REPORT = ROOT / "reports" / "validation.json"
SOURCE_PDF = ROOT / "data" / "eu-ai-act-consolidated-2026-07-27-en.pdf"
SOURCE_SHA256 = "1ccd38d1c78482cf2053b70110115adcc5080700acc8bd7bead8cb3579143ccf"
NS = "https://github.com/ferzcam/act_ontology#"
PROV = "http://www.w3.org/ns/prov#wasDerivedFrom"
DCT_ID = "http://purl.org/dc/terms/identifier"


def iri(local: str) -> str:
    return NS + local


def provision_id(reference: str) -> str:
    return "Provision_" + re.sub(r"[^A-Za-z0-9]+", "_", reference).strip("_")


def records() -> dict:
    data = json.loads(RECORDS.read_text())
    class_ids = {item["id"] for item in data["classes"]}
    statement_ids = set()
    for item in data["statements"]:
        if item["id"] in statement_ids:
            raise ValueError(f"Duplicate statement: {item['id']}")
        statement_ids.add(item["id"])
        if item["type"] not in class_ids:
            raise ValueError(f"Unknown statement type: {item['type']}")
        for field in ("actor_roles", "system_categories", "practice_categories"):
            for target in item.get(field, []):
                if target not in class_ids:
                    raise ValueError(f"Unknown {field} target: {target}")
        for required in ("label", "description", "source_ref", "evidence"):
            if not item.get(required):
                raise ValueError(f"Missing {required} in {item['id']}")
    return data


def init_jvm() -> None:
    mowl.init_jvm("2g")


def build(data: dict) -> dict:
    from java.util import HashSet
    from org.semanticweb.owlapi.formats import RDFXMLDocumentFormat
    from org.semanticweb.owlapi.model import IRI
    from mowl.owlapi import OWLAPIAdapter

    adapter = OWLAPIAdapter()
    manager = adapter.owl_manager
    factory = adapter.data_factory
    ontology = adapter.create_ontology(data["ontology_iri"])

    def add(axiom) -> None:
        manager.addAxiom(ontology, axiom)

    def j_iri(value: str):
        return IRI.create(value)

    def declare(entity) -> None:
        add(factory.getOWLDeclarationAxiom(entity))

    annotations = {
        key: factory.getOWLAnnotationProperty(j_iri(iri(key)))
        for key in ("appliesToActorRole", "appliesToSystemCategory", "concernsPractice", "hasCondition", "hasException", "evidenceExcerpt", "sourceReference")
    }
    annotations["dctermsIdentifier"] = factory.getOWLAnnotationProperty(j_iri(DCT_ID))
    for prop in annotations.values():
        declare(prop)

    derived = adapter.create_object_property(PROV)
    in_version = adapter.create_object_property(iri("inActVersion"))
    for prop in (derived, in_version):
        declare(prop)

    def annotate(subject: str, prop, value: str, *, link: bool = False) -> None:
        obj = j_iri(value) if link else factory.getOWLLiteral(value)
        add(factory.getOWLAnnotationAssertionAxiom(prop, j_iri(subject), obj))

    def label_comment(subject: str, label: str, description: str) -> None:
        annotate(subject, factory.getRDFSLabel(), label)
        annotate(subject, factory.getRDFSComment(), description)

    classes = {}
    for item in data["classes"]:
        entity = adapter.create_class(iri(item["id"]))
        classes[item["id"]] = entity
        declare(entity)
        label_comment(iri(item["id"]), item["label"], item["description"])
        if item.get("source_ref"):
            annotate(iri(item["id"]), annotations["sourceReference"], item["source_ref"])

    for item in data["classes"]:
        if item.get("parent"):
            add(adapter.create_subclass_of(classes[item["id"]], classes[item["parent"]]))

    # Disjointness here concerns the kinds of entities, not risk classifications.
    for left, right in (("ActorRole", "AISystem"), ("AIPractice", "AISystem")):
        pair = HashSet()
        pair.add(classes[left])
        pair.add(classes[right])
        add(factory.getOWLDisjointClassesAxiom(pair))

    version_iri = data["source"]["eli_iri"]
    version = adapter.create_individual(version_iri)
    declare(version)
    add(adapter.create_class_assertion(classes["ActVersion"], version))
    label_comment(version_iri, data["source"]["label"], data["source"]["description"])
    annotate(version_iri, annotations["dctermsIdentifier"], data["source"]["celex"])

    provisions = {}
    def provision(reference: str):
        if reference not in provisions:
            p_iri = iri(provision_id(reference))
            entity = adapter.create_individual(p_iri)
            declare(entity)
            add(adapter.create_class_assertion(classes["LegalProvision"], entity))
            label_comment(p_iri, reference, f"Provision in {data['source']['label']}")
            annotate(p_iri, annotations["dctermsIdentifier"], reference)
            add(adapter.create_object_property_assertion(in_version, entity, version))
            provisions[reference] = entity
        return provisions[reference]

    for item in data["statements"]:
        s_iri = iri(item["id"])
        entity = adapter.create_individual(s_iri)
        declare(entity)
        add(adapter.create_class_assertion(classes[item["type"]], entity))
        label_comment(s_iri, item["label"], item["description"])
        for field, prop in (("actor_roles", "appliesToActorRole"), ("system_categories", "appliesToSystemCategory"), ("practice_categories", "concernsPractice")):
            for target in item.get(field, []):
                annotate(s_iri, annotations[prop], iri(target), link=True)
        for field, prop in (("condition", "hasCondition"), ("exception", "hasException"), ("evidence", "evidenceExcerpt")):
            if item.get(field):
                annotate(s_iri, annotations[prop], item[field])
        add(adapter.create_object_property_assertion(derived, entity, provision(item["source_ref"])))

    OWL.parent.mkdir(parents=True, exist_ok=True)
    manager.saveOntology(ontology, RDFXMLDocumentFormat(), j_iri(OWL.resolve().as_uri()))
    # OWLAPI emits whitespace-only lines; normalize them for a clean tracked artifact.
    OWL.write_text("\n".join(line.rstrip() for line in OWL.read_text().splitlines()).rstrip() + "\n")
    return {"classes": len(data["classes"]), "statements": len(data["statements"]), "provisions": len(provisions), "owl_path": str(OWL)}


def normalized(text: str) -> str:
    text = re.sub("\u00ad\\s*\\n\\s*", "", text)
    text = text.replace("\u00ad", "").replace("’", "'").replace("‘", "'")
    text = re.sub(r"-\s*\n\s*", "", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def validate(data: dict) -> dict:
    from java.io import File
    from org.semanticweb.elk.owlapi import ElkReasonerFactory
    from org.semanticweb.owlapi.apibinding import OWLManager
    from org.semanticweb.owlapi.profiles import OWL2ELProfile

    if not SOURCE_PDF.is_file():
        raise FileNotFoundError(f"Download the source PDF first: {SOURCE_PDF}")
    digest = hashlib.sha256(SOURCE_PDF.read_bytes()).hexdigest()
    if digest != SOURCE_SHA256:
        raise ValueError(f"Source PDF hash differs: {digest}")

    # Validate the serialized file, not only the in-memory ontology used to build it.
    manager = OWLManager.createOWLOntologyManager()
    ontology = manager.loadOntologyFromOntologyDocument(File(str(OWL)))
    profile = OWL2ELProfile().checkOntology(ontology)
    violations = [str(x) for x in profile.getViolations()]
    reasoner = ElkReasonerFactory().createReasoner(ontology)
    try:
        consistent = bool(reasoner.isConsistent())
        unsatisfiable = sorted(str(x.getIRI()) for x in reasoner.getUnsatisfiableClasses().getEntitiesMinusBottom())
    finally:
        reasoner.dispose()

    graph = Graph()
    graph.parse(OWL, format="xml")
    expected = json.loads((QUERIES / "expected.json").read_text())
    query_results = {}
    query_ok = True
    for name, specification in expected.items():
        query = (QUERIES / f"{name}.rq").read_text()
        rows = [tuple(str(value) if value is not None else "" for value in row) for row in graph.query(query)]
        references = {cell for row in rows for cell in row if cell.startswith(("Article ", "Annex "))}
        missing = sorted(set(specification["required_references"]) - references)
        passed = len(rows) >= specification["minimum_rows"] and not missing
        query_ok &= passed
        query_results[name] = {"rows": rows, "row_count": len(rows), "missing_required_references": missing, "passed": passed}

    extracted = subprocess.run(["pdftotext", "-layout", str(SOURCE_PDF), "-"], capture_output=True, text=True, check=True).stdout
    source_text = normalized(extracted)
    missed_evidence = [item["id"] for item in data["statements"] if normalized(item["evidence"]) not in source_text]
    annotation_complete = all(item.get("label") and item.get("description") and item.get("source_ref") for item in data["statements"])
    statement_count = len(data["statements"])
    cited_refs = {item["source_ref"] for item in data["statements"]}
    report = {
        "source_celex": data["source"]["celex"],
        "source_sha256": digest,
        "owl2_el_profile": bool(profile.isInProfile()),
        "profile_violations": violations,
        "consistent": consistent,
        "unsatisfiable_named_classes": unsatisfiable,
        "triple_count": len(graph),
        "class_count": len(data["classes"]),
        "statement_count": statement_count,
        "cited_provision_count": len(cited_refs),
        "annotation_completeness": annotation_complete,
        "evidence_matches": statement_count - len(missed_evidence),
        "evidence_match_rate": (statement_count - len(missed_evidence)) / statement_count if statement_count else 0,
        "missing_evidence": missed_evidence,
        "queries": query_results,
    }
    report["passed"] = bool(profile.isInProfile()) and consistent and not unsatisfiable and annotation_complete and not missed_evidence and query_ok
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "validate", "all"))
    args = parser.parse_args()
    data = records()
    init_jvm()
    if args.action in ("build", "all"):
        print(json.dumps(build(data), indent=2))
    if args.action in ("validate", "all"):
        report = validate(data)
        print(json.dumps({key: report[key] for key in ("passed", "owl2_el_profile", "consistent", "class_count", "statement_count", "cited_provision_count", "evidence_match_rate")}, indent=2))
        if not report["passed"]:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
