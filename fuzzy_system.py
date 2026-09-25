"""
A genuine Mamdani-style Fuzzy Inference System (FIS) for academic
performance, implemented from first principles with NumPy so every
step is visible and explainable line by line:

    1. Universes of discourse + membership functions
    2. Fuzzification        (crisp input  -> membership degrees)
    3. Fuzzy rule base
    4. Rule evaluation       (fuzzy AND = min)
    5. Aggregation           (fuzzy OR / rule combination = max)
    6. Defuzzification       (centroid method -> crisp output)

No if-else decision logic is used anywhere in this module. All
reasoning happens through fuzzy membership degrees and the two
classic fuzzy set operators: min() for AND, max() for combining rules.
"""

from dataclasses import dataclass

import numpy as np

# ---------------------------------------------------------------------------
# STEP 1: Universes of discourse (the range each variable can take)
# ---------------------------------------------------------------------------
STUDY_UNIVERSE = np.linspace(0, 12, 241)         # hours/day
ATTENDANCE_UNIVERSE = np.linspace(0, 100, 201)   # %
SCORE_UNIVERSE = np.linspace(0, 100, 201)        # %
PERFORMANCE_UNIVERSE = np.linspace(0, 100, 201)  # output score


# ---------------------------------------------------------------------------
# STEP 1 (continued): Membership function shapes
# ---------------------------------------------------------------------------
def trimf(x, params):
    """Triangular membership function. params = (a, b, c): rises a->b, falls b->c."""
    a, b, c = params
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    if b > a:
        idx = (x >= a) & (x <= b)
        y[idx] = (x[idx] - a) / (b - a)
    if c > b:
        idx = (x >= b) & (x <= c)
        y[idx] = np.maximum(y[idx], (c - x[idx]) / (c - b))
    return np.clip(y, 0.0, 1.0)


def trapmf(x, params):
    """Trapezoidal membership function. params = (a, b, c, d): rises a->b, flat b->c, falls c->d."""
    a, b, c, d = params
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)
    if b > a:
        idx = (x >= a) & (x < b)
        y[idx] = (x[idx] - a) / (b - a)
    y[(x >= b) & (x <= c)] = 1.0
    if d > c:
        idx = (x > c) & (x <= d)
        y[idx] = (d - x[idx]) / (d - c)
    return np.clip(y, 0.0, 1.0)


def degree_at(value, mf_func, params):
    """Membership degree of ONE crisp value - this is fuzzification for a single number."""
    return float(mf_func(np.array([value]), params)[0])


# ---------------------------------------------------------------------------
# Linguistic variable definitions: label -> (shape function, corner points)
# Kept as plain dictionaries so they are easy to read and tweak for a viva.
# ---------------------------------------------------------------------------
STUDY_MFS = {
    "low": (trapmf, (0, 0, 1, 3)),
    "medium": (trimf, (1, 4, 7)),
    "high": (trapmf, (5, 8, 12, 12)),
}

ATTENDANCE_MFS = {
    "poor": (trapmf, (0, 0, 40, 60)),
    "average": (trimf, (40, 65, 85)),
    "good": (trapmf, (70, 85, 100, 100)),
}

SCORE_MFS = {
    "low": (trapmf, (0, 0, 35, 50)),
    "medium": (trimf, (35, 55, 75)),
    "high": (trapmf, (60, 80, 100, 100)),
}

PERFORMANCE_MFS = {
    "low": (trapmf, (0, 0, 25, 45)),
    "medium": (trimf, (30, 50, 70)),
    "high": (trapmf, (55, 75, 100, 100)),
}


# ---------------------------------------------------------------------------
# STEP 2: Fuzzification
# ---------------------------------------------------------------------------
def fuzzify(value, mf_dict):
    """Convert one crisp input into a dict of {linguistic label: membership degree}."""
    return {label: degree_at(value, fn, params) for label, (fn, params) in mf_dict.items()}


# ---------------------------------------------------------------------------
# STEP 3 & 4: Fuzzy rule base and rule evaluation
# ---------------------------------------------------------------------------
@dataclass
class RuleResult:
    rule_id: str
    description: str
    strength: float
    consequent: str


def evaluate_rules(study_deg, attend_deg, score_deg):
    """
    Evaluate every rule in the fuzzy rule base.

    Each rule evaluates its antecedents with the standard fuzzy AND operator (min).
    The rules are structured across three logical tiers:
      - High Performance: strong test scores reinforced by good attendance/study hours,
        or medium scores backed by both high attendance and high study hours.
      - Medium Performance / Moderate Risk: balanced average performance, or cases
        where a strong metric is compromised by a weak metric (e.g. high score with
        poor attendance, or a low score cushioned by diligent attendance and study).
      - Low Performance / High Risk: poor scores combined with poor or average habits,
        or poor attendance and low study hours regardless of test score.

    Aggregation combines rules sharing the same consequent with fuzzy OR (max).
    """

    def rule(rule_id, description, degrees, consequent):
        return RuleResult(rule_id, description, min(degrees), consequent)

    results = [
        # --- High Performance (Low Risk) ---
        rule("R1", "Score=High AND Attendance=Good -> Performance=High",
             [score_deg["high"], attend_deg["good"]], "high"),
        rule("R2", "Score=High AND StudyHours=High -> Performance=High",
             [score_deg["high"], study_deg["high"]], "high"),
        rule("R3", "Score=High AND Attendance=Average AND StudyHours=Medium -> Performance=High",
             [score_deg["high"], attend_deg["average"], study_deg["medium"]], "high"),
        rule("R4", "Score=Medium AND Attendance=Good AND StudyHours=High -> Performance=High",
             [score_deg["medium"], attend_deg["good"], study_deg["high"]], "high"),

        # --- Medium Performance (Moderate Risk) ---
        rule("R5", "Score=Medium AND Attendance=Average -> Performance=Medium",
             [score_deg["medium"], attend_deg["average"]], "medium"),
        rule("R6", "Score=Medium AND StudyHours=Medium -> Performance=Medium",
             [score_deg["medium"], study_deg["medium"]], "medium"),
        rule("R7", "Score=Medium AND Attendance=Good -> Performance=Medium",
             [score_deg["medium"], attend_deg["good"]], "medium"),
        rule("R8", "Score=Medium AND StudyHours=Low -> Performance=Medium",
             [score_deg["medium"], study_deg["low"]], "medium"),
        rule("R9", "Score=Medium AND Attendance=Poor -> Performance=Medium",
             [score_deg["medium"], attend_deg["poor"]], "medium"),
        # Risk compromise: strong exam score compromised by poor attendance or low study hours
        rule("R10", "Score=High AND Attendance=Poor -> Performance=Medium",
             [score_deg["high"], attend_deg["poor"]], "medium"),
        rule("R11", "Score=High AND StudyHours=Low -> Performance=Medium",
             [score_deg["high"], study_deg["low"]], "medium"),
        # Effort cushion: low exam score mitigated by high study hours and good attendance
        rule("R12", "Score=Low AND Attendance=Good AND StudyHours=High -> Performance=Medium",
             [score_deg["low"], attend_deg["good"], study_deg["high"]], "medium"),

        # --- Low Performance (High Risk) ---
        rule("R13", "Score=Low AND Attendance=Poor -> Performance=Low",
             [score_deg["low"], attend_deg["poor"]], "low"),
        rule("R14", "Score=Low AND StudyHours=Low -> Performance=Low",
             [score_deg["low"], study_deg["low"]], "low"),
        rule("R15", "Score=Low AND Attendance=Average -> Performance=Low",
             [score_deg["low"], attend_deg["average"]], "low"),
        rule("R16", "Score=Low AND StudyHours=Medium -> Performance=Low",
             [score_deg["low"], study_deg["medium"]], "low"),
        rule("R17", "Score=Medium AND Attendance=Poor AND StudyHours=Low -> Performance=Low",
             [score_deg["medium"], attend_deg["poor"], study_deg["low"]], "low"),
        rule("R18", "Attendance=Poor AND StudyHours=Low -> Performance=Low",
             [attend_deg["poor"], study_deg["low"]], "low"),
    ]

    aggregated = {"low": 0.0, "medium": 0.0, "high": 0.0}
    for res in results:
        aggregated[res.consequent] = max(aggregated[res.consequent], res.strength)

    return results, aggregated


# ---------------------------------------------------------------------------
# STEP 5 & 6: Aggregation of output sets + Defuzzification (centroid method)
# ---------------------------------------------------------------------------
def defuzzify(aggregated_strengths):
    """
    Clip each output membership curve at its rule strength (this is
    "implication"), take the point-wise maximum of the three clipped
    curves (this is "aggregation"), then compute the centroid of the
    resulting shape - the standard Mamdani defuzzification method.
    """
    clipped_curves = []
    for label, (fn, params) in PERFORMANCE_MFS.items():
        mf_curve = fn(PERFORMANCE_UNIVERSE, params)
        clipped_curves.append(np.minimum(mf_curve, aggregated_strengths[label]))

    aggregated_curve = np.maximum.reduce(clipped_curves)

    if aggregated_curve.sum() == 0:
        # No rule fired at all (shouldn't normally happen) - neutral fallback.
        return 50.0, aggregated_curve

    score = float(
        np.sum(PERFORMANCE_UNIVERSE * aggregated_curve) / np.sum(aggregated_curve)
    )
    return score, aggregated_curve


def classify_score(score):
    """Map the crisp defuzzified score to a human-readable performance level."""
    if score < 40:
        return "High Risk - Needs Serious Improvement"
    if score < 65:
        return "Moderate Risk - Needs Improvement"
    return "Low Risk - Good Performance"


# ---------------------------------------------------------------------------
# Orchestrator - runs the full pipeline, used by the Streamlit app
# ---------------------------------------------------------------------------
def run_fuzzy_inference(study_hours, attendance_percentage, test_score_percentage):
    """Run steps 2-6 end to end and return everything the UI needs to display."""
    study_hours = float(np.clip(study_hours, 0, 12))
    attendance_percentage = float(np.clip(attendance_percentage, 0, 100))
    test_score_percentage = float(np.clip(test_score_percentage, 0, 100))

    study_deg = fuzzify(study_hours, STUDY_MFS)
    attend_deg = fuzzify(attendance_percentage, ATTENDANCE_MFS)
    score_deg = fuzzify(test_score_percentage, SCORE_MFS)

    rule_results, aggregated_strengths = evaluate_rules(study_deg, attend_deg, score_deg)
    score, aggregated_curve = defuzzify(aggregated_strengths)
    level = classify_score(score)

    return {
        "inputs": {
            "study_hours": study_hours,
            "attendance_percentage": attendance_percentage,
            "test_score_percentage": test_score_percentage,
        },
        "membership_degrees": {
            "study_hours": study_deg,
            "attendance_percentage": attend_deg,
            "test_score_percentage": score_deg,
        },
        "rule_results": rule_results,
        "aggregated_strengths": aggregated_strengths,
        "aggregated_curve": aggregated_curve,
        "score": score,
        "level": level,
    }


if __name__ == "__main__":
    # Quick manual test: python fuzzy_system.py
    demo = run_fuzzy_inference(study_hours=2, attendance_percentage=68, test_score_percentage=55)
    print("Inputs:", demo["inputs"])
    print("Membership degrees:", demo["membership_degrees"])
    print("Aggregated rule strengths:", demo["aggregated_strengths"])
    print(f"Score: {demo['score']:.2f} -> {demo['level']}")
