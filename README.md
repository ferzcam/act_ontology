# EU AI Act ontology

A proof-of-concept OWL 2 EL ontology for exploring EU AI Act categories, actors, cited obligations, prohibitions and classification rules. This branch implements a **record-and-query** approach: OWL classes represent categories; cited legal statements are individuals linked to those categories by queryable annotations. Protégé is useful for showcasing, while the build, reasoning and four competency queries run programmatically.

## Get the project

```bash
git clone https://github.com/ferzcam/act_ontology.git
cd act_ontology
git switch approach/record-and-query
```

The `approach/record-and-query` branch is the first modelling approach. Other approaches can be developed on separate branches.

## Requirements and source text

Use Python 3.10, Java 21, `uv`, and Poppler's `pdftotext`. Install the pinned lightweight runtime for mOWL's OWLAPI wrapper, ELK and RDFLib:

```bash
uv venv .venv --python 3.10
uv pip install --python .venv/bin/python --no-deps -r requirements.txt
```

The `--no-deps` option avoids mOWL's unused machine-learning dependency stack for this OWLAPI-only workflow; the needed transitive packages are pinned explicitly. The source PDFs belong in the gitignored `data/` directory:

```bash
mkdir -p data
curl -fL -o data/eu-ai-act-consolidated-2026-07-27-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A02024R1689-20260727'
curl -fL -o data/eu-ai-act-original-2024-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32024R1689'
sha256sum -c sources.sha256
```

The downloaded files used for this build have SHA-256 hashes (also in `sources.sha256`):

```text
1ccd38d1c78482cf2053b70110115adcc5080700acc8bd7bead8cb3579143ccf  data/eu-ai-act-consolidated-2026-07-27-en.pdf
bba630444b3278e881066774002a1d7824308934f49ccfa203e65be43692f55e  data/eu-ai-act-original-2024-en.pdf
```

If `sha256sum -c` fails, stop before building. EUR-Lex may respond to command-line downloads with an HTTP 202 bot challenge and an empty file. Open the same two official links in a browser, save the PDFs under the exact filenames in `data/`, and repeat the hash check. The PDFs remain gitignored.

The consolidated text is a dated documentation aid (CELEX `02024R1689-20260727`); the original Official Journal publication (CELEX `32024R1689`) is the authentic base act. The builder checks the exact consolidated PDF hash before validation.

## Build, test and query without Protégé

```bash
.venv/bin/python scripts/ontology.py all
.venv/bin/python scripts/query.py cq1
.venv/bin/python scripts/query.py cq2
.venv/bin/python scripts/query.py cq3
.venv/bin/python scripts/query.py cq4
```

`all` builds `ontology/act-ontology.owl` from `ontology/reviewed-records.json` using the mOWL OWLAPI wrapper, then reloads the saved file. It checks the OWL 2 EL profile, ELK consistency and unsatisfiable classes, source hashes and evidence spans within their cited Articles, and all four RDFLib SPARQL queries against `queries/expected.json`. The full machine-readable result is `reports/validation.json`; a failed check makes the command exit nonzero. Use `build` or `validate` in place of `all` to run either stage alone. The `.owl` and validation report are tracked as reviewable outputs. The [four source-to-query traces](docs/trace-examples.md) show a targeted legal audit. The [technical note](docs/technical-note.md) explains the competency questions, scope, modelling choices and limitations. To render the submission note as a one-page PDF (optional, requires Pandoc and LaTeX):

```bash
pandoc docs/technical-note.md -o docs/technical-note.pdf --pdf-engine=pdflatex -V geometry:margin=0.5in -V fontsize=10pt
```

The generated PDF is gitignored; the Markdown note is the tracked source.

## Showcase in Protégé

Open `ontology/act-ontology.owl` in Protégé (verified with version 5.6.9 and bundled ELK 0.6.0). In the **Classes** view, expand `AISystem`, `AIPractice`, `ActorRole` and `LegalStatement`. In **Individuals**, inspect `Obligation_Article16_a`, `Rule_Article6_3` or a `Provision_*` individual to see its labels, citations and category links. Choose **Reasoner → ELK → Start reasoner** to view the inferred hierarchy and consistency status. The [showcase walkthrough](docs/protege-showcase.md) gives the exact example records to display. The CLI above reproduces the checks without opening Protégé. Protégé's SPARQL tab can run the saved `.rq` files if a suitable plugin is installed; the supplied CLI requires no plugin.

## Extraction audit and diagram

The `prompts/pi-qwen/` and `intermediate/pi-qwen/` directories record bounded prompts and raw outputs from the local Pi `borg/qwen3.8-27b` model. The [review log](intermediate/review.md) identifies corrections. The deterministic builder reads only reviewed records, so the model is not needed to reproduce the ontology or tests.

The entity–relation diagram source is `fig/conceptual-model.tex`. Render it with a TeX installation including TikZ:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory fig fig/conceptual-model.tex
```

The rendered PDF is a local build artifact and is gitignored.
