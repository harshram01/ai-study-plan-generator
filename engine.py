# engine.py

def generate_study_plan(subjects, hours_per_day=2):
    """
    Generate a simple study plan.

    subjects: list of subject names
    hours_per_day: available study hours per day
    """

    if not subjects:
        return "No subjects provided."

    try:
        hours_per_day = float(hours_per_day)
    except (ValueError, TypeError):
        hours_per_day = 2

    hours_per_subject = hours_per_day / len(subjects)

    plan = []

    for subject in subjects:
        plan.append({
            "subject": subject,
            "hours": round(hours_per_subject, 2)
        })

    return plan