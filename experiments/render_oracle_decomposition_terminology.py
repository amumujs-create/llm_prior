#!/usr/bin/env python3
"""Terminology-only PPT renderer from frozen Oracle Decomposition results."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'results'/'oracle_decomposition_v1'/'results.json').read_text())
fig,axs=plt.subplots(1,3,figsize=(14,4),constrained_layout=True)
names={'regime_change':'Regime change','emergent_curvature':'Emergent curvature','asymptotic_bound':'Asymptotic bound'}
labels=[('no_prior','no prior','#777'),('family_oracle','generative-family oracle','#cc4c4c'),('parameter_oracle','parameter oracle','#3978b8'),('full_information_oracle','full-information oracle','#43a86b')]
for ax,f in zip(axs,names):
 z=sorted([q for q in d['summary'] if q['family']==f],key=lambda q:q['observability'])
 for key,label,color in labels: ax.plot([q['observability'] for q in z],[q[key] for q in z],'o-',label=label,color=color)
 ax.set(title=names[f],xlabel='observability',ylabel='far-OOD RMSE'); ax.legend(fontsize=7)
fig.suptitle('Oracle decomposition: family truth is not realization knowledge')
fig.savefig(ROOT/'figures'/'fig09_oracle_decomposition_terminology.png',dpi=220)
