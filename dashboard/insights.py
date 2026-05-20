import pandas as pd


def _safe_first_or_none(series):
    return series.iloc[0] if len(series) else None


def generate_key_insights(df: pd.DataFrame, *, top_n: int = 3) -> list[dict]:
    """Generate recruiter-friendly, deterministic insights from the dataset.

    Returns a list of dicts like:
    {
      "title": str,
      "bullets": [str, ...]
    }
    """
    insights: list[dict] = []

    required_cols = {"Amount", "Date", "Product", "Country"}
    missing = required_cols - set(df.columns)
    if missing:
        insights.append(
            {
                "title": "Key Insights",
                "bullets": [
                    f"Not enough columns to compute insights. Missing: {', '.join(sorted(missing))}.",
                    "Charts still render, but narrative insights are limited.",
                ],
            }
        )
        return insights

    # Ensure types
    data = df.copy()
    data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")
    data = data.dropna(subset=["Amount"])
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"])

    if data.empty:
        insights.append(
            {
                "title": "Key Insights",
                "bullets": ["No data available after filtering."]
                ,
            }
        )
        return insights

    # --- 1) Why sales dropped (simple, explainable decomposition)
    # Use last two periods (monthly) within current slice.
    data["Month"] = data["Date"].dt.to_period("M")
    monthly = data.groupby("Month")["Amount"].sum().sort_index()

    if len(monthly) >= 2:
        prev_month, curr_month = monthly.index[-2], monthly.index[-1]
        delta = monthly.iloc[-1] - monthly.iloc[-2]
        direction = "increased" if delta >= 0 else "dropped"
        drop_amt = abs(delta)

        # Contribution to change by Product
        prod_month = (
            data[data["Month"].isin([prev_month, curr_month])]
            .groupby(["Product", "Month"])["Amount"]
            .sum()
            .unstack("Month")
            .fillna(0)
        )
        if curr_month in prod_month.columns and prev_month in prod_month.columns:
            prod_month["change"] = prod_month[curr_month] - prod_month[prev_month]
            worst = prod_month.sort_values("change").head(top_n)
            best = prod_month.sort_values("change").tail(top_n)

            bullets = [
                f"Total sales {direction} by ${drop_amt:,.2f} from {str(prev_month)} → {str(curr_month)}.",
            ]
            if delta < 0:
                bullets.append(
                    "Largest negative drivers (by Product): "
                    + ", ".join(
                        [
                            f"{idx} (${row['change']:.2f})"
                            for idx, row in worst.iterrows()
                        ]
                    )
                    + "."
                )
            else:
                bullets.append(
                    "Strongest positive drivers (by Product): "
                    + ", ".join(
                        [
                            f"{idx} (${row['change']:.2f})"
                            for idx, row in best.iterrows()
                        ]
                    )
                    + "."
                )

            insights.append({"title": "Why sales changed (recent month)", "bullets": bullets})

    # --- 2) Which category underperformed
    # Use Product as category proxy.
    product_sales = data.groupby("Product")["Amount"].sum().sort_values(ascending=False)
    if len(product_sales) >= top_n:
        underperform = product_sales.tail(top_n)
        bullets = [
            "Lowest-performing products in the selected data slice: "
            + ", ".join([f"{p} (${a:,.2f})" for p, a in underperform.items()])
            + "."
        ]
        insights.append({"title": "Underperforming products", "bullets": bullets})

    # --- 3) Which region drives revenue (Country proxy)
    country_sales = data.groupby("Country")["Amount"].sum().sort_values(ascending=False)
    if len(country_sales) > 0:
        top_countries = country_sales.head(top_n)
        bullets = [
            "Top countries by revenue: "
            + ", ".join([f"{c} (${a:,.2f})" for c, a in top_countries.items()])
            + "."
        ]
        insights.append({"title": "Regions driving revenue (proxy: Country)", "bullets": bullets})

    # --- 4) Which month causes spikes/dips
    # identify max and min month by sales.
    if len(monthly) >= 3:
        max_month = monthly.idxmax()
        min_month = monthly.idxmin()
        bullets = [
            f"Highest month: {str(max_month)} (${monthly.loc[max_month]:,.2f}).",
            f"Lowest month: {str(min_month)} (${monthly.loc[min_month]:,.2f}).",
        ]
        # MoM spikes: largest absolute MoM change
        mom = monthly.diff().dropna()
        if len(mom) > 0:
            spike_month = mom.abs().idxmax()
            bullets.append(
                f"Largest month-over-month swing: {str(spike_month)} (change ${mom.loc[spike_month]:,.2f})."
            )
        insights.append({"title": "Seasonality: spikes & dips", "bullets": bullets})

    # Fallback if nothing computed
    if not insights:
        insights.append({"title": "Key Insights", "bullets": ["Not enough data to generate insights."]})

    return insights

