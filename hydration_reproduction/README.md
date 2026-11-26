# V17 hydration-response reproduction (Figures S17 and S18)

This directory adds the approved hydration extension's figure reproduction and source evidence. Browse `figures/`, `integration_evidence/`, and the Python scripts for the exact published figure assets, CIFs, tables and plotting code. The full calculation inputs, optimized coordinates and referenced output logs are in the losslessly split archive.

## Reproduce from a fresh checkout

From the repository root:

```bash
python hydration_reproduction/unpack_evidence.py --out ../P1_v17_hydration
cd ../P1_v17_hydration/hydration_reproduction
python -m pip install -r requirements.txt
python check_evidence.py integration_evidence --out verification
python build_figures.py integration_evidence --out figures
python check_new_figures.py
```

The unpacker checks the complete archive SHA-256, all contained file hashes and ZIP integrity. It will not overwrite an existing extraction directory. The extracted README explains the full archive and optional xTB replay. Figure regeneration uses archived geometries, not new electronic-structure calculations. The archive includes rejected attempts and the LA2-1 evidence omitted from the final figure; it excludes publisher PDFs, internal peer review, manuscripts, unrelated legacy plots and optimizer trajectory logs. The original source DOIs and literature benchmark tables remain included. The experimental MOF-303 CIF is not available; the published computational geometry and reported diffraction distances are distinguished.
