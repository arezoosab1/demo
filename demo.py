import pandas as pd
import plotly.express as px  # (version 4.7.0)

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

df_SIS_Seri5or3= pd.read_csv('C:\EaaS\data.csv')


#finding average lines 
median_NC = df_SIS_Seri5or3["NCtime(h/year)"].median()
median_NCtoStrahl = df_SIS_Seri5or3['BeamON%'].median()

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
                 options=[{'label': 'Country', 'value': 'Country'},
			              {'label': 'Machine DevCode', 'value': 'Machine_DevCode'},
			              {'label': 'Machine Type', 'value': 'MachineType'}],
		        value= 'Machine_DevCode',
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

    fig = px.scatter(df[df.EquipNr != slct_equip], x='NCtime(h/year)', y='BeamON%', color = slct_clnm, hover_name="EquipNr",
                     hover_data=['Machine_DevCode','MachineType','Country','top_NCtime','top_BeamON%','top_overall'])
    fig.update_traces(marker=dict(size=5), selector=dict(mode='markers'))

    fig2 = px.scatter(df[df.EquipNr == slct_equip], x='NCtime(h/year)', y='BeamON%', color = slct_clnm, hover_name="EquipNr",
                      hover_data=['Machine_DevCode', 'MachineType', 'Country', 'top_NCtime', 'top_BeamON%', 'top_overall'],
                      color_discrete_sequence = ['Black'])
    fig2.update_traces(marker=dict(size=7, line=dict(width=1, color='darkgrey')), selector=dict(mode='markers'))

    fig.add_trace(fig2.data[0])
    fig.add_hline(y=median_NCtoStrahl, line_width=2, line_dash="dash", line_color="green")
    fig.add_vline(x=median_NC, line_width=2, line_dash="dash", line_color="green")
    fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_layout(spikedistance=10, hoverdistance=10)
    fig.update_layout(xaxis_range=[0, 9000])
    fig.update_layout(yaxis_range=[0, 100])

    fig.update_layout(
        xaxis_title="Average NC run-time per year(h)",
        yaxis_title="Beam on (percent)")



    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)

