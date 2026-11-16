"""OpenPKFlow reproducible software demonstration; NOT a ranolazine prediction.

Uses only the package's bundled example. Never connects a package demonstration
profile to FDA recall cases or claims release criteria/causal effects.
"""
import argparse
import importlib.resources
import json
import math
from pathlib import Path


def probe() -> dict:
    import pandas as pd
    import numpy as np
    import openpkflow
    from openpkflow.dissolution.models import fit_dissolution_models

    example = importlib.resources.files('openpkflow.datasets').joinpath('example_dissolution.csv')
    data = pd.read_csv(example)
    required = {'formulation','batch','time','percent_released'}
    if set(data.columns) != required or data.empty or data[list(required)].isna().any().any():
        raise ValueError('bundled example columns/data invalid')
    if not data['percent_released'].between(0,100).all():
        raise ValueError('example percent released out of range')
    out = {'status':'software_demonstration_only','source':'openpkflow bundled example_dissolution.csv',
           'version':openpkflow.__version__, 'product':'not_ranolazine',
           'profile_units':{'time':'package API documents minutes; example CSV does not state unit','release':'percent'},
           'model_set':['zero_order','first_order','higuchi','weibull','hixson_crowell'],
           'profiles':{},'uncertainty':{'calibration':'not_established','reason':'example has no independent validation or per-vessel dissolution records'},
           'caveats':['not FDA recall measurements','batch IDs in example cannot be assumed to be independent vessels',
                      'AICc is within-profile fit, not validated predictive performance',
                      'no drug/product-specific objective or approved criterion']}
    for name, subset in data.groupby('formulation',sort=True):
        means = subset.groupby('time',sort=True)['percent_released'].mean()
        result = fit_dissolution_models(means.index.to_numpy(),means.to_numpy(),name,models=out['model_set'])
        fits = [f for f in result.fits if f.converged and math.isfinite(f.aicc)]
        if not fits:
            raise ValueError('no converged, finite model fits')
        out['profiles'][name] = {'timepoints':len(means), 'batches':subset['batch'].nunique(),
            'best_by_aicc':min(fits,key=lambda f:f.aicc).model_name,
            'model_fits':[{'name':f.model_name,'aicc':f.aicc,'r_squared':f.r_squared,
                'in_sample_rmse_percent':float(np.sqrt(np.mean((means.to_numpy()-f.predict(means.index.to_numpy()))**2)))} for f in fits]}
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    result = probe()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':result['status'],'product':result['product'],'version':result['version'],
                      'best_by_aicc':{k:v['best_by_aicc'] for k,v in result['profiles'].items()},'out':str(args.out)}))


if __name__ == '__main__': main()
