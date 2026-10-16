# Build an interactive dashboard to explore fuel efficiency in the Auto dataset.
import streamlit as st
import pandas as pd
import plotly.express as px
from ISLP import load_data

st.set_page_config(page_title="Auto Data Dashboard", layout="wide")

@st.cache_data
def get_auto_data():
    # Load the Auto dataset and add readable origin labels.
    data = load_data("Auto").copy()
    origin_names = {1: "American", 2: "European", 3: "Japanese"}
    data["origin_name"] = data["origin"].map(origin_names)
    return data.dropna(subset=["mpg", "horsepower", "weight", "year", "origin_name"])

auto = get_auto_data()

st.title("Fuel Efficiency of Cars, 1970–1982")
st.write(
    "Explore how fuel efficiency relates to horsepower, vehicle weight, "
    "and model year in the ISLP Auto dataset."
)

# This filter updates all four charts below.
origin_options = ["All origins"] + sorted(auto["origin_name"].unique().tolist())
selected_origin = st.sidebar.selectbox("Filter by vehicle origin", origin_options)

if selected_origin == "All origins":
    filtered = auto
else:
    filtered = auto[auto["origin_name"] == selected_origin]

st.caption(f"Showing {len(filtered)} cars.")

# Chart 1: distribution of fuel efficiency.
histogram = px.histogram(
    filtered,
    x="mpg",
    nbins=20,
    color="origin_name",
    title="Fuel Efficiency Distribution",
    labels={"mpg": "Miles per gallon (mpg)", "count": "Number of cars"},
)
st.plotly_chart(histogram, use_container_width=True)

# Chart 2: relationship between horsepower and fuel efficiency.
scatter = px.scatter(
    filtered,
    x="horsepower",
    y="mpg",
    color="origin_name",
    hover_data=["weight", "year"],
    title="Horsepower and Fuel Efficiency",
    labels={
        "horsepower": "Horsepower",
        "mpg": "Miles per gallon (mpg)",
        "origin_name": "Vehicle origin",
    },
)
st.plotly_chart(scatter, use_container_width=True)

# Chart 3: compare fuel efficiency across origins.
boxplot = px.box(
    filtered,
    x="origin_name",
    y="mpg",
    color="origin_name",
    title="Fuel Efficiency by Vehicle Origin",
    labels={
        "origin_name": "Vehicle origin",
        "mpg": "Miles per gallon (mpg)",
    },
)
st.plotly_chart(boxplot, use_container_width=True)

# Chart 4: show the average fuel efficiency trend by model year.
yearly = (
    filtered.assign(model_year=filtered["year"] + 1900)
    .groupby("model_year", as_index=False)["mpg"]
    .mean()
    .rename(columns={"mpg": "average_mpg"})
)

line_chart = px.line(
    yearly,
    x="model_year",
    y="average_mpg",
    markers=True,
    title="Average Fuel Efficiency by Model Year",
    labels={
        "model_year": "Model year",
        "average_mpg": "Average miles per gallon (mpg)",
    },
)
st.plotly_chart(line_chart, use_container_width=True)
