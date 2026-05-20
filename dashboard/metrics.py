import pandas as pd


def _require_cols(df: pd.DataFrame, cols: set[str]) -> tuple[bool, list[str]]:
    missing = sorted(cols - set(df.columns))
    return (len(missing) == 0), missing


def compute_real_world_kpis(df: pd.DataFrame) -> dict:
    """Compute business metrics with guardrails.

    If columns are missing, returns a value of None with a human explanation.
    """
    data = df.copy()
    if data.empty:
        return {
            "kpis": [],
            "notes": ["No data available after filtering."],
        }

    # Total sales always computable (Amount)
    data["Amount"] = pd.to_numeric(data.get("Amount"), errors="coerce")
    data = data.dropna(subset=["Amount"])

    total_sales = float(data["Amount"].sum()) if len(data) else 0.0

    kpis = []
    notes = []

    # Profit margin
    can_profit = _require_cols(data, {"Profit"})[0]
    if can_profit:
        profit = pd.to_numeric(data["Profit"], errors="coerce").dropna()
        profit_sum = float(profit.sum()) if len(profit) else 0.0
        margin = (profit_sum / total_sales) if total_sales else 0.0
        kpis.append({
            "name": "Profit margin",
            "value": f"{margin*100:.1f}%",
            "explanation": "Computed as total Profit / total Sales."
        })
    else:
        notes.append("Profit margin not computed: 'Profit' column not found.")
        kpis.append({
            "name": "Profit margin",
            "value": "N/A",
            "explanation": "Dataset does not include a Profit column."
        })

    # Retention / repeat customers
    # Try customer identifiers.
    customer_cols = ["Customer", "Customer Name", "Client", "Order ID"]
    cust_col = next((c for c in customer_cols if c in data.columns), None)

    if cust_col is not None and "Date" in data.columns:
        tmp = data.copy()
        tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
        tmp = tmp.dropna(subset=["Date"])
        if len(tmp) >= 2:
            # Repeat customer proxy: customers appearing in >1 month.
            tmp["Month"] = tmp["Date"].dt.to_period("M")
            cust_months = tmp.groupby(cust_col)["Month"].nunique()
            repeat_rate = float((cust_months > 1).mean())
            kpis.append({
                "name": "Retention rate (proxy)",
                "value": f"{repeat_rate*100:.1f}%",
                "explanation": f"Computed using '{cust_col}': % of entities appearing in 2+ months (proxy retention)."
            })
        else:
            kpis.append({
                "name": "Retention rate (proxy)",
                "value": "N/A",
                "explanation": "Not enough dated records to compute retention proxy."
            })
    else:
        notes.append("Retention not computed: customer identifier and/or Date column not found.")
        kpis.append({
            "name": "Retention rate (proxy)",
            "value": "N/A",
            "explanation": "Dataset missing customer identifier and/or Date."
        })

    # Top loss-making products (or lowest margin)
    if can_profit:
        if "Product" in data.columns:
            # compute profit by product
            prod_profit = data.groupby("Product")["Profit"].sum().sort_values()
            worst = prod_profit.head(5)
            kpis.append({
                "name": "Top loss-making products",
                "value": ", ".join([f"{p}" for p in worst.index]),
                "explanation": "Products with lowest total Profit."
            })
        else:
            kpis.append({
                "name": "Top loss-making products",
                "value": "N/A",
                "explanation": "Dataset missing Product column."
            })
    else:
        # Use lowest sales as proxy if profit isn't available
        if "Product" in data.columns:
            prod_sales = data.groupby("Product")["Amount"].sum().sort_values()
            worst = prod_sales.head(5)
            kpis.append({
                "name": "Top loss-making products (proxy)",
                "value": ", ".join([f"{p}" for p in worst.index]),
                "explanation": "Dataset has no Profit, so proxy uses lowest total Sales."
            })
        else:
            kpis.append({
                "name": "Top loss-making products",
                "value": "N/A",
                "explanation": "Dataset missing Product column."
            })

    # Repeat customer analysis (if customer proxy exists)
    if cust_col is not None and "Date" in data.columns and len(data) > 0:
        tmp = data.copy()
        tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")
        tmp = tmp.dropna(subset=["Date"])
        tmp["Month"] = tmp["Date"].dt.to_period("M")
        cust_months = tmp.groupby(cust_col)["Month"].nunique()
        dist = cust_months.value_counts().sort_index()
        kpis.append({
            "name": "Repeat customer distribution (proxy)",
            "value": ", ".join([f"{int(idx)} mo: {int(cnt)}" for idx, cnt in dist.head(4).items()]),
            "explanation": f"How many months each '{cust_col}' appears in (proxy repeat analysis)."
        })

    return {"kpis": kpis, "notes": notes, "total_sales": total_sales}

