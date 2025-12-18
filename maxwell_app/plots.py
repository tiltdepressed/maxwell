import os
import numpy as np


def snapshot_history(sim):
    return {
        "t": np.array(sim.time_history, dtype=float),
        "h": np.array(sim.h_history, dtype=float),
        "v": np.array(sim.v_history, dtype=float),
        "ep": np.array(sim.ep_history, dtype=float),
        "ek_t": np.array(sim.ek_trans_history, dtype=float),
        "ek_r": np.array(sim.ek_rot_history, dtype=float),
    }


def save_plots(history, folder="plots"):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if len(history["t"]) < 2:
        return

    os.makedirs(folder, exist_ok=True)

    t = history["t"]
    h = history["h"]
    v = history["v"]
    ep = history["ep"]
    ek_t = history["ek_t"]
    ek_r = history["ek_r"]

    def style_ax(ax):
        ax.set_facecolor("#1a1a1a")
        ax.figure.set_facecolor("#1a1a1a")
        ax.tick_params(colors="#e0e0e0")
        for spine in ax.spines.values():
            spine.set_color("#e0e0e0")
        ax.xaxis.label.set_color("#e0e0e0")
        ax.yaxis.label.set_color("#e0e0e0")
        ax.title.set_color("#e0e0e0")

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, h, color="#ff4444", label="h(t)")
    ax.set_xlabel("t, s")
    ax.set_ylabel("h, m")
    ax.set_title("Высота h(t)")
    style_ax(ax)
    ax.grid(True, color="#444444")
    fig.tight_layout()
    fig.savefig(os.path.join(folder, "height.jpg"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, v, color="#4488ff", label="v(t)")
    ax.set_xlabel("t, s")
    ax.set_ylabel("v, m/s")
    ax.set_title("Скорость v(t)")
    style_ax(ax)
    ax.grid(True, color="#444444")
    fig.tight_layout()
    fig.savefig(os.path.join(folder, "velocity.jpg"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, ep, color="#44ff44", label="Ep")
    ax.plot(t, ek_t, color="#ffff44", label="Ek поступ.")
    ax.plot(t, ek_r, color="#ff8844", label="Ek вращ.")
    ax.set_xlabel("t, s")
    ax.set_ylabel("E, Дж")
    ax.set_title("Энергии во времени")
    ax.legend()
    style_ax(ax)
    ax.grid(True, color="#444444")
    fig.tight_layout()
    fig.savefig(os.path.join(folder, "energy.jpg"), dpi=150)
    plt.close(fig)
