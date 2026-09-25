"""
Matplotlib helpers that turn the fuzzy system's internal arrays into
simple charts for the Streamlit UI. Kept separate from fuzzy_system.py
so the fuzzy math stays free of any plotting/UI code.
"""

import matplotlib.pyplot as plt

from fuzzy_system import (
    ATTENDANCE_MFS,
    ATTENDANCE_UNIVERSE,
    PERFORMANCE_MFS,
    PERFORMANCE_UNIVERSE,
    SCORE_MFS,
    SCORE_UNIVERSE,
    STUDY_MFS,
    STUDY_UNIVERSE,
)

_INPUT_CONFIG = {
    "study_hours": ("Study Hours (per day)", STUDY_UNIVERSE, STUDY_MFS),
    "attendance_percentage": ("Attendance (%)", ATTENDANCE_UNIVERSE, ATTENDANCE_MFS),
    "test_score_percentage": ("Last Test Score (%)", SCORE_UNIVERSE, SCORE_MFS),
}


def plot_input_membership(variable_key, crisp_value):
    """Plot the membership curves for one input variable with the crisp value marked."""
    title, universe, mf_dict = _INPUT_CONFIG[variable_key]

    fig, ax = plt.subplots(figsize=(4.2, 3))
    for label, (fn, params) in mf_dict.items():
        ax.plot(universe, fn(universe, params), label=label.capitalize())

    ax.axvline(crisp_value, color="black", linestyle="--", linewidth=1)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel("Membership degree", fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    return fig


def plot_output_membership(aggregated_curve, score):
    """Plot the aggregated fuzzy output set with the defuzzified centroid marked."""
    fig, ax = plt.subplots(figsize=(6, 3.2))

    for label, (fn, params) in PERFORMANCE_MFS.items():
        ax.plot(
            PERFORMANCE_UNIVERSE,
            fn(PERFORMANCE_UNIVERSE, params),
            linestyle=":",
            linewidth=1,
            label=f"{label.capitalize()} (reference)",
        )

    ax.fill_between(
        PERFORMANCE_UNIVERSE,
        aggregated_curve,
        alpha=0.4,
        color="tab:blue",
        label="Aggregated output",
    )
    ax.axvline(
        score, color="red", linestyle="--", linewidth=1.5, label=f"Centroid = {score:.1f}"
    )

    ax.set_title("Output: Academic Performance Score", fontsize=10)
    ax.set_ylabel("Membership degree", fontsize=8)
    ax.set_ylim(-0.05, 1.05)
    ax.tick_params(labelsize=8)
    ax.legend(fontsize=7)
    fig.tight_layout()
    return fig
