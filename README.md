# EU AI Act ontology

A proof-of-concept OWL ontology of the EU AI Act for exploring its system categories, actors, and obligations.

## Status

This project is in design. There is no ontology file or runnable release yet.

## Get the project

```bash
git clone https://github.com/ferzcam/act_ontology.git
cd act_ontology
git switch approach/record-and-query
```

The `approach/record-and-query` branch is the first modelling approach. Other approaches may be developed on separate branches.

## Use and reproduce

There is nothing to run or load in Protégé yet. When the first prototype is available, this README will give the exact steps to generate the ontology, open it in Protégé, run the example SPARQL queries, and repeat the validation checks. Required software versions and source references will be listed alongside those steps.

## Source texts

The source PDFs are kept in the gitignored `data/` directory. Download them after cloning:

```bash
mkdir -p data
curl -fL -o data/eu-ai-act-consolidated-2026-07-27-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A02024R1689-20260727'
curl -fL -o data/eu-ai-act-original-2024-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32024R1689'
sha256sum data/*.pdf
```

The files downloaded on 27 September 2026 had these SHA-256 hashes:

```text
1ccd38d1c78482cf2053b70110115adcc5080700acc8bd7bead8cb3579143ccf  data/eu-ai-act-consolidated-2026-07-27-en.pdf
bba630444b3278e881066774002a1d7824308934f49ccfa203e65be43692f55e  data/eu-ai-act-original-2024-en.pdf
```

The consolidated text is a dated working reference (CELEX 02024R1689-20260727). EUR-Lex states that consolidated texts are documentation aids; the original Official Journal publication (CELEX 32024R1689) is the authentic base act. Keep both identifiers with extracted claims so their source can be checked.

## View the draft design diagram

The current entity-and-relation sketch is in `fig/conceptual-model.tex`. With a TeX installation that includes TikZ, render it from the repository root:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory fig fig/conceptual-model.tex
```

Open `fig/conceptual-model.pdf` to review the figure. The PDF is a local build artifact and is not tracked by Git. The diagram is provisional; it describes the proposed query structure, not a completed ontology.
