from xmlrpc import server
import requests 
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

df = pd.read_csv("dtu_data_cleaned.csv ")
# df = df[["parameter","value","datetimeLocal"]]
# print(df.head())
# print(df["parameter"].unique())
df["datetimeLocal"]=pd.to_datetime(df["datetimeLocal"])


app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Delhi AQI"),
    html.Div(id="last-updated-text"),
    dcc.Interval(id="refresh-interval",interval=60*60*1000,n_intervals = 0),
    dcc.Store(id="data-store"),
    
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
r = requests.get(
    "https://air-quality-api.open-meteo.com/v1/air-quality",
    params={
        "latitude": 28.65,
        "longitude": 77.23,
        "hourly": "pm2_5,pm10",
    },
)
print(r.status_code)
print(r.json())

def fetch_live_data():
    r = requests.get(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params={
            "latitude": 28.65,
            "longitude": 77.23,
            "hourly": "pm2_5,pm10",
        },
    )


    if r.status_code == 200:
        df = pd.DataFrame(r.json()["hourly"])
        df["time"]=pd.to_datetime(df["time"],format="%Y-%m-%dT%H:%M")
        # df["parameter"] = df.columns[1] 
        df_long = df.melt(
            id_vars="time",
            value_vars=["pm2_5", "pm10"],
            var_name="parameter",
            value_name="value",
        )
        df_long = df_long.rename(columns={"time": "datetimeLocal"})
        df_long.to_csv("air_quality_data_long.csv", index=False)
        
        
    else:
        print(f"Error fetching data: {r.status_code}")
# # df = pd.DataFrame(r.json()["hourly"])
# df.to_csv("air_quality_data.csv", index=False)
@app.callback(
    Output("data-store","data"),
    Output("last-updated-text","children"),
    Input("refresh-interval","n_intervals")
)
def refresh_data(n):
    df = fetch_live_data()
    ts = f"last updated: {pd.Timestamp.now(tz='Asia/Kolkata').strftime('%Y-%m-%d %H:%M:%S')}"
    return df.to_dict("records"), ts
@app.callback(
        Output("pollutant-graph","figure"),
        [Input("pollutant-dropdown","value"), Input("date-picker-range","start_date"), Input("date-picker-range","end_date"),Input("data-store","data")]
        )
    
def update_chart(selected_pollutant,start_date,end_date,data):
    if data is None:
        return px.line(title="Loading data...")
    
    df = pd.DataFrame(data)
    df["datetimeLocal"] = pd.to_datetime(df["datetimeLocal"])
    if start_date is None or end_date is None:
        return px.line(title="Please select a date range.")
    else:
        start = pd.to_datetime(start_date).tz_localize(df["datetimeLocal"].dt.tz)
        end = pd.to_datetime(end_date).tz_localize(df["datetimeLocal"].dt.tz)
        filtered = df[
            (df["parameter"] == selected_pollutant) &
            (df["datetimeLocal"] >= start) &
            (df["datetimeLocal"] <= end)
        ]
    return px.line(filtered, x="datetimeLocal", y="value", title=f"{selected_pollutant.upper()} levels from {start_date} to {end_date}")
   
if __name__ == "__main__":
    app.run(debug=True)
    
