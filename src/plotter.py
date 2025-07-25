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
    plot_kwargs = {
        "kind": kind,
        "xlabel": xlabel,
        "ylabel": ylabel,
        "color": [colors[col] for col in merged.columns],
        "figsize": (10, 6),
        "rot": 0,
    }
    if kind == "bar":
        plot_kwargs["stacked"] = True
    if kind == "line":
        plot_kwargs["marker"] = "o"
        plot_kwargs["markersize"] = 4
        plot_kwargs["linestyle"] = "-"
        plot_kwargs["linewidth"] = 1.5
        plot_kwargs["markerfacecolor"] = "white"
    ax = merged.plot(**plot_kwargs)
    if kind == "bar":
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
    elif kind == "line":
        plt.grid(True)
        for line in ax.lines:
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            for x, y in zip(x_data, y_data):
                if not pandas.isna(y):
                    ax.annotate(
                        f"{y * 100:.0f}%",
                        xy=(x, y),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha="center",
                        fontsize=8,
                    )
    plt.xticks(rotation=0)
    plt.gca().yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"{int(x * 100)}%")
    )
    plt.ylim(0, 1.05)
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
            "check": "#f1c232",
            "bet": "#9fc5e8",
            "bet1": "#9fc5e8",
            "bet2": "#9dc4e7",
            "bet3": "#9bc3e6",
            "bet4": "#99c2e5",
            "bet5": "#97c1e4",
            "bet6": "#95c0e3",
            "bet7": "#93bfe2",
            "bet8": "#91bee1",
            "bet9": "#8fbee0",
            "bet10": "#8dbddf",
            "bet11": "#8bbcdf",
            "bet12": "#89bbde",
            "bet13": "#87badd",
            "bet14": "#85b9dc",
            "bet15": "#83b8db",
            "bet16": "#81b7da",
            "bet17": "#7fb6d9",
            "bet18": "#7db5d8",
            "bet19": "#7bb4d7",
            "bet20": "#79b3d6",
            "bet21": "#77b3d5",
            "bet22": "#75b2d4",
            "bet23": "#73b1d3",
            "bet24": "#71b0d2",
            "bet25": "#6fafd2",
            "bet26": "#6daed1",
            "bet27": "#6badd0",
            "bet28": "#69accf",
            "bet29": "#67abce",
            "bet30": "#65aacd",
            "bet31": "#63a9cc",
            "bet32": "#61a8cb",
            "bet33": "#5fa8ca",
            "bet34": "#5da7c9",
            "bet35": "#5ba6c8",
            "bet36": "#59a5c7",
            "bet37": "#57a4c6",
            "bet38": "#55a3c5",
            "bet39": "#53a2c5",
            "bet40": "#51a1c4",
            "bet41": "#4fa0c3",
            "bet42": "#4d9fc2",
            "bet43": "#4b9ec1",
            "bet44": "#499dc0",
            "bet45": "#479cbf",
            "bet46": "#459bbe",
            "bet47": "#439abd",
            "bet48": "#4199bc",
            "bet49": "#3f98bb",
            "bet50": "#3d97ba",
            "bet51": "#3b96b9",
            "bet52": "#3995b9",
            "bet53": "#3794b8",
            "bet54": "#3593b7",
            "bet55": "#3392b6",
            "bet56": "#3191b5",
            "bet57": "#2f90b4",
            "bet58": "#2d8fb3",
            "bet59": "#2b8eb2",
            "bet60": "#298db1",
            "bet61": "#278cb0",
            "bet62": "#258baf",
            "bet63": "#238aae",
            "bet64": "#2189ae",
            "bet65": "#1f88ad",
            "bet66": "#1d87ac",
            "bet67": "#1b86ab",
            "bet68": "#1985aa",
            "bet69": "#1784a9",
            "bet70": "#1583a8",
            "bet71": "#1382a7",
            "bet72": "#1181a6",
            "bet73": "#0f80a5",
            "bet74": "#0d7fa4",
            "bet75": "#0b7ea3",
            "bet76": "#097da3",
            "bet77": "#077ca2",
            "bet78": "#057ba1",
            "bet79": "#037aa0",
            "bet80": "#01799f",
            "bet81": "#00789e",
            "bet82": "#00779d",
            "bet83": "#00769c",
            "bet84": "#00759b",
            "bet85": "#00749a",
            "bet86": "#007399",
            "bet87": "#007298",
            "bet88": "#007197",
            "bet89": "#007096",
            "bet90": "#006f95",
            "bet91": "#006e94",
            "bet92": "#006d93",
            "bet93": "#006c92",
            "bet94": "#006b91",
            "bet95": "#006a90",
            "bet96": "#00698f",
            "bet97": "#00688e",
            "bet98": "#00678d",
            "bet99": "#00668c",
            "bet100": "#3d85c6",
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
                "bet": "#9fc5e8",
                "bet1": "#9fc5e8",
                "bet2": "#9dc4e7",
                "bet3": "#9bc3e6",
                "bet4": "#99c2e5",
                "bet5": "#97c1e4",
                "bet6": "#95c0e3",
                "bet7": "#93bfe2",
                "bet8": "#91bee1",
                "bet9": "#8fbee0",
                "bet10": "#8dbddf",
                "bet11": "#8bbcdf",
                "bet12": "#89bbde",
                "bet13": "#87badd",
                "bet14": "#85b9dc",
                "bet15": "#83b8db",
                "bet16": "#81b7da",
                "bet17": "#7fb6d9",
                "bet18": "#7db5d8",
                "bet19": "#7bb4d7",
                "bet20": "#79b3d6",
                "bet21": "#77b3d5",
                "bet22": "#75b2d4",
                "bet23": "#73b1d3",
                "bet24": "#71b0d2",
                "bet25": "#6fafd2",
                "bet26": "#6daed1",
                "bet27": "#6badd0",
                "bet28": "#69accf",
                "bet29": "#67abce",
                "bet30": "#65aacd",
                "bet31": "#63a9cc",
                "bet32": "#61a8cb",
                "bet33": "#5fa8ca",
                "bet34": "#5da7c9",
                "bet35": "#5ba6c8",
                "bet36": "#59a5c7",
                "bet37": "#57a4c6",
                "bet38": "#55a3c5",
                "bet39": "#53a2c5",
                "bet40": "#51a1c4",
                "bet41": "#4fa0c3",
                "bet42": "#4d9fc2",
                "bet43": "#4b9ec1",
                "bet44": "#499dc0",
                "bet45": "#479cbf",
                "bet46": "#459bbe",
                "bet47": "#439abd",
                "bet48": "#4199bc",
                "bet49": "#3f98bb",
                "bet50": "#3d97ba",
                "bet51": "#3b96b9",
                "bet52": "#3995b9",
                "bet53": "#3794b8",
                "bet54": "#3593b7",
                "bet55": "#3392b6",
                "bet56": "#3191b5",
                "bet57": "#2f90b4",
                "bet58": "#2d8fb3",
                "bet59": "#2b8eb2",
                "bet60": "#298db1",
                "bet61": "#278cb0",
                "bet62": "#258baf",
                "bet63": "#238aae",
                "bet64": "#2189ae",
                "bet65": "#1f88ad",
                "bet66": "#1d87ac",
                "bet67": "#1b86ab",
                "bet68": "#1985aa",
                "bet69": "#1784a9",
                "bet70": "#1583a8",
                "bet71": "#1382a7",
                "bet72": "#1181a6",
                "bet73": "#0f80a5",
                "bet74": "#0d7fa4",
                "bet75": "#0b7ea3",
                "bet76": "#097da3",
                "bet77": "#077ca2",
                "bet78": "#057ba1",
                "bet79": "#037aa0",
                "bet80": "#01799f",
                "bet81": "#00789e",
                "bet82": "#00779d",
                "bet83": "#00769c",
                "bet84": "#00759b",
                "bet85": "#00749a",
                "bet86": "#007399",
                "bet87": "#007298",
                "bet88": "#007197",
                "bet89": "#007096",
                "bet90": "#006f95",
                "bet91": "#006e94",
                "bet92": "#006d93",
                "bet93": "#006c92",
                "bet94": "#006b91",
                "bet95": "#006a90",
                "bet96": "#00698f",
                "bet97": "#00688e",
                "bet98": "#00678d",
                "bet99": "#00668c",
                "bet100": "#3d85c6",
            },
            show_legend=True,
        )
    plt.show()
