import requests
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

API_BASE = "https://p41xpcerk1.execute-api.us-east-1.amazonaws.com/prod"


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


def machine_card(item):
    return dbc.Card(
        [
            dbc.CardHeader(
                f"Machine {item['machineId']}",
                className="text-center fw-bold"
            ),
            dbc.CardBody(
                [
                    html.P(f"Energy: {item['energy']}"),
                    html.P(f"Temp: {item['temperature']} °C"),
                    html.P(f"Humidity: {item['humidity']}%"),
                    html.P(f"Load: {item['load']}"),
                    html.P(f"State: {item['state']}"),
                    html.P(f"Source: {item.get('source', 'unknown')}"),
                ]
            ),
        ],
        color="dark",
        outline=True,
        className="m-2 shadow-lg",
        style={"width": "250px"}
    )


app.layout = dbc.Container(
    [
        html.H1("Factory Energy Dashboard", className="text-center my-4"),

        # Latest readings
        dbc.Row(id="latest-cards", className="d-flex flex-wrap justify-content-center"),

        html.Hr(),

        # Machine selector
        html.Div(
            [
                html.Label("Select Machine:"),
                dcc.Dropdown(
                    id="machine-dropdown",
                    options=[{"label": f"M{i}", "value": f"M{i}"} for i in range(1, 4)],
                    value="M1",
                    style={"width": "200px", "color": "black"}
                ),
            ],
            className="mb-4"
        ),

        # History graph
        dcc.Graph(id="history-graph"),

        html.Hr(),

        html.H2("Advanced Analytics", className="text-center my-4"),

        # 2x2 grid of advanced charts
        dbc.Row([
            dbc.Col(dcc.Graph(id="multi-axis-chart"), md=6),
            dbc.Col(dcc.Graph(id="state-pie-chart"), md=6),
        ]),

        dbc.Row([
            dbc.Col(dcc.Graph(id="machine-comparison-chart"), md=6),
            dbc.Col(dcc.Graph(id="avg-energy-bar-chart"), md=6),
        ]),

        # Auto-refresh every 5 seconds
        dcc.Interval(id="refresh", interval=5000, n_intervals=0)
    ],
    fluid=True
)


@app.callback(
    Output("latest-cards", "children"),
    Input("refresh", "n_intervals")
)
def update_latest(_):
    try:
        r = requests.get(f"{API_BASE}/latest").json()
    except:
        return [html.Div("Error fetching latest data", className="text-danger")]

    return [machine_card(item) for item in r]


@app.callback(
    Output("history-graph", "figure"),
    Input("machine-dropdown", "value"),
    Input("refresh", "n_intervals")
)
def update_history(machine, _):
    try:
        r = requests.get(f"{API_BASE}/history?machineId={machine}").json()
    except:
        return go.Figure()

    timestamps = [i["timestamp"] for i in r]
    energy = [i["energy"] for i in r]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=timestamps,
            y=energy,
            mode="lines+markers",
            line=dict(color="#00E5FF", width=3),
            marker=dict(size=6)
        )
    )

    fig.update_layout(
        title=f"Energy History for {machine}",
        xaxis_title="Time",
        yaxis_title="Energy",
        template="plotly_dark",
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
        font=dict(color="white")
    )

    return fig


@app.callback(
    Output("multi-axis-chart", "figure"),
    Output("state-pie-chart", "figure"),
    Output("machine-comparison-chart", "figure"),
    Output("avg-energy-bar-chart", "figure"),
    Input("refresh", "n_intervals")
)
def update_advanced_charts(_):
    try:
        r = requests.get(f"{API_BASE}/latest").json()
    except:
        return go.Figure(), go.Figure(), go.Figure(), go.Figure()

    machines = [i["machineId"] for i in r]
    energy = [i["energy"] for i in r]
    temp = [i["temperature"] for i in r]
    humidity = [i["humidity"] for i in r]
    states = [i["state"] for i in r]

    
    multi = go.Figure()

    multi.add_trace(go.Bar(
        x=machines, y=energy, name="Energy", marker_color="#00E5FF"
    ))
    multi.add_trace(go.Scatter(
        x=machines, y=temp, name="Temperature", mode="lines+markers",
        yaxis="y2", line=dict(color="orange")
    ))

    multi.update_layout(
        title="Energy vs Temperature",
        yaxis=dict(title="Energy"),
        yaxis2=dict(title="Temperature", overlaying="y", side="right"),
        template="plotly_dark"
    )

   
    pie = go.Figure(
        data=[go.Pie(
            labels=machines,
            values=[1 for _ in machines],
            marker=dict(colors=["#00E5FF", "orange", "red"])
        )]
    )
    pie.update_layout(title="Machine State Distribution", template="plotly_dark")

    compare = go.Figure()
    compare.add_trace(go.Bar(
        x=machines, y=energy, name="Energy", marker_color="#00E5FF"
    ))
    compare.add_trace(go.Bar(
        x=machines, y=temp, name="Temperature", marker_color="orange"
    ))
    compare.add_trace(go.Bar(
        x=machines, y=humidity, name="Humidity", marker_color="purple"
    ))

    compare.update_layout(
        title="Machine Comparison",
        barmode="group",
        template="plotly_dark"
    )

    avg_bar = go.Figure()
    avg_bar.add_trace(go.Bar(
        x=machines, y=energy, marker_color="#00E5FF"
    ))
    avg_bar.update_layout(
        title="Average Energy per Machine",
        template="plotly_dark"
    )

    return multi, pie, compare, avg_bar


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050)