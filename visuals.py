import matplotlib.pyplot as plt
import numpy as np

def plot_performance_gap(subjects: dict):
    """
    Generates a horizontal bar chart comparing Current Score vs Target Score.
    """
    subject_names = list(subjects.keys())
    current_scores = [data.current_score for data in subjects.values()]
    target_scores = [data.target_score for data in subjects.values()]

    y_pos = np.arange(len(subject_names))
    height = 0.35

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')

    # Horizontal bars
    rects1 = ax.barh(y_pos - height/2, current_scores, height, label='Current Score', color='#FF4B4B')
    rects2 = ax.barh(y_pos + height/2, target_scores, height, label='Target Score', color='#00FFAA')

    # Formatting axes and labels
    ax.set_xlabel('Score (%)', color='white')
    ax.set_title('Current vs Target Performance Gap', color='white', fontsize=14, weight='bold')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(subject_names, color='white')
    ax.set_xlim(0, 100)
    ax.tick_params(axis='x', colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.legend(facecolor='#262730', edgecolor='none', labelcolor='white')

    # Value tags on bars
    for rect in rects1:
        w = rect.get_width()
        ax.text(w + 1, rect.get_y() + rect.get_height()/2, f'{int(w)}%', ha='left', va='center', color='white', fontsize=9)
    for rect in rects2:
        w = rect.get_width()
        ax.text(w + 1, rect.get_y() + rect.get_height()/2, f'{int(w)}%', ha='left', va='center', color='white', fontsize=9)

    plt.tight_layout()
    return fig


def plot_hours_allocation(weekly_schedule: list):
    """
    Generates a donut chart displaying allocated study hours per subject.
    """
    hours_per_subject = {}
    for item in weekly_schedule:
        hours_per_subject[item.subject] = hours_per_subject.get(item.subject, 0.0) + item.duration_hours

    labels = list(hours_per_subject.keys())
    sizes = list(hours_per_subject.values())

    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor('#0E1117')

    colors = ['#FF4B4B', '#1E88E5', '#FFD166', '#06D6A0', '#118AB2']
    wedges, texts, autotexts = ax.pie(
        sizes, 
        labels=labels, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=colors[:len(labels)],
        textprops=dict(color="white"),
        wedgeprops=dict(width=0.4, edgecolor='#0E1117')
    )

    for at in autotexts:
        at.set_color('black')
        at.set_weight('bold')

    ax.set_title('Study Hours Distribution', color='white', fontsize=14, weight='bold')
    plt.tight_layout()
    return fig
