# EU AI Act ontology

A proof-of-concept OWL 2 EL ontology of EU AI Act categories, actors and cited legal statements. The current **record-and-query** approach represents categories as OWL classes and obligations, prohibitions and classification rules as individuals linked to those classes by queryable annotations. Protégé is for showcasing; construction, reasoning checks and SPARQL queries run from the command line.

The validated version is on `main`. The `approach/record-and-query` branch preserves its development history for comparison with possible future approaches.

## 1. Clone and prepare the environment

```bash
git clone https://github.com/ferzcam/act_ontology.git
cd act_ontology
uv python install 3.10
uv venv .venv --python 3.10
uv pip install --python .venv/bin/python --no-deps -r requirements.txt
```

Requirements: Git, `uv`, Java 21, `pdftotext` (Poppler), `curl` and `sha256sum`. The six pinned packages in `requirements.txt` are the lightweight runtime for mOWL's OWLAPI wrapper, ELK and RDFLib. `--no-deps` avoids mOWL's unused machine-learning dependency stack; the needed dependencies are pinned explicitly. Check `java -version` before building. Optional tools for later steps are Pi with local `borg/qwen3.8-27b`, Pandoc, a LaTeX installation with TikZ, and Protégé 5.6.9.

## 2. Obtain and verify the Act PDFs

The source PDFs belong in gitignored `data/`. Download the dated consolidated text and the original Official Journal act:

```bash
mkdir -p data
curl -fL -o data/eu-ai-act-consolidated-2026-07-27-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A02024R1689-20260727'
curl -fL -o data/eu-ai-act-original-2024-en.pdf 'https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=CELEX%3A32024R1689'
sha256sum -c sources.sha256
```

Both lines of the checksum check must say `OK`. EUR-Lex can return an empty HTTP 202 bot-challenge response to `curl`; `curl -fL` may still exit successfully. If the hashes fail, open the same two links in a browser, save the PDFs under the exact names above, and rerun `sha256sum -c sources.sha256`. Do not run validation with unverified files. The consolidated text (CELEX `02024R1689-20260727`) is a dated documentation aid; the original publication (CELEX `32024R1689`) is the authentic base act. The builder checks the consolidated PDF's exact hash.

## 3. Build and validate without Protégé

```bash
.venv/bin/python scripts/ontology.py all
```

This builds `ontology/act-ontology.owl` deterministically from the tracked `ontology/reviewed-records.json`, then reloads the serialized OWL file. Validation checks the OWL 2 EL profile, ELK consistency and unsatisfiable classes, source-PDF hash and evidence spans within their cited Articles, the intended Annex III/high-risk non-entailment, and all four SPARQL competency queries against `queries/expected.json`. A failed check exits nonzero. The full result is `reports/validation.json`; look for `"passed": true`. The reviewed prototype has 41 classes, 42 legal statements and query row counts of 10, 8, 19 and 32. You can run `build` or `validate` instead of `all` for either stage alone.

Run the saved competency queries directly:

```bash
.venv/bin/python scripts/query.py cq1
.venv/bin/python scripts/query.py cq2
.venv/bin/python scripts/query.py cq3
.venv/bin/python scripts/query.py cq4
```

The [one-page technical note](docs/technical-note.md) gives the four questions, two shorter SPARQL examples, model scope and evaluation proposal. The [four source-to-query traces](docs/trace-examples.md) explain representative results and their legal qualifications.

## 4. Re-run the local AI extraction (optional)

The final ontology can be rebuilt without the model. To repeat the AI-assisted candidate extraction, have the local Pi provider `borg` and model `qwen3.8-27b` available. The bounded prompts are in `prompts/pi-qwen/`; the original raw responses are preserved in `intermediate/pi-qwen/`. Run all prompts into a gitignored comparison directory:

```bash
mkdir -p reproduced/pi-qwen
for input in prompts/pi-qwen/*-prompt.txt; do
  name="${input##*/}"
  output="${name%-prompt.txt}-raw.txt"
  pi --provider borg --model qwen3.8-27b --offline \
    --no-extensions --no-skills --no-prompt-templates --no-themes \
    --no-session --no-tools -p "@${input}" > "reproduced/pi-qwen/${output}"
done
```

Model responses may differ between runs. Compare the new candidates with the preserved raw outputs and the exact source provisions. The [review log](intermediate/review.md) documents corrections; `ontology/reviewed-records.json` is the curated, version-controlled input used by the builder. Editing that file is a human review step, not an automatic conversion from model output.

## 5. Render the note and diagram (optional)

With Pandoc and LaTeX, render the submission note as a one-page PDF:

```bash
pandoc docs/technical-note.md -o docs/technical-note.pdf --pdf-engine=pdflatex -V geometry:margin=0.5in -V fontsize=10pt
```

With TikZ installed, render the entity–relation diagram:

```bash
pdflatex -interaction=nonstopmode -halt-on-error -output-directory fig fig/conceptual-model.tex
```

The generated PDFs are gitignored; the Markdown and TikZ sources are tracked.

## 6. Showcase in Protégé (optional)

Open `ontology/act-ontology.owl` in Protégé. In **Classes**, expand `AISystem`, `AIPractice`, `ActorRole` and `LegalStatement`; in **Individuals**, inspect `Rule_Article6_3`, `Prohibition_Article5_h`, or `Obligation_Article16_e` and follow their provision links. Choose **Reasoner → ELK → Start reasoner**. Protégé 5.6.9 with bundled ELK 0.6.0 loaded and reasoned over this file; the [screenshot and walkthrough](docs/protege-showcase.md) show the result. The command-line checks above reproduce the validation without Protégé or a SPARQL plugin.
