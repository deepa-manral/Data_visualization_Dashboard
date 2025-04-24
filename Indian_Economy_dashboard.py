import dash
import dash_table
from pathlib import Path
import pandas as pd
from dash import dcc # import dcc from dash
from dash import html # import html from dash
import dash_bootstrap_components as dbc
import plotly.express as px



# Load data from CSV file

# Get the current working directory
current_dir = Path.cwd()

# File path in the same directory
file_path = current_dir / "indianEco.csv"

print("Current Directory:", current_dir)
print("CSV File Path:", file_path)
data = pd.read_csv(file_path)
# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


# Add Decade column for hierarchy
data['Decade'] = (data['Year'] // 10 * 10).astype('Int64')

# Define layout
controls = dbc.Card(
    [
        html.Div(
            [
                dbc.Label("X variable"),
                dcc.Dropdown(
        id='x-axis',
        options=[{'label': col, 'value': col} for col in data.columns],
        value='Year',style={'color':'blue'}#LOAD YEAR TO X AXIS WHEN LOADING DASHBOARD
                ),
            ]
        ),
        html.Div(
            [
                dbc.Label("Y variable"),
                dcc.Dropdown(
        id='y-axis',
        options=[{'label': col, 'value': col} for col in data.columns],
        value='GDP (current US$) ',style={'color':'blue'}#LOAD GDP TO Y AXIS WHEN LOADING DASHBOARD
                ),
            ]
        ),
        html.Div(
            [
        dbc.Label("Color Palette (Z Variable)"),
        dcc.Dropdown(
            id='z-axis',
            options=[
                {'label': 'Rainbow', 'value': 'rainbow'},
                {'label': 'Warm', 'value': 'warm'},
                {'label': 'Cool', 'value': 'cool'},
                {'label': 'Red-Green-Blue', 'value': 'rgb'},
                {'label': 'Orange-Purple-Cyan', 'value': 'opc'},
            ],
            value='rainbow',style={'color': 'blue'}
        ),
            ]
    ),
        html.Div(
            [
        dbc.Label("Graph type"),
        dcc.Dropdown(
            id='graph-type',
            options=[{'label': 'Line chart', 'value': 'line'},
                     {'label': 'Bar chart', 'value': 'bar'},
                     {'label': 'Scatter plot', 'value': 'scatter'}],
            value='line',style={'color':'blue'}#LOAD LINE TO GRAPHTYPE WHEN LOADING DASHBOARD
        ),
           ]
),
        html.Div(
    [
        dbc.Label("Hierarchy"),
        dcc.Dropdown(
            id="hierarchy-dropdown",
            options=[
                {"label": col, "value": col} for col in data.columns],
            value='Year',style={'color':'blue'}
        ),
    ]
),
html.Div(
    [
        dbc.Label("Value"),
        dcc.Dropdown(
            id="value-dropdown",
            options=[{"label": col, "value": col} for col in data.columns],
            value='Population, total',style={'color':'blue'} #LOAD Population, total TO VALUES WHEN LOADING DASHBOARD
        ),
    ]
),
html.Div(
    [
        dbc.Label("Pie Chart Category"),
        dcc.Dropdown(
            id="pie-category",
            options=[{"label": col, "value": col} for col in data.columns],
            value='Population growth (annual %)', style={'color':'blue'} #LOAD Population growth TO PIE CHART CATEGORY WHEN LOADING DASHBOARD
        ),
    ]
),
html.Div(
    [
        dbc.Label("Pie Chart Values"),
        dcc.Dropdown(
            id="pie-values",
            options=[{"label": col, "value": col} for col in data.columns],
            value='Life expectancy at birth, total (years)', style={'color':'blue'}#LOAD Life expectancy at birth, total (years)TO PIE CHART VALUES WHEN LOADING DASHBOARD
        ),
    ]
),

    ],
    body=True,
style={'border-style': 'dotted',
  'border-color': 'red'})

app.layout = dbc.Container(
    [
        html.H1("India's Economy Growth Dashboard",style={'text-align': 'center'}),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=6),#ADDS GRAPHS TO DASHBOARD
                dbc.Col(dcc.Graph(id='plot', className='plot',style={'margin-top': '25px'}), md=6),
                dbc.Col(dcc.Graph(id="sunburst-chart", className="sunburst-chart",style={'margin-top': '25px','margin-bottom': '25px'}), md=6),
                dbc.Col(dcc.Graph(id="treemap-chart", className="treemap-chart",style={'margin-top': '25px','margin-bottom': '25px'}), md=6),
                dbc.Col(dcc.Graph(id="pie-chart", className="pie-chart", style={'margin-top': '25px','margin-bottom': '25px'}), md=6),
                dbc.Col(dash_table.DataTable(
            id='data-table',
            columns=[{'name': col, 'id': col} for col in data.columns],
            data=data.to_dict('records'), page_size=14,
        style_table={'overflowX': 'auto'},
             style_cell={
        'height': 'auto',
        # all three widths are needed
        'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
        'whiteSpace': 'normal'
    },style_data={'color':'black'},style_header={'color':'black'}),md=12)
            ],
            align="center",
        ),
    ],
    fluid=True,
)

# Update plot when dropdowns are changed
@app.callback(
    dash.dependencies.Output('plot', 'figure'),
    [dash.dependencies.Input('x-axis', 'value'),
     dash.dependencies.Input('y-axis', 'value'),
     dash.dependencies.Input('z-axis', 'value'),
     dash.dependencies.Input('graph-type', 'value')])
def update_plot(x_col, y_col,z_col, graph_type):
    if graph_type == 'line':
        fig = px.line(data, x=x_col, y=y_col)
    elif graph_type == 'bar':
        fig = px.bar(data, x=x_col, y=y_col)
    elif graph_type == 'scatter':
        color_palettes = {
            'rainbow': px.colors.sequential.Rainbow,
            'warm': px.colors.sequential.OrRd,
            'cool': px.colors.sequential.Blues,
            'rgb': ['red', 'green', 'blue'],
            'opc': ['orange', 'purple', 'cyan'],
        }

        selected_colors = color_palettes.get(z_col, px.colors.sequential.Rainbow)
        full_colors = selected_colors * (len(data) // len(selected_colors) + 1)

        fig = px.scatter(data, x=x_col, y=y_col, size='GDP (current US$) ', log_x=True, size_max=60)
        fig.update_traces(marker=dict(color=full_colors[:len(data)]))
    return fig

# Update  sunburst-chart when dropdowns are changed
@app.callback(
    dash.dependencies.Output("sunburst-chart", "figure"),
    [
        dash.dependencies.Input("hierarchy-dropdown", "value"),
        dash.dependencies.Input("value-dropdown", "value"),
    ],
)
def update_sunburst_chart(hierarchy_col, value_col):
    fig = px.sunburst(
    data,
    path=[value_col, hierarchy_col],
    values=value_col,
    color=hierarchy_col,
    color_continuous_scale=px.colors.qualitative.Alphabet,
    hover_data={hierarchy_col: True, value_col: ':.2f'}
    )
    fig.update_layout(
    title_text=f"{value_col} by {hierarchy_col} (Sunburst View)",
    title_x=0.5
    )

    return fig

# Update  treemap-chart when dropdowns are changed
@app.callback(
        dash.dependencies.Output("treemap-chart", "figure"),
        [
        dash.dependencies.Input("hierarchy-dropdown", "value"),
        dash.dependencies.Input("value-dropdown", "value"),
    ],
)
def update_treemap_chart(hierarchy_col, value_col):
    fig = px.treemap(
    data,
    path=[value_col, hierarchy_col],
    values=value_col,
    color=hierarchy_col,
    color_continuous_scale='RdBu',
    hover_data={hierarchy_col: True, value_col: ':.2f'}
    )
    fig.update_layout(
    title_text=f"{value_col} by {hierarchy_col} (Treemap View)",
    title_x=0.5
    )

    return fig

# Update  pie-chart when dropdowns are changed
@app.callback(
    dash.dependencies.Output("pie-chart", "figure"),
    [
        dash.dependencies.Input("pie-category", "value"),
        dash.dependencies.Input("pie-values", "value"),
    ],
)
def update_pie_chart(category_col, value_col):
    pie_data = data.groupby(category_col)[value_col].sum().reset_index()
    fig = px.pie(
    pie_data,
    names=category_col,
    values=value_col,
    color_discrete_sequence=px.colors.sequential.RdBu,
    hover_data={category_col: True, value_col: ':.2f'}
    )
    fig.update_layout(
    title_text=f"{value_col} by {category_col} (Pie Chart)",
    title_x=0.5
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False) 