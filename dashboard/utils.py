import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    df['Amount'] = (
        df['Amount']
        .replace('[\$,]', '', regex=True)
        .astype(float)
    )
    df['Date'] = pd.to_datetime(df['Date'].astype(str).str.strip(), dayfirst=True, errors='coerce')
    return df