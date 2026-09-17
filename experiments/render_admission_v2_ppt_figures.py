#!/usr/bin/env python3
"""Presentation-only renderer from frozen admission-v2 results; does not rerun models."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results'/'admission_v2_identifiability_sweep_v2'/'results.json').read_text())
label={
 'num__x0':'boundary slope change','num__x1':'boundary slope decay','num__x2':'change-point BIC advantage',
 'num__x3':'post-change support','num__x4':'curvature sign evidence','num__x5':'asymptote proximity',
 'num__x6':'parameter precision','num__x7':'covariance conditioning','num__x8':'fit stability','num__x9':'v1 pseudo-OOD score',
 'fam__x10_regime_change':'candidate: regime change','fam__x10_emergent_curvature':'candidate: emergent curvature','fam__x10_asymptotic_bound':'candidate: asymptotic bound'}
top=data['feature_coefficients'][:10][::-1]
names=[label.get(z['feature'],z['feature']) for z in top]; vals=[z['coefficient'] for z in top]
fig,ax=plt.subplots(figsize=(8.6,5.2),constrained_layout=True)
ax.barh(names,vals,color=['#3978b8' if v>0 else '#cc4c4c' for v in vals]); ax.axvline(0,color='#555',lw=1)
ax.set(title='Admission-v2: evidence associated with useful prior admission',xlabel='standardized logistic coefficient (train seeds only)')
fig.savefig(ROOT/'figures'/'fig06_v2_evidence_coefficients_labeled.png',dpi=220)

fig,ax=plt.subplots(figsize=(12,3.6),constrained_layout=True); ax.axis('off')
boxes=[('Candidate prior','matching structural family'),('Boundary evidence','slope change / decay'),('Structure evidence','BIC, curvature, bound'),('Identifiability','precision, condition, stability'),('Admission-v2','P(useful | evidence) ≥ .50')]
for i,(title,detail) in enumerate(boxes):
 x=.02+i*.197; ax.text(x+.08,.58,title+'\n',ha='center',va='center',fontsize=12,weight='bold',bbox=dict(boxstyle='round,pad=.65',fc='#eaf2f8' if i<4 else '#d5f5e3',ec='#3978b8')); ax.text(x+.08,.30,detail,ha='center',va='center',fontsize=9)
 if i<4: ax.annotate('',xy=(x+.19,.58),xytext=(x+.16,.58),arrowprops=dict(arrowstyle='->',lw=1.8,color='#65737e'))
ax.text(.5,.06,'Training label: held-out-tail utility sign, used only on development train seeds. Test seeds evaluate FAR and coverage.',ha='center',fontsize=10,style='italic')
fig.savefig(ROOT/'figures'/'fig07_admission_v2_logic.png',dpi=220)
