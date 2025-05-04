from datetime import time
import pandas as pd
import plotly.express as px
from plotly.graph_objs import Figure

from config import PERIOD
from utils import add_period_to_rounded_time


def plot_upcoming_charges(df: pd.DataFrame, current_time: time) -> Figure:
    """Plot the upcoming charges for the car"""
    fig = px.line(df, x="Time", y="Battery %")

    # Add a vertical line at the current time
    fig.add_vline(
        x=current_time,
        line_dash="dash",
        line_color="white",
        label=dict(text="Now", textposition="top center"),
    )

    # Add vertical rectangles for charging periods
    for i, row in df.iterrows():
        if not row["Car is Charging"]:
            continue
        fig.add_vrect(
            x0=row["Time"],
            x1 = add_period_to_rounded_time(row["Time"], PERIOD),
            fillcolor="red" if row["Charge is Override"] else "green",
            opacity=0.1,
            layer="below",
            label=dict(
                text="Override" if row["Charge is Override"] else "Scheduled",
                font=dict(
                    color="red" if row["Charge is Override"] else "green",
                ),
                textposition="top center",
            ),
        )

    fig.update_traces(mode="markers+lines")
    return fig
