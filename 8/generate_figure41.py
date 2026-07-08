"""
Generates Figure 4.1 - System Module Dependency Diagram as a PNG.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(13, 8))
ax.set_xlim(0, 13)
ax.set_ylim(0, 8)
ax.axis("off")
fig.patch.set_facecolor("#F8F9FA")

def box(ax, x, y, w, h, label, sublabel="", color="#2196F3", textcolor="white"):
    fancy = FancyBboxPatch((x, y), w, h,
                           boxstyle="round,pad=0.1",
                           facecolor=color, edgecolor="white",
                           linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    ax.text(x + w/2, y + h/2 + (0.12 if sublabel else 0),
            label, ha="center", va="center",
            fontsize=9, fontweight="bold", color=textcolor, zorder=4)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22,
                sublabel, ha="center", va="center",
                fontsize=7, color=textcolor, alpha=0.85, zorder=4)

def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#555555",
                                lw=1.4, connectionstyle="arc3,rad=0.0"),
                zorder=2)

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(6.5, 7.55, "Figure 4.1: System Module Dependency Diagram",
        ha="center", va="center", fontsize=12, fontweight="bold", color="#1A237E")
ax.text(6.5, 7.20, "Network Congestion Simulation System – Caleb University FYP",
        ha="center", va="center", fontsize=9, color="#555555")

# ── Layer labels ─────────────────────────────────────────────────────────────
for label, y in [("WEB LAYER", 5.85), ("ORCHESTRATION LAYER", 4.15),
                 ("SIMULATION LAYER", 2.45), ("DATA / UTILITY LAYER", 0.75)]:
    ax.text(0.15, y, label, va="center", fontsize=7.5,
            color="#888888", fontweight="bold", rotation=90)

# Divider lines
for y in [5.3, 3.6, 1.9]:
    ax.plot([0.45, 12.8], [y, y], color="#CCCCCC", lw=1, ls="--", zorder=1)

# ── WEB LAYER ────────────────────────────────────────────────────────────────
box(ax, 1.0, 5.5, 2.2, 0.65, "app.py", "Flask Application", color="#1565C0")
box(ax, 3.5, 5.5, 2.0, 0.65, "templates/", "Jinja2 HTML", color="#1976D2")
box(ax, 5.8, 5.5, 2.0, 0.65, "static/", "CSS + JS", color="#1976D2")
box(ax, 8.1, 5.5, 2.0, 0.65, "simulation_results.db", "SQLite Database", color="#0D47A1")

# ── ORCHESTRATION LAYER ──────────────────────────────────────────────────────
box(ax, 1.0, 3.75, 2.2, 0.65, "main.py", "CLI Entry Point", color="#2E7D32")
box(ax, 3.5, 3.75, 2.0, 0.65, "experiments.py", "Experiment Runner", color="#388E3C")
box(ax, 5.8, 3.75, 2.0, 0.65, "validation.py", "M/M/1 Validation", color="#388E3C")
box(ax, 8.1, 3.75, 2.0, 0.65, "visualisation.py", "Plot Generator", color="#388E3C")
box(ax, 10.3, 3.75, 2.0, 0.65, "config.py", "SimConfig", color="#1B5E20")

# ── SIMULATION LAYER ─────────────────────────────────────────────────────────
box(ax, 2.2, 2.05, 2.2, 0.65, "simulation_engine.py", "SimulationEngine", color="#E65100")
box(ax, 4.7, 2.05, 2.0, 0.65, "network_node.py", "NetworkNode", color="#F57C00")
box(ax, 7.2, 2.05, 2.0, 0.65, "poisson_traffic.py", "PoissonTraffic", color="#F57C00")

# ── DATA / UTILITY LAYER ─────────────────────────────────────────────────────
box(ax, 2.2, 0.35, 2.0, 0.65, "fifo_queue.py", "FIFOQueue", color="#6A1B9A")
box(ax, 4.7, 0.35, 2.0, 0.65, "packet.py", "Packet (dataclass)", color="#7B1FA2")
box(ax, 7.2, 0.35, 2.0, 0.65, "utils.py", "Helper Functions", color="#7B1FA2")

# ── ARROWS – Web → Orchestration ─────────────────────────────────────────────
arrow(ax, 2.1,  5.50, 2.1,  4.40)   # app → main
arrow(ax, 4.5,  5.50, 4.5,  4.40)   # app → experiments
arrow(ax, 6.8,  5.50, 6.8,  4.40)   # app → validation
arrow(ax, 9.1,  5.50, 9.1,  4.40)   # app → visualisation

# ── ARROWS – Orchestration → Simulation ──────────────────────────────────────
arrow(ax, 4.5,  3.75, 3.3,  2.70)   # experiments → engine
arrow(ax, 6.8,  3.75, 3.5,  2.70)   # validation  → engine
arrow(ax, 4.5,  3.75, 5.7,  2.70)   # experiments → node
arrow(ax, 4.5,  3.75, 8.2,  2.70)   # experiments → traffic

# ── ARROWS – Simulation → Data ───────────────────────────────────────────────
arrow(ax, 3.3,  2.05, 3.2,  1.00)   # engine → queue
arrow(ax, 5.7,  2.05, 5.7,  1.00)   # node   → packet
arrow(ax, 8.2,  2.05, 5.9,  1.00)   # traffic→ packet
arrow(ax, 3.3,  2.05, 5.7,  1.00)   # engine → packet

# ── Legend ───────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color="#1565C0", label="Web / Frontend"),
    mpatches.Patch(color="#2E7D32", label="Orchestration"),
    mpatches.Patch(color="#E65100", label="Simulation Core"),
    mpatches.Patch(color="#6A1B9A", label="Data Structures / Utilities"),
]
ax.legend(handles=legend_items, loc="lower right",
          fontsize=8, framealpha=0.9, title="Layer", title_fontsize=8)

plt.tight_layout()
out = "outputs/figure_4_1_module_diagram.png"
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
plt.close(fig)
print(f"Saved: {out}")
