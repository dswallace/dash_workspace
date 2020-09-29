# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np


def percent_in_borehole(x_pts, y_pts, borehole_radius):
    count = 0
    for x, y in zip(x_pts, y_pts):
        if np.sqrt(x**2 + y**2) <= borehole_radius:
            count += 1

    try:
        return (count/len(x_pts))*100.
    except ZeroDivisionError:
        return 0


app = dash.Dash(__name__)

server = app.server

tool_diameter = 3.5
f1 = 10
f4 = 15
hole_pos = [0, 0]

app.layout = html.Div([
    html.H3("NMR Wireline Tool Sensitivity Graph",
            style={'text-align': 'center', 'width': '45%', 'margin-bottom': '0%'}),
    html.Div([
        dcc.Graph(id='borehole-plot')
    ],
        style={'display': 'block', 'margin-left': '5%', 'margin-right': '5%', 'margin-top': '0%', 'margin-bottom': '0%'}
    ),
    html.Div([
        html.Hr(),
        html.Div(id='f1-percentage-calc', style={'color': 'blue', 'fontSize': 14}),
        html.Div(id='f4-percentage-calc', style={'color': 'red', 'fontSize': 14}),
        html.Hr(),
        html.Div([
            dcc.Dropdown(
                id='borehole-scenario',
                options=[{"label": "Centered Scenario", "value": "center"},
                         {"label": "'Wall-Hugger' Scenario", "value": "wall"}],
                value="center"
            )
        ]),
        html.Br(),
        html.Br(),
        html.Div(children="Borehole Diameter in Inches"),
        dcc.Slider(
            id='borehole-slider',
            min=5,
            max=12,
            value=5,
            marks={5: {'label': '5 in.', 'style': {'font-size': 18}},
                   6: {'label': '6 in.', 'style': {'font-size': 18}},
                   7: {'label': '7 in.', 'style': {'font-size': 18}},
                   8: {'label': '8 in.', 'style': {'font-size': 18}},
                   9: {'label': '9 in.', 'style': {'font-size': 18}},
                   10: {'label': '10 in.', 'style': {'font-size': 18}},
                   11: {'label': '11 in.', 'style': {'color': 'red', 'font-size': 18}},
                   12: {'label': '12 in.', 'style': {'color': 'red', 'font-size': 18}}},
            step=None
        )
    ], style={'width': '45%', 'display': 'inline-block', 'vertical-align': 'middle', 'font-family': 'helvetica'}
    )
])


@app.callback(
    [Output('borehole-plot', 'figure'),
     Output('f1-percentage-calc', 'children'),
     Output('f4-percentage-calc', 'children')],
    [Input('borehole-slider', 'value'),
     Input('borehole-scenario', 'value')])
def update_figure(selected_diameter, borehole_scenario):
    fig = go.Figure()

    # Set axes properties
    fig.update_xaxes(range=[-15, 15], zeroline=False)
    fig.update_yaxes(range=[-15, 15])

    # Grab tool position coordinates
    tool_pos = [0, 0]
    if borehole_scenario == "wall":
        tool_pos = [0 - (selected_diameter / 2.) + (tool_diameter / 2.), 0]

    # Frequency 4 Shell
    f4_theta = np.linspace(0, 2 * np.pi, 100)
    f4_r = f4/2.
    f4_x1 = f4_r * np.cos(f4_theta) + tool_pos[0]
    f4_x2 = f4_r * np.sin(f4_theta)

    fig.add_scatter(
        x=f4_x1,
        y=f4_x2,
        fill=None,
        mode='lines',
        name='F4 shell',
        opacity=1,
        marker_color='red',
        line_dash='dash',
        hovertemplate='<b>F4 Shell</b><extra></extra>',
        showlegend=True
    )

    # Frequency 1 Shell
    f1_theta = np.linspace(0, 2 * np.pi, 100)
    f1_r = f1/2.
    f1_x1 = f1_r * np.cos(f1_theta) + tool_pos[0]
    f1_x2 = f1_r * np.sin(f1_theta)

    fig.add_scatter(
        x=f1_x1,
        y=f1_x2,
        fill=None,
        mode='lines',
        name='F1 shell',
        hovertemplate='<b>F1 Shell</b><extra></extra>',
        opacity=1,
        marker_color='blue',
        line_dash='dash',
        showlegend=True
    )

    # Borehole Circle
    bh_theta = np.linspace(0, 2 * np.pi, 100)
    bh_r = selected_diameter/2.
    bh_x1 = bh_r * np.cos(bh_theta)
    bh_x2 = bh_r * np.sin(bh_theta)

    fig.add_scatter(
        x=bh_x1,
        y=bh_x2,
        fill=None,
        mode='lines',
        name='Borehole',
        hovertemplate='<b>Borehole</b><extra></extra>',
        opacity=1,
        marker_color='black',
        showlegend=True
    )

    # Tool Circle
    theta = np.linspace(0, 2 * np.pi, 100)
    r = tool_diameter / 2.
    x1 = r * np.cos(theta) + tool_pos[0]
    x2 = r * np.sin(theta)

    fig.add_scatter(
        x=x1,
        y=x2,
        fill="toself",
        mode='lines',
        name='NMR Tool',
        text='NMR Tool',
        opacity=1,
        marker_color='green',
        showlegend=True
    )

    # Calculate percentage of f4 inside borehole
    f4_pct = percent_in_borehole(f4_x1, f4_x2, selected_diameter/2.)

    # Calculate percentage of f1 inside borehole
    f1_pct = percent_in_borehole(f1_x1, f1_x2, selected_diameter / 2.)

    # Set figure size
    fig.update_layout(transition_duration=100, width=500, height=500)

    fig.write_html("test.html")

    return fig, 'Percent of F1 inside borehole: {} %'.format(int(f1_pct)), \
           'Percent of F4 inside borehole: {} %'.format(int(f4_pct))


if __name__ == '__main__':
    app.run_server(debug=True)
