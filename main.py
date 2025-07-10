from pathlib import Path
import pandas as pd
from dash import Dash
from src.loader import load_file


# загрузка json
data = load_file(Path("data/test.json"))
df = pd.DataFrame(data)




# запуск
if __name__ == "__main__":
    print(df.head())
