from flask import Flask, render_template, request
import pandas as pd
from src.plotter import plot
from src.loader import load_file

app = Flask(__name__)

@app.route("/")
def index():
    # загрузка json
    data = load_file("data/test.json")
    df = pd.DataFrame(data)

    # список сотрудников и проектов для фильтрации
    employees = df['employee'].unique().tolist()
    projects = df[df['type'] == 'assignment']['task'].unique().tolist()

    selected_employees = request.args.getlist('employees') or employees
    selected_projects = request.args.getlist('projects') or projects

    # фильтрация
    filtered_df = df[
        (df['employee'].isin(selected_employees)) &
        ((df['task'].isin(selected_projects)) | (df['type'] != 'assignment'))
        ]

    # диаграмма
    plot(filtered_df)

    # рендер страницы
    return render_template(
        "index.html",
        employees=employees,
        projects=projects,
        selected_employees=selected_employees,
        selected_projects=selected_projects
    )

if __name__ == "__main__":
    app.run(debug=True)
