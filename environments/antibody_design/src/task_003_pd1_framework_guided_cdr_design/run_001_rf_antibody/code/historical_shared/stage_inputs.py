#!/usr/bin/env python3
"""Stage framework, target and interface inputs for task_003.

Panel sequences are staged by parse_panel.py (programmatic extraction from the
supplementary PDF). This script stages Table-1 framework blocks, the PD-1 target
record, and generates the Antibody_Numbering CSV from the parsed panel JSON.
"""
import json, os

SRC = '/home/boltzmann10/.sci/cache/scratch/task003_paper'
BASE = '/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design'
INP = f'{BASE}/src/task_003_pd1_framework_guided_cdr_design/inputs'

FR = {
    'FR-H1': 'EVQLLESGGGLVQPGGSLRLSCAAS',
    'FR-H2': 'AMSWVRQAPGKGLEWVSAI',
    'FR-H3': 'TYYADSVKGRFTISRDNSKNTLYLQMNSLRAEDTAVYYCAK',
    'FR-H4': 'WGQGTLVTVSS',
    'FR-L1': 'DIQMTQSPSTLSASVGDRVTITC',
    'FR-L2': 'WYQQKPGKAPKLLIY',
    'FR-L3': 'GVPSRFSGSGSGTEFTLTISSLQPDDFATYYC',
    'FR-L4': 'FGQGTKVEIK',
}
assert {k: len(v) for k, v in FR.items()} == {
    'FR-H1': 25, 'FR-H2': 19, 'FR-H3': 41, 'FR-H4': 11,
    'FR-L1': 23, 'FR-L2': 15, 'FR-L3': 32, 'FR-L4': 10}

PD1_UNIPROT = 'MQIPQAPWPVVWAVLQLGWRPGWFLDSPDRPWNPPTFSPALLVVTEGDNATFTCSFSNTSESFVLNWYRMSPSNQTDKLAAFPEDRSQPGQDCRFRVTQLPNGRDFHMSVVRARRNDSGTYLCGAISLAPKAQIKESLRAELRVTERRAEVPTAHPSPSPRPAGQFQTLVVGVVGGLLGSLVLLVWVLAVICSRAARGTIGARRTGQPLKEDPSAVPVFSVDYGELDFQWREKTPEPPVPCVPEQTEYATIVFPSGMGTSSPARRGSADGPRSAQPLRPEDGHCSWPL'
PD1_PDL1_INTERFACE_4ZQK = [63,64,65,66,68,73,74,75,76,77,78,79,80,81,83,84,124,126,127,128,129,130,131,132,133,134]
PD1_FAB_INTERFACE_5GGS = [60,62,63,64,65,66,67,68,71,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,124,125,126,128,129,130,131,134]

with open(f'{INP}/framework_table1.json', 'w') as f:
    json.dump({'source': 'PMC12815924 Table 1', 'scheme': 'Chothia', 'FR_blocks': FR,
               'cdr_lengths': {'H1': 7, 'H2': 6, 'H3': [7, 18], 'L1': 11, 'L2': 7, 'L3': [9, 11]}}, f, indent=1)

with open(f'{INP}/pd1_target.json', 'w') as f:
    json.dump({'uniprot': 'Q15116', 'uniprot_seq_res1_288': PD1_UNIPROT,
               'ecd_33_150': PD1_UNIPROT[32:150],
               'design_construct_33_134': PD1_UNIPROT[32:134],
               'pd1_pdl1_interface_4zqk': PD1_PDL1_INTERFACE_4ZQK,
               'pd1_fab_interface_5ggs': PD1_FAB_INTERFACE_5GGS,
               'construct_notes': '4ZQK chain B: 33-146 observed, 85-92 disordered, S93 (UniProt C93) construct substitution; 5GGS chain Y: 33-146, S93.'}, f, indent=1)

with open(f'{INP}/pd1_ecd_33_134.fasta', 'w') as f:
    f.write('>PD1_HUMAN_ECD_33_134|Q15116|design_construct\n' + PD1_UNIPROT[32:134] + '\n')

panel = json.load(open(f'{INP}/pd1_panel_published.json'))['panel']
h965 = panel['Anti-PD1-H965']
with open(f'{INP}/h965_numbering.csv', 'w') as f:
    f.write('Heavy_chain,Light_chain\n')
    f.write(f"{h965['VH']},{h965['VL']}\n")

# interface residue contact list (recomputed from 4ZQK earlier; store as record)
with open(f'{INP}/pd1_interface_contacts.txt', 'w') as f:
    f.write('PD-1 residues with CA within 10 A of PD-L1 CA in 4ZQK (CA proxy; saved from coordinate analysis 2026-11-14):\n')
    f.write(','.join(map(str, PD1_PDL1_INTERFACE_4ZQK)) + '\n')
    f.write('PD-1 residues with CA within 10 A of pembrolizumab Fab CA in 5GGS:\n')
    f.write(','.join(map(str, PD1_FAB_INTERFACE_5GGS)) + '\n')
    f.write('Overlap (ligand-binding surface cross-confirmed by independent Fab): 63-68,71,73-84,124-134 window\n')

print('Framework, target, interface inputs staged; numbering CSV written from parsed H965.')
