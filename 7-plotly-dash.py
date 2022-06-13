# Import required libraries
import pandas as pd
from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px
import wget

# Read the airline data into pandas dataframe
spacex_csv_file = wget.download("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")
spacex_df=pd.read_csv(spacex_csv_file)
df = spacex_df[['Launch Site','Payload Mass (kg)','Booster Version Category','class']]
df.rename(columns={'Payload Mass (kg)':'Payload Mass'}, inplace=True)

launchSite = list(df['Launch Site'].unique())
launchSite.append('All')

max_payload = df['Payload Mass'].max()
min_payload = df['Payload Mass'].min()

# Create a dash application
app = Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36','font-size': 40}),   
    html.Br(),
    
    # Dropdown - 选择 site
    # id=site
    dcc.Dropdown(id='site',
                options=[{'label':i, 'value':i} for i in launchSite],
                placeholder='Select a site',
                value='All',
                style={'width':'80%', 'padding':'3px', 'font-size':'20px', 'text-alight':'center'}),
    # 图表 1 - pie chart
    html.Div(dcc.Graph(id='pie-chart')),
    html.Br(),
    html.P("Payload range (Kg):"),

    # RangeSlider
    # id=payload
    dcc.RangeSlider(id='payload',
                    min=min_payload,
                    max=max_payload,
                    step=2000,
                    value=[min_payload, max_payload]),
    # 图表 2 - catplot
    html.Div(dcc.Graph(id='catplot')),
    ])

# 通过输入的 site 来绘制第一张图表
@app.callback(
    Output(component_id='pie-chart', component_property='figure'),
    Input(component_id='site', component_property='value'))
def get_graph1(site):
    
    if site == 'All': 
        successRate = df.groupby('Launch Site')['class'].mean().reset_index()
        plot = px.pie(
            successRate,
            values='class',
            names='Launch Site',
            title='Success Rate for Different Sites')
    else:
        filtered_df = df[df['Launch Site']==site]
        filtered_df = filtered_df.groupby('class').count().reset_index()        
        plot = px.pie(filtered_df, 
                     values='Launch Site', 
                     names='class', 
                     title=f'Success Rate for {site}')        
        # return the outcomes piechart for a selected site

    return plot

# 通过输入的 site, payload 来输出第二张图表
@app.callback(
    Output(component_id='catplot', component_property='figure'),
    [Input(component_id='site', component_property='value'),
    Input(component_id='payload', component_property='value')])
def get_graph2(site, payload):
    if site == 'All':
        filtered_df = df[(df['Payload Mass']>=int(payload[0])) & (df['Payload Mass']<=int(payload[1]))]
        plot = px.scatter(
            filtered_df,
            x='Payload Mass',
            y='class',
            color='Booster Version Category',
            title='Success Rate for Different Booster'
        )
    else:
        filtered_df = df[(df['Payload Mass']>=int(payload[0])) & 
        (df['Payload Mass']<=int(payload[1])) &
        (df['Launch Site']==site)]
        plot = px.scatter(
            filtered_df,
            x='Payload Mass',
            y='class',
            color='Booster Version Category',
            title=f'Success Rate for Different Booster between {payload[0]} and {payload[1]} kg'
        )

    return plot

# Run the app
if __name__ == '__main__':
    app.run_server()