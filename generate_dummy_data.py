import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_data(filename="data/history.csv", num_rows=1000):
    print(f"Generando {num_rows} filas de datos sintéticos...")
    
    # Generar timestamps
    base = datetime.now()
    date_list = [base - timedelta(minutes=x) for x in range(num_rows)]
    date_list.reverse()

    # Generar precios aleatorios (Random Walk)
    price = 1.1000
    data = []
    
    for date in date_list:
        change = np.random.normal(0, 0.0005)
        open_p = price
        close_p = price + change
        high_p = max(open_p, close_p) + abs(np.random.normal(0, 0.0002))
        low_p = min(open_p, close_p) - abs(np.random.normal(0, 0.0002))
        volume = np.random.randint(100, 1000)
        
        data.append([date, open_p, high_p, low_p, close_p, volume])
        price = close_p

    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df.set_index('timestamp', inplace=True)
    
    df.to_csv(filename)
    print(f"Datos guardados en {filename}")

if __name__ == "__main__":
    generate_data()
