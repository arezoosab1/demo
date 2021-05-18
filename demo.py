import pandas as pd
import plotly.express as px  # (version 4.7.0)

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df_SIS_Seri5or3= pd.read_csv('https://github.com/arezoosab1/demo/blob/main/data.csv')


#finding average lines 
mean_NC = df_SIS_Seri5or3["NC_Mittel"].mean()
mean_NCtoStrahl = df_SIS_Seri5or3['Strahl/NC'].mean()

#list of equipments
equip_lst = df_SIS_Seri5or3.EquipNr.to_list() 


options = []
for i in equip_lst:
    d = {"label": i, "value": i}
    options.append(d)

#------------------------------------------------------------------------------

# App layout
app.layout = html.Div([

    html.H1("Machine Performance Benchmark", style={'text-align': 'center'}),
    dcc.Dropdown(id="slct_equip",
                 options= options,
		         value= 'A0221E0260',
                 multi=False,
                 style={'width': "40%"}
                 ),
    dcc.Dropdown(id="slct_clnm",
                 options=[{'label': 'Country', 'value': 'Maschinenstandort'},
			              {'label': 'Machine DevCode', 'value': 'EquipTyp_Gruppiert'},
			              {'label': 'Machine Type', 'value': 'type'}],
		        value= 'Maschinenstandort',
                 multi=False,
                 style={'width': "40%"}
                 ),

    # html.Div(id='output_container', children=[]),
    html.Br(),

    dcc.Graph(id='my_graph', figure={})

])
#-----------------------------------------------------------------------------------------------
# Output(component_id='output_container', component_property='children'),
# Connect the Plotly graphs with Dash Components
@app.callback(
    Output(component_id='my_graph', component_property='figure'),
    [Input(component_id='slct_equip', component_property='value'),
     Input(component_id='slct_clnm', component_property='value')]
)
def update_graph(slct_equip, slct_clnm):

    df = df_SIS_Seri5or3
    # container = "The equipment chosen by user was: {}".format(slct_equip)
  
    # Plotly Express

    fig = px.scatter(df[df.EquipNr != slct_equip], x="NC_Mittel", y="Strahl/NC", color = slct_clnm, hover_name="EquipNr",
                     hover_data=['top_NC_Mittel', 'top_Strahl_Mittel', 'top_Strahl/NC'])
    fig.update_traces(marker=dict(size=5), selector=dict(mode='markers'))

    fig2 = px.scatter(df[df.EquipNr == slct_equip], x="NC_Mittel", y="Strahl/NC", color = slct_clnm, hover_name="EquipNr",
                      hover_data=['top_NC_Mittel', 'top_Strahl_Mittel', 'top_Strahl/NC'],
                      color_discrete_sequence = ['Black'])
    fig2.update_traces(marker=dict(size=7, line=dict(width=1, color='darkgrey')), selector=dict(mode='markers'))

    fig.add_trace(fig2.data[0])
    fig.add_hline(y=mean_NCtoStrahl, line_width=2, line_dash="dash", line_color="green")
    fig.add_vline(x=mean_NC, line_width=2, line_dash="dash", line_color="green")
    fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_layout(spikedistance=10, hoverdistance=10)
    fig.update_layout(
    xaxis_title="Average NC run-time per year(h)",
    yaxis_title="Beam on (percent)"
    )


    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)

