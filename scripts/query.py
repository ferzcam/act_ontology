"""Run a saved competency-question SPARQL query against the generated OWL file."""
from __future__ import annotations
import argparse
from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('query', choices=('cq1','cq2','cq3','cq4'))
args = parser.parse_args()
graph = Graph()
graph.parse(ROOT / 'ontology' / 'act-ontology.owl', format='xml')
result = graph.query((ROOT / 'queries' / f'{args.query}.rq').read_text())
print('\t'.join(str(var) for var in result.vars))
for row in result:
    print('\t'.join(str(value) if value is not None else '' for value in row))
