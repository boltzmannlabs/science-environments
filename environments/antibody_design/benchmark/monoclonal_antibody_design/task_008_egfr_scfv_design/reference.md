# Benchmark: EGFR scFv design

**Task:** [EGFR: Reference-Guided scFv Design](../../../tasks/monoclonal_antibody_design/task_008_egfr_scfv_design.md)

## Published computational reference

Source: [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv). The saved 10 November 2026 snapshot contains 21 EGFR records. The table reports one minimum–maximum range per metric across those records; domain scores have their own scope.

| Metric | Minimum | Maximum | Scope |
| --- | --- | --- | --- |
| Molecular weight (Da) | 25714.1494 | 25929.3209 | Whole sequence |
| Isoelectric point (pH) | 4.969796944 | 7.80791111 | Whole sequence |
| ESMFold pLDDT (0–100) | 82.39856752 | 83.71150302 | Whole structure |
| ESMFold pLDDT (0–100) | 83.75149336 | 86.74728535 | Source-annotated domains |
| ProteinMPNN original-sequence score | 1.4344 | 1.4958 | Sequence scored on its ESMFold prediction |
| ProteinMPNN redesigned-sequence score | 0.7567 | 0.78516 | Separate source redesign calculation |
| ProteinMPNN sequence recovery (raw) | 0.49875 | 0.52987 | Source redesign calculation |

ProteinMPNN scores retain the source scale; lower negative log likelihood is preferred. The redesigned-sequence scores and recovery describe the catalog's own redesign calculation. They are separate from scoring the submitted sequences on their own predicted backbones in this task.

## Matched reference and input structure

The sequence comparator is cetuximab scFv [vast-bear-marble](https://proteinbase.com/proteins/vast-bear-marble). The prepared construct contains VH (119 residues), a 15-residue `(G4S)3` linker, and VL (107 residues), for 241 residues total. Its VH/VL pair matches the Fv extracted from the experimental [1YY9 cetuximab–EGFR complex](https://www.rcsb.org/structure/1YY9). The saved EGFR input contains 613 residues.

The editable Chothia CDR positions in each variable domain are VH 26–32, 52–56 and 98–108; VL 24–34, 50–56 and 89–97. Framework residues and linker are protected. The run's matched reference scores are reported in [comparison.md](comparison.md), separately from the catalog snapshot.

## Reference records

- [vast-bear-marble](https://proteinbase.com/proteins/vast-bear-marble)
- [scarlet-seal-granite](https://proteinbase.com/proteins/scarlet-seal-granite)
- [bright-crane-jade](https://proteinbase.com/proteins/bright-crane-jade)
- [green-boar-bronze](https://proteinbase.com/proteins/green-boar-bronze)
- [lunar-bear-dust](https://proteinbase.com/proteins/lunar-bear-dust)
- [lunar-zebra-topaz](https://proteinbase.com/proteins/lunar-zebra-topaz)
- [mellow-shark-ruby](https://proteinbase.com/proteins/mellow-shark-ruby)
- [shy-shark-cypress](https://proteinbase.com/proteins/shy-shark-cypress)
- [silent-ibis-reed](https://proteinbase.com/proteins/silent-ibis-reed)
- [soft-jaguar-fern](https://proteinbase.com/proteins/soft-jaguar-fern)
- [soft-seal-cypress](https://proteinbase.com/proteins/soft-seal-cypress)
- [strong-quail-topaz](https://proteinbase.com/proteins/strong-quail-topaz)
- [young-heron-pearl](https://proteinbase.com/proteins/young-heron-pearl)
- [solid-bison-topaz](https://proteinbase.com/proteins/solid-bison-topaz)
- [mellow-ram-reed](https://proteinbase.com/proteins/mellow-ram-reed)
- [mellow-ram-sand](https://proteinbase.com/proteins/mellow-ram-sand)
- [quick-hawk-opal](https://proteinbase.com/proteins/quick-hawk-opal)
- [radiant-otter-marble](https://proteinbase.com/proteins/radiant-otter-marble)
- [rough-quail-granite](https://proteinbase.com/proteins/rough-quail-granite)
- [strong-mole-onyx](https://proteinbase.com/proteins/strong-mole-onyx)
- [vast-boar-granite](https://proteinbase.com/proteins/vast-boar-granite)
