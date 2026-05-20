import pandas as pd
import plotly.express as px


def _monthly_series(df: pd.DataFrame) -> pd.Series:
    data = df.copy()
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["Amount"])
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])

    if data.empty:
        return pd.Series(dtype=float)

    data["Month"] = data["Date"].dt.to_period("M")
    s = data.groupby("Month")["Amount"].sum().sort_index()
    s.index = s.index.astype(str)
    return s


def forecast_monthly_sales(df: pd.DataFrame, *, periods: int = 3):
    """Lightweight baseline forecasting.

    Uses a seasonal-naive / moving-average hybrid:
    - If enough history: use rolling mean of last 3 months.
    - Otherwise: use mean of available months.

    Returns: (history_series, forecast_series, figure)
    """
    hist = _monthly_series(df)

    if hist.empty or len(hist) < 2:
        return hist, pd.Series(dtype=float), None

    last_n = min(3, len(hist))
    window_mean = hist.tail(last_n).mean()

    # Simple trend extrapolation: use last delta if possible
    if len(hist) >= 3:
        recent_delta = hist.iloc[-1] - hist.iloc[-2]
        step = recent_delta / 1.0
    else:
        step = 0.0

    last_month = pd.Period(hist.index[-1])
    future_index = [str((last_month + i).to_timestamp().date()) for i in range(1, periods + 1)]

    forecast_vals = []
    base = window_mean
    for i in range(1, periods + 1):
        forecast_vals.append(base + step * i)

    forecast = pd.Series(forecast_vals, index=future_index, name="Forecast")

    full = pd.DataFrame({"Month": hist.index.tolist() + forecast.index.tolist(),
                         "Sales": hist.values.tolist() + forecast.values.tolist(),
                         "Type": ["History"] * len(hist) + ["Forecast"] * len(forecast)})

    fig = px.line(
        full,
        x="Month",
        y="Sales",
        color="Type",
        markers=True,
        title=f"Monthly Sales Forecast (baseline, next {periods} months)",
    )
    fig.update_traces(mode="lines+markers")

    return hist, forecast, fig

