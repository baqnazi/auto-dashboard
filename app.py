# Create an interactive dashboard for exploring fuel efficiency in the Auto dataset.
import streamlit as st
import pandas as pd
import plotly.express as px
from ISLP import load_data

st.set_page_config(page_title="Auto Data Dashboard", layout="wide")

@st.cache_data
def get_auto_data():
    # Load the dataset and add readable origin and model-year labels.
    data = load_data("Auto").copy()
    origin_names = {1: "American", 2: "European", 3: "Japanese"}
    data["origin_name"] = data["origin"].map(origin_names)
    data["model_year"] = data["year"] + 1900
    return data.dropna(
        subset=["mpg", "horsepower", "weight", "year", "cylinders", "origin_name"]
    )

auto = get_auto_data()

st.title("Which Cars Are the Most Fuel-Efficient, and Has This Changed?")
st.caption("Audience: a car dealer deciding which models to stock. Data: ISLP Auto, 392 cars.")
st.write(
    "Use the filters to compare fuel efficiency by vehicle origin, model year, "
    "and number of cylinders. All charts and the data table update together."
)

# Add filters that update every chart and the data table.
st.sidebar.header("Filters")

origins = sorted(auto["origin_name"].unique())
selected_origins = st.sidebar.multiselect(
    "Vehicle origin",
    options=origins,
    default=origins
)

year_min = int(auto["model_year"].min())
year_max = int(auto["model_year"].max())
selected_years = st.sidebar.slider(
    "Model year",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max)
)

cylinder_options = sorted(auto["cylinders"].unique())
selected_cylinders = st.sidebar.multiselect(
    "Cylinders",
    options=cylinder_options,
    default=cylinder_options
)

filtered = auto[
    auto["origin_name"].isin(selected_origins)
    & auto["model_year"].between(selected_years[0], selected_years[1])
    & auto["cylinders"].isin(selected_cylinders)
]

if filtered.empty:
    st.warning("No cars match these filters. Adjust the selections in the sidebar.")
    st.stop()

# Summarize the cars currently selected by the filters.
metric1, metric2, metric3, metric4 = st.columns(4)
metric1.metric("Cars selected", f"{len(filtered)}")
metric2.metric("Average mpg", f"{filtered['mpg'].mean():.1f}")
metric3.metric("Average weight", f"{filtered['weight'].mean():,.0f} lb")
metric4.metric("Average horsepower", f"{filtered['horsepower'].mean():.0f}")

# Chart 1: compare yearly average fuel efficiency across origins.
yearly = (
    filtered.groupby(["model_year", "origin_name"], as_index=False)["mpg"]
    .mean()
)
line_chart = px.line(
    yearly,
    x="model_year",
    y="mpg",
    color="origin_name",
    markers=True,
    title="Average Fuel Efficiency by Model Year",
    labels={
        "model_year": "Model year",
        "mpg": "Average mpg",
        "origin_name": "Vehicle origin",
    },
)

# Chart 2: show how vehicle weight relates to fuel efficiency.
scatter_chart = px.scatter(
    filtered,
    x="weight",
    y="mpg",
    color="origin_name",
    hover_data=["horsepower", "year"],
    title="Vehicle Weight and Fuel Efficiency",
    labels={
        "weight": "Weight (lb)",
        "mpg": "Miles per gallon (mpg)",
        "origin_name": "Vehicle origin",
    },
)

left, right = st.columns(2)
with left:
    st.plotly_chart(line_chart, use_container_width=True)
with right:
    st.plotly_chart(scatter_chart, use_container_width=True)

# Chart 3: compare fuel-efficiency distributions across origins.
box_chart = px.box(
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

# Chart 4: show the distribution of fuel efficiency for selected cars.
histogram = px.histogram(
    filtered,
    x="mpg",
    color="origin_name",
    nbins=20,
    title="Fuel Efficiency Distribution",
    labels={
        "mpg": "Miles per gallon (mpg)",
        "count": "Number of cars",
        "origin_name": "Vehicle origin",
    },
)

left, right = st.columns(2)
with left:
    st.plotly_chart(box_chart, use_container_width=True)
with right:
    st.plotly_chart(histogram, use_container_width=True)

# Let readers inspect and download the cars selected by the filters.
with st.expander("Show the filtered data"):
    display_data = filtered[
        [
            "mpg", "cylinders", "displacement", "horsepower",
            "weight", "acceleration", "model_year", "origin_name"
        ]
    ].rename(columns={"origin_name": "origin", "model_year": "model year"})

    st.dataframe(display_data, use_container_width=True)
    st.download_button(
        "Download filtered data as CSV",
        data=display_data.to_csv(index=False).encode("utf-8"),
        file_name="filtered_auto_data.csv",
        mime="text/csv",
    )
