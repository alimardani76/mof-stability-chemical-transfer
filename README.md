# MOF stability: saved results and figure reproduction

This repository reproduces published numerical summaries and six figures from saved MOF stability-transfer results. It does not independently reproduce the original experiments, train models, or extract descriptors. Numerical findings and scientific interpretations are preserved.

## Install and reproduce

Use Python 3.11 and run these commands from the repository root (PowerShell or a Unix shell):

```text
python -m venv .venv
```

Activate with `.venv\Scripts\Activate.ps1` on Windows or `source .venv/bin/activate` on Unix, then run:

```text
python -m pip install -r figure_sources/requirements.txt
python scripts/manifest.py
python scripts/reproduce.py --isolated
python scripts/make_tables.py --check
```

The reproduction command regenerates all six figures and three tables, then validates scientific values, labels, panel assignments, dimensions and output completeness. It denies reads of sibling project folders and disables network access. GitHub Actions runs these same commands. To run individual stages:

```text
python figure_sources/make_figures.py
python scripts/make_tables.py
python scripts/check_figures.py
```

`SHA256_MANIFEST.csv` covers distributed files; verify it **before** regeneration. Rendering can differ across platforms despite fixed package versions. `data/aggregate/INPUT_SHA256.csv` is the selected scientific-input slice of the supplied original manifest and remains verifiable after regeneration. After intentional package changes, rebuild the distribution manifest with `python scripts/manifest.py --write`.

## Figure mapping

All main figures use `figure_sources/make_figures.py`. There is one output set: `figure_sources/figures/{pdf,svg,png}/Figure_01` through `Figure_06`, with the corresponding extension. Paths below are relative to `figure_sources/`.

| Figure / function | Retained inputs | Panels |
| --- | --- | --- |
| 1 / `make1` | `assets/concept_top.png`; definitions in script | A: B/C/L/I information blocks; B: evaluation design |
| 2 / `make2` | `source_data/family_water_ladder.csv` | A–D: ASR element, FSR element, ASR topology, FSR topology; absolute rankings and paired increments |
| 3 / `make3` | `source_data/family_conditional_contributions.csv` | A: constitution controls; B: properties versus identity; C: conditional context/attachment |
| 4 / `make4` | `source_data/local_examples.csv`, `source_data/local_graphs.json`, `assets/{helped,harmed}_illustration.png` | A: ASR-1180-1180; B: ASR-1065-1065 |
| 5 / `make5` | `source_data/structural_summary.csv` | G/N/V/H/J summaries; separate SOAP kernel comparison |
| 6 / `make6` | `source_data/family_N_paths.csv` | A: parent/child ranks; B/C: ASR/FSR family changes and conditional intervals |

`figure_sources/figure_definitions.json` provides machine-readable inputs and expected panel labels.

The three PDFs `figures/support/support_examples_01.pdf` through `support_examples_03.pdf` are **retained reference outputs**, not locally regenerated outputs. They show all six result-selected examples. Their original rendering code is [phase_10_figures.py](https://github.com/alimardani76/mof_stablity_transfer/blob/65725ae2b8b7f25d15ba08e68632198cc0ddc954/figure_sources/originals/phase_10_figures.py), using [illustrative_examples.csv](https://github.com/alimardani76/mof_stablity_transfer/blob/65725ae2b8b7f25d15ba08e68632198cc0ddc954/figure_sources/panel_data/phase_07/illustrative_examples.csv) and the six record-specific JSON files in [selected_geometry](https://github.com/alimardani76/mof_stablity_transfer/tree/65725ae2b8b7f25d15ba08e68632198cc0ddc954/figure_sources/selected_geometry). Local condensed examples/graphs retain their scientific content; exact original layout regeneration is unavailable in this package.

## Table mapping

`scripts/make_tables.py` adapts the supported table-generation portions of the pinned [upstream generator](https://github.com/alimardani76/mof_stablity_transfer/blob/65725ae2b8b7f25d15ba08e68632198cc0ddc954/figure_sources/originals/phase_10_numbers.py). It deterministically regenerates standalone table fragments and checks every displayed value against the saved numerical macros.

| Output | Input in `data/aggregate/` | Reproduction scope |
| --- | --- | --- |
| `generated/water_ladder.tex` | `figure_02_ladder.csv` | Reformat saved equal-family summaries; family means also checked against local family data |
| `generated/structural.tex` | `figure_04_structural.csv` | Reformat saved means and favourable-family counts |
| `generated/endpoint_ladders.tex` | `figure_05_endpoints.csv` | Reformat saved activation/thermal endpoint summaries |
| `generated/subblocks.tex` | Saved result using `generated/numbers.tex` | Full regeneration unavailable: local family data omit L-given-I; the other five contrasts are numerically checked |
| `generated/numbers.tex` | Saved upstream numerical macro snapshot | Full regeneration unavailable: complete original summary inputs and full-precision claim ledger are absent |

Table fragments use `\Num` from `numbers.tex` and standard `booktabs` commands if embedded in a LaTeX document. No LaTeX installation is required for reproduction or validation.

## Scientific provenance and limitations

Upstream research: https://github.com/alimardani76/mof_stablity_transfer at commit `65725ae2b8b7f25d15ba08e68632198cc0ddc954`. `figure_sources/source_data/lineage.txt` records condensation and rounding. `data/aggregate/SOURCE_FILE_MANIFEST.csv` preserves original source-path metadata; use its `pinned_tree_sha` with `repository_path` to locate the frozen source, rather than its historical moving-branch URLs. Geometry blob identities and derived example checks are retained in the `fig3_*` files.

Targets are inherited model estimates, **not experimental stability measurements**. Family means are unweighted. ASR/FSR are distinct preparation forms, not independent experimental replications; exact AllNodes labels do not establish certified graph novelty. Conditional 95% intervals reuse saved fitted models and omit refit/full model uncertainty. Leave-one-family-out mean ranges are descriptive sensitivity ranges, not confidence intervals. SOAP kernel ridge and the other learners have different comparison definitions.

The three artwork assets are conceptual illustrations, not authenticated structure renderings. Saved atom-labelled graphs are 2D periodic-image contact projections with unresolved CIF-to-record identity; they do not establish bond orders, mechanisms or hydrolysis pathways. Examples were selected after inspecting errors. Rounded summary tables cannot recover upstream observations, complete predictions or uncertainty calculations. This package reproduces saved summaries and graphics without asserting independent experimental or model reproduction.
