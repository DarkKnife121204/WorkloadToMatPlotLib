from pathlib import Path
import pandas as pd
from src.loader import load_file
from src.plotter import plot


# загрузка json
data = load_file(Path("data/test.json"))
df = pd.DataFrame(data)




# запуск
if __name__ == "__main__":
    plot(df)
