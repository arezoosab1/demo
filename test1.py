import pandas as pd
import datetime as dt
import plotly.express as px  # (version 4.7.0)
#import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

SISHours= pd.read_excel('C:\EaaS\SISHours.xlsx')

SISHours["Date"]=SISHours["Betrachtungszeitpunkt"].dt.strftime('%Y-%m-%d' )
df_SIS = SISHours.filter(['EquipNr','Date','Maschinenstandort', 'EquipTyp_Gruppiert', 'IB1', 'IB2', 'NC_Mittel','Strahl_Mittel', ], axis=1)
df_SIS[['year','month', 'day']] = df_SIS.Date.str.split("-",expand=True,)

df_SIS_mean = df_SIS.groupby(["EquipNr", "Maschinenstandort", "EquipTyp_Gruppiert"], as_index=False)["NC_Mittel", "Strahl_Mittel"].mean()
df_SIS_mean['NC_Mittel'] = df_SIS_mean['NC_Mittel'] * 365
df_SIS_mean['Strahl_Mittel'] = df_SIS_mean['Strahl_Mittel'] * 365
df_SIS_mean['Strahl/NC'] =  (df_SIS_mean.Strahl_Mittel / df_SIS_mean.NC_Mittel) *100
df_SIS_mean = df_SIS_mean[df_SIS_mean['Strahl/NC'] < 100].reset_index()

#only series 5000 and 3000
regex5 = r'5\d{3}'
regex3 = r'3\d{3}'

regex = [regex5, regex3]
df_SIS_Seri5or3 = df_SIS_mean[df_SIS_mean.EquipTyp_Gruppiert.str.contains('|'.join(regex))].reset_index()
df_SIS_Seri5or3['type'] = ' '

for i in range (0, len (df_SIS_Seri5or3)):
    if 'fiber' in df_SIS_Seri5or3['EquipTyp_Gruppiert'].loc[i]:
        df_SIS_Seri5or3['type'].loc[i] = 'fiber'
    if not 'fiber' in df_SIS_Seri5or3['EquipTyp_Gruppiert'].loc[i]:
        df_SIS_Seri5or3['type'].loc[i] = 'CO2'

df_SIS_Seri5or3['top_NC_Mittel'] = ' '
df_SIS_Seri5or3['top_Strahl_Mittel'] = ' '
df_SIS_Seri5or3['top_Strahl/NC'] = ' '

for i in range (0, len (df_SIS_Seri5or3)):
    nc = len(df_SIS_Seri5or3[df_SIS_Seri5or3['NC_Mittel'] > df_SIS_Seri5or3['NC_Mittel'].loc[i]])
    s = len(df_SIS_Seri5or3[df_SIS_Seri5or3['Strahl_Mittel'] > df_SIS_Seri5or3['Strahl_Mittel'].loc[i]])
    r = len(df_SIS_Seri5or3[(df_SIS_Seri5or3['NC_Mittel'] > df_SIS_Seri5or3['NC_Mittel'].loc[i]) & (df_SIS_Seri5or3['Strahl_Mittel'] > df_SIS_Seri5or3['Strahl_Mittel'].loc[i])] )

    l = len(df_SIS_Seri5or3)
    df_SIS_Seri5or3['top_NC_Mittel'].loc[i] = 100 - (nc/l)*100
    df_SIS_Seri5or3['top_Strahl_Mittel'].loc[i] = 100 - (s/l)*100
    df_SIS_Seri5or3['top_Strahl/NC'].loc[i] = 100 - (r/l)*100

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
                
#colunms = ['Maschinenstandort', 'EquipTyp_Gruppiert']

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

    fig = px.scatter(df[df.EquipNr != slct_equip], x="NC_Mittel", y="Strahl/NC", color = slct_clnm, hover_name="EquipNr", hover_data=['top_NC_Mittel','top_Strahl_Mittel','top_Strahl/NC'])
    fig.update_traces(marker=dict(size=4), selector=dict(mode='markers'))

    fig2 = px.scatter(df[df.EquipNr == slct_equip], x="NC_Mittel", y="Strahl/NC", hover_name="EquipNr", hover_data=['top_NC_Mittel','top_Strahl_Mittel','top_Strahl/NC'], color_discrete_sequence = ['Black'])
    fig2.update_traces(marker=dict(size=6, line=dict(width=1, color='darkgrey')), selector=dict(mode='markers'))

    fig.add_trace(fig2.data[0])



    fig.add_hline(y=mean_NCtoStrahl)
    fig.add_vline(x=mean_NC)
    fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_layout(spikedistance=10, hoverdistance=10)
    fig.update_layout(
    xaxis_title="average NC run-time per year(h)",
    yaxis_title="Beam on (percent)"
    )


    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=False)

