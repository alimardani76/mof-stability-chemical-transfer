# Zn-centred single-water comparison

The V16 Results and Discussion section “When does richer structural information help?” is the natural location for a short follow-on after Figure 5, with coordinates, job settings and sensitivity results in the Supporting Information. Both CoRE ASR models have the same frozen Zn donor-element counts and periodic path summaries. Their coordination angles, ligand identities and local clearance differ. The calculation asks whether those frameworks also differ under one local water perturbation. Both were selected after inspecting inherited scores. The water-score difference of 0.386354 supplies context for the example.

## Cluster models

| Record | Archived coordination at Zn1 | Neutral constrained cluster |
|---|---|---|
| ASR-84-0084 | O3 1.9544 Å, O1 1.9577 Å, N4 2.0230 Å, N1 2.0666 Å | Zn(II), two monodentate pbc carboxylates and two neutral pyridyl-bound pbc-derived ligands. The latter retain benzimidazole N–H and use distal aromatic C–H caps in place of the removed carboxylate groups. C₅₀H₃₄N₁₂O₄Zn, singlet. |
| ASR-152-0152 | O1/O2 1.9520 Å, N1/N2 2.0329 Å | Zn(II), two monodentate naphthalene carboxylates derived from ndc and two neutral full tppa ligands. Each ndc distal carboxylate is replaced by an aromatic C–H cap. C₈₈H₆₂N₈O₄Zn, singlet. |

Each charged ligand carries −1, balancing Zn(II). Image-labelled atom identities and cuts are in `pilot_atom_map.csv` and `cluster_models.json`. The models retain two different N-donor contexts and the intact coordinating carboxylate groups. The C–H caps terminate covalent boundaries. Archived hydrogen assignments are retained on the coordinating ligand fragments. The cluster models use the guest-free archived coordinates. They represent a local finite perturbation of those coordinates, with no assertion about experimental solvent removal or open access through the bulk crystal.

One comparable start per framework uses water donating to a free oxygen of a Zn-bound carboxylate at O···O = 2.90 Å. The corresponding starting water-O–Zn separations are 5.263 Å for A and 3.759 Å for B. The fixed-boundary mask leaves 26 framework atoms mobile in A and 25 in B. Each framework has the same active atom mask in its dry and water-containing model. Three water atoms are also mobile in the hydrated state. The additional water geometries are saved as inputs. See [the cluster visualization](proposed_clusters.png).

## Numerical record

The chosen implementation under test is CP2K Quickstep, closed-shell GPW PBE-D3(BJ) with two-body dispersion, DZVP-MOLOPT-PBE-GTH and GTH-PBE potentials. The isolated-cluster probes use nonperiodic pair lists and the multipole Poisson solver. The 140 Ry trial uses 45 Ry relative cutoff and an SCF tolerance of 10⁻⁶. Higher-grid jobs and all-electron Psi4 feasibility tests have separate outputs. The current validation and calculation statuses, including errors, are in [PROGRESS.md](PROGRESS.md).

The planned electronic adsorption energy is E(wet) − E(dry) − E(H₂O) with the same accepted numerical model and electronic-energy convention. This is a constrained, single-water electronic energy difference. It carries no water exposure conditions, hydrolysis rates, or durability ranking. The four Zn–donor distances and populations should be compared by archived atom and periodic image. Interpretive use of a population change depends on a converged wavefunction and a retained first shell.
