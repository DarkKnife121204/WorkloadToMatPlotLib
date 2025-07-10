import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import itertools
import matplotlib
import os
matplotlib.use("Agg")


# выбор уровня при перегрузке
def get_levels(events):
    levels = []
    for event in sorted(events, key=lambda x: x['start']):
        placed = False
        for level_idx, level in enumerate(levels):
            if all(event['end'] < e['start'] or event['start'] > e['end'] for e in level):
                level.append(event)
                event['level'] = level_idx
                placed = True
                break
        if not placed:
            levels.append([event])
            event['level'] = len(levels) - 1
    return events, len(levels)


def plot(df):
    plt.style.use("dark_background")

    # время
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["duration"] = (df["end"] - df["start"]).dt.days + 1

    # сотрудники
    employees = df["employee"].unique()
    employee_base_pos = {name: idx * 3 for idx, name in enumerate(employees)}

    fig, ax = plt.subplots(figsize=(16, 9))

    # цвета
    color_palette = [
        "#5DA5DA", "#FAA43A", "#60BD68", "#F17CB0", "#B2912F", "#B276B2"
    ]

    color_cycle = itertools.cycle(color_palette)

    project_colors = {}
    for task in df["task"].unique():
        if task == "Отпуск":
            project_colors[task] = "#A0A0A0"
        elif task == "Переработка":
            continue
        else:
            project_colors[task] = next(color_cycle)

    yticks = []
    yticklabels = []
    legend_items = {}

    # отрисовка
    for employee in employees:
        emp_assignments = df[(df["employee"] == employee) & (df["type"] == "assignment")].copy()
        events = [{'index': idx, 'start': row['start'], 'end': row['end']} for idx, row in emp_assignments.iterrows()]
        events, index = get_levels(events)

        # поиск пересечений
        overlap_indices = {
            e1['index']
            for i, e1 in enumerate(events)
            for j, e2 in enumerate(events)
            if i != j and not (e1['end'] < e2['start'] or e1['start'] > e2['end'])
        }

        base_y = employee_base_pos[employee]
        max_level = 0

        emp_events = df[df["employee"] == employee].reset_index()
        for index, row in emp_events.iterrows():
            if row["type"] == "overtime":
                # переработка
                ax.scatter(
                    mdates.date2num(row["start"]), base_y,
                    marker="D", s=60, color="#F15854", zorder=2
                )
                continue

            # уровень для баров при перегрузке
            assignment_level = 0
            if row["type"] == "assignment":
                for e in events:
                    if e["index"] == row["index"]:
                        assignment_level = e["level"]
                        break

            y = base_y + assignment_level
            max_level = max(max_level, assignment_level)

            start = mdates.date2num(row["start"])
            duration = row["duration"]
            end = mdates.date2num(row["end"])

            color = project_colors.get(row["task"], "#AAAAAA")

            # рамка для перегрузки
            edge_col = "red" if row["type"] == "assignment" and row["index"] in overlap_indices else None

            # бары в легенде
            if row["task"] not in legend_items and row["type"] != "overtime":
                legend_items[row["task"]] = plt.Rectangle((0, 0), 1, 1, color=color)

            # сами бары
            ax.barh(
                y, duration, left=start, height=0.95,
                color=color, alpha=0.7, edgecolor=edge_col, linewidth=1, zorder=2
            )

            # подпись блоков
            ax.text(end, y, row["task"], ha="right", va="center",
                    fontsize=11, color="white", alpha=0.9)

        yticks.append(base_y + max_level / 2)
        yticklabels.append(employee)

    # оси и сетка
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels)
    ax.xaxis_date()
    plt.xticks(rotation=45)

    ax.set_xlabel("Дата")
    ax.set_ylabel("Сотрудник")
    ax.set_title("Загруженность сотрудников", fontsize=14)

    plt.grid(True, axis='x', linestyle='--', linewidth=0.5, alpha=0.3, zorder=1)

    # легенда
    handles = list(legend_items.values())
    labels = list(legend_items.keys())
    handles.append(
        plt.Line2D([0], [0], marker='D', linestyle='None', markerfacecolor="#F15854", markersize=8, label='Переработка')
    )
    ax.legend(
        handles=handles, labels=labels + ['Переработка'],
        title="Тип занятости",
        loc='upper left', bbox_to_anchor=(1.02, 1),
        borderaxespad=0, fontsize=10, title_fontsize=11
    )

    plt.tight_layout()
    os.makedirs("static", exist_ok=True)
    plt.savefig("static/plot.png", bbox_inches='tight')
    plt.close()
