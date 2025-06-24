from pathlib import Path

import matplotlib.pyplot as plt
import pandas

from src.analyzer import get_chart_data


def plot_chart_data(chart_data: pandas.DataFrame,
                    kind: str,
                    title: str,
                    xlabel: str,
                    ylabel: str,
                    colors: dict,
                    show_legend: bool):
    merged = pandas.DataFrame()
    for column in chart_data.columns:
        series = pandas.Series(chart_data[column][0])
        merged[column] = series
    merged = merged.transpose()
    merged = merged.reindex(colors.keys(), axis=1)
    merged = merged.dropna(axis=1, how="all")
    ax = merged.plot(
        kind=kind,
        stacked=True,
        figsize=(10, 6),
        color=[colors[col] for col in merged.columns],
        rot=0,
        xlabel=xlabel,
        ylabel=ylabel,
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
    plt.ylim(0, 1)
    plt.title(title)
    if show_legend:
        plt.legend(title=xlabel)
    else:
        plt.legend().set_visible(False)
    plt.tight_layout()


def plot_chart(file: Path = None):
    general_bar_chart_data, bet_line_chart_data = get_chart_data(file=file)
    plot_chart_data(
        chart_data=general_bar_chart_data,
        kind="bar",
        title="Action Distribution by KPI",
        xlabel="KPI",
        ylabel="Action Distribution",
        colors={
            "call": "#cc4125",
            "fold": "#666666",
            "raise": "#6aa84f",
            "bet": "#3d85c6",
            "check": "#f1c232",
        },
        show_legend=True,
    )
    if bet_line_chart_data is not None:
        plot_chart_data(
            chart_data=bet_line_chart_data,
            kind="line",
            title="Bet Rate by KPI",
            xlabel="KPI",
            ylabel="Bet Rate",
            colors={
                "bet": "#3d85c6",
            },
            show_legend=False,
        )
    plt.show()
