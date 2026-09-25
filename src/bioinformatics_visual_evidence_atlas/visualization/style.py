"""Publication export and colour-blind-aware styling."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

OKABE_ITO = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442", "#000000"]


def palette(names: list[str]) -> dict[str, str]:
    return {name: OKABE_ITO[index % len(OKABE_ITO)] for index, name in enumerate(names)}


def new_figure(width: float = 7.2, height: float = 4.8):
    fig, ax = plt.subplots(figsize=(width, height), dpi=120)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    return fig, ax


def style_axes(ax, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, fontsize=12, fontweight="bold", pad=8)
    ax.set_xlabel(xlabel, fontsize=10, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=10, fontweight="bold")
    ax.tick_params(labelsize=9)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight("bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def legend(ax, **kwargs) -> None:
    ax.legend(frameon=False, prop={"size": 9, "weight": "normal"}, **kwargs)


def save_figure(fig, folder: Path, stem: str) -> dict[str, str]:
    folder.mkdir(parents=True, exist_ok=True)
    paths = {}
    for suffix, dpi in (("png", 300), ("svg", None), ("pdf", None)):
        path = folder / f"{stem}.{suffix}"
        if dpi:
            fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
        else:
            fig.savefig(path, bbox_inches="tight", facecolor="white")
        paths[suffix] = str(path)
    plt.close(fig)
    return paths
