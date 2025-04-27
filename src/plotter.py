from pathlib import Path

import matplotlib.pyplot as plt
import pandas

from src.analyzer import get_chart_data


def plot_chart(file: Path = None):
    chart_data = get_chart_data(file=file)
    merged = pandas.DataFrame()
    for column in chart_data.columns:
        series = pandas.Series(chart_data[column][0])
        merged[column] = series
    merged = merged.transpose()
    colors = {
        "call": "#cc4125",
        "fold": "#666666",
        "raise": "#6aa84f",
        "bet": "#3d85c6",
        "check": "#f1c232",
    }
    merged = merged.reindex(colors.keys(), axis=1)
    merged = merged.dropna(axis=1, how="all")
    ax = merged.plot(
        kind="bar",
        stacked=True,
        figsize=(10, 6),
        color=[colors[col] for col in merged.columns],
        rot=0,
        xlabel="KPI",
        ylabel="Distribution",
    )
    for container in ax.containers:
        labels = []
        for rectangle in container:
            rectangle.set_edgecolor("black")
            rectangle.set_linewidth(1)
            label = (
                f"{rectangle.get_height() * 100:.1f}%"
                if f"{rectangle.get_height() * 100:.1f}%" != "0.0%"
                else ""
            )
            labels.append(label)
        ax.bar_label(container, labels=labels, label_type="center", fontsize=8)
    plt.xticks(rotation=0)
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{int(x * 100)}%")
    )
    plt.title("KPI Comparison")
    plt.legend(title="KPI")
    plt.tight_layout()
    plt.show()
