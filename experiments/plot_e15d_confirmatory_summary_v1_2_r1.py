#!/usr/bin/env python3
"""Render frozen E15-D R1 contrast summary."""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results'/'prior_utilization_e15d'/'confirmatory_v1_2_r1'
SOURCES=[('D1_S','E15D_D1_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv','mean_D1'),('D2_S','E15D_D2S_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv','mean_contrast'),('D2_J','E15D_D2J_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv','mean_contrast'),('D3_S','E15D_D3S_CELLWISE_PAIRED_BOOTSTRAP_V1_2_R1.csv','mean_contrast')]
OUT=BASE/'E15D_CONFIRMATORY_CONTRAST_SUMMARY_V1_2_R1.png'
def main():
 rows=[]
 for label,name,key in SOURCES:
  with (BASE/name).open(newline='',encoding='utf-8') as f: row=next(csv.DictReader(f))
  rows.append((label,float(row[key]),float(row['ci_2_5']),float(row['ci_97_5'])))
 fig,ax=plt.subplots(figsize=(7.4,4.2)); ax.axvline(0,color='0.35',lw=1.1)
 for i,(label,mean,lo,hi) in enumerate(rows): ax.errorbar(mean,i,xerr=[[mean-lo],[hi-mean]],fmt='o',capsize=5,lw=2,color='#1f77b4')
 ax.set(yticks=range(len(rows)),yticklabels=[r[0] for r in rows],xlabel='Mean paired NRMSE contrast (95% paired-bootstrap CI)',title='E15-D v1.2 R1 frozen confirmatory contrasts')
 ax.invert_yaxis(); ax.grid(axis='x',color='0.9'); fig.tight_layout(); fig.savefig(OUT,dpi=200)
if __name__=='__main__': main()
