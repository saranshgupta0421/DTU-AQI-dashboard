from xmlrpc import server

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("dtu_data_cleaned.csv")
# df = df[["parameter","value","datetimeLocal"]]
# print(df.head())
# print(df["parameter"].unique())
df["datetimeLocal"]=pd.to_datetime(df["datetimeLocal"])


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("interactive page"),
    dcc.DatePickerRange(
        id="date-picker-range",
        max_date_allowed=df["datetimeLocal"].max().date(),
        min_date_allowed=df["datetimeLocal"].min().date(),
        start_date=df["datetimeLocal"].min().date(),
        end_date=df["datetimeLocal"].max().date(),
        initial_visible_month=df["datetimeLocal"].min().date()
    ),
    dcc.Dropdown(
        id="pollutant-dropdown",
        options=[{"label":i.upper(),"value":i} for i in df["parameter"].unique()],
    
        value="pm10"),
    dcc.Graph(id="pollutant-graph")
])
@app.callback(
        Output("pollutant-graph","figure"),
        [Input("pollutant-dropdown","value"), Input("date-picker-range","start_date"), Input("date-picker-range","end_date")]
    )
def update_chart(selected_pollutant,start_date,end_date):
    filtered = df[
        (df["parameter"] == selected_pollutant) &
        (df["datetimeLocal"] >= start_date) &
        (df["datetimeLocal"] <= end_date)
    ]
    fig = px.line(filtered, x="datetimeLocal", y="value")
    return fig
if __name__ == "__main__":
    app.run(debug=True)
    