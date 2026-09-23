"""Render the E15 A--D frozen synthesis diagram from the final result indices."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prior_utilization_e15d" / "E15_FROZEN_SYNTHESIS.png"


def box(ax, x, y, w, h, text, face, edge="#334155", size=11, weight="normal"):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        facecolor=face, edgecolor=edge, linewidth=1.25,
    )
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, fontweight=weight, wrap=True, color="#0f172a")


def main():
    fig = plt.figure(figsize=(16, 11), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.text(0.5, 0.965, "E15 frozen synthesis: utilization follows evidence-dimension alignment",
            ha="center", va="center", fontsize=21, fontweight="bold")
    ax.text(0.5, 0.935,
            "Four frozen synthetic studies; arrows state permitted reduction, not universal rules.",
            ha="center", va="center", fontsize=11.5, color="#475569")

    headers = ["Uncertainty anatomy", "Evidence identifies", "Frozen result", "Utilization boundary"]
    xs = [0.06, 0.275, 0.49, 0.735]
    widths = [0.19, 0.19, 0.22, 0.205]
    for x, w, h in zip(xs, widths, headers):
        box(ax, x, 0.865, w, 0.04, h, "#e2e8f0", size=11, weight="bold")

    rows = [
        ("E15-A\nOnset location", "Onset location", "Weak evidence: retain\nonset hypotheses.\nLater: weighting helps.",
         "Reduce onset uncertainty\nonly when onset evidence\nis informative.", "#dbeafe"),
        ("E15-B\nValidity scope", "Scope endpoint\nnot post-scope realization", "Retention helps; endpoint\nweighting harms predictive\naveraging in covered states.",
         "Do not collapse post-scope\nfuture uncertainty using\nendpoint-only evidence.", "#fee2e2"),
        ("E15-C\nInvariant + residual", "Residual shape q\n(still weak overall)", "Retention beats MAP.\nWeighting: harmful ->\nneutral -> beneficial.",
         "Share invariant; reduce\nresidual-shape uncertainty\nwhen q evidence informs q.", "#dcfce7"),
        ("E15-D\nKappa + lambda", "S: kappa strong,\nlambda weak\nJ: lambda greater", "Kappa-selective beats\nuniform in S. D2_S\ninconclusive; MAP costs.",
         "Selective kappa reduction\nsupported; no universal\nban on weak-dimension\nweighting.", "#fef3c7"),
    ]
    ys = [0.69, 0.515, 0.34, 0.165]
    for (anatomy, evidence, result, boundary, color), y in zip(rows, ys):
        box(ax, xs[0], y, widths[0], 0.135, anatomy, color, size=12, weight="bold")
        box(ax, xs[1], y, widths[1], 0.135, evidence, "#f8fafc", size=11)
        box(ax, xs[2], y, widths[2], 0.135, result, "#f8fafc", size=10.5)
        box(ax, xs[3], y, widths[3], 0.135, boundary, "#f8fafc", size=10.5)
        for x0, x1 in [(0.255, 0.27), (0.47, 0.485), (0.72, 0.73)]:
            ax.annotate("", xy=(x1, y + 0.0675), xytext=(x0, y + 0.0675),
                        arrowprops=dict(arrowstyle="->", color="#64748b", lw=1.5))

    box(ax, 0.06, 0.045, 0.275, 0.07,
        "Strongest: premature point commitment\nto unresolved futures can be costly.", "#dbeafe", size=10.5, weight="bold")
    box(ax, 0.365, 0.045, 0.275, 0.07,
        "Moderate: evidence is most useful when\naligned with the uncertainty reduced.", "#dcfce7", size=10.5, weight="bold")
    box(ax, 0.67, 0.045, 0.275, 0.07,
        "Retired: weak dimensions should\nnever be weighted.", "#fee2e2", size=10.5, weight="bold")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=220, bbox_inches="tight")


if __name__ == "__main__":
    main()
