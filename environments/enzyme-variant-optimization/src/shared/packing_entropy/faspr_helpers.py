"""Reversible formatting-only consumer for FASPR's repeated atom serials."""
def unique_pdb_serial_view(text):
    lines=text.splitlines(keepends=True); mapping=[]; serial=0
    for i,line in enumerate(lines):
        if line.startswith(('ATOM  ','HETATM','TER   ')):
            if line.startswith(('ATOM  ','HETATM')) and len(line.rstrip('\r\n'))<78:
                raise ValueError('short native atom record')
            serial+=1
            if serial>99999: raise ValueError('PDB serial field overflow')
            mapping.append({'line_index':i,'old_serial_field':line[6:11],'new_serial':serial})
            lines[i]=line[:6]+f'{serial:5d}'+line[11:]
    if not mapping: raise ValueError('no native atom records')
    view=''.join(lines); restored=view.splitlines(keepends=True)
    for item in mapping:
        i=item['line_index']; restored[i]=restored[i][:6]+item['old_serial_field']+restored[i][11:]
    if ''.join(restored)!=text: raise ValueError('serial normalization not reversible')
    return view,mapping
