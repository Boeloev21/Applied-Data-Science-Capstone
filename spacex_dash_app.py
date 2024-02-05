# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),

                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                             ],
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                html.Div(dcc.Graph(id='success-pie-chart')),

                                html.Br(),

                                html.P("Payload range (Kg):"),
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                                value=[min_payload, max_payload]),

                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    # Filter the dataframe based on the selected launch site
    if entered_site == 'ALL':
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='Success Count')
        title = 'Total Successful Launches for All Sites'
        fig = px.pie(success_counts, names='Launch Site', values='Success Count', title=title, labels={'Launch Site': 'Launch'})
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        title = f'Total Successful Launches for site {entered_site}'
        # Count success and failure for the selected site
        success_count = filtered_df[filtered_df['class'] == 1].shape[0]
        failure_count = filtered_df[filtered_df['class'] == 0].shape[0]
        # Create a pie chart
        fig = px.pie(names=['Success', 'Failure'], values=[success_count, failure_count], title=title,
                 labels={'Success': f'Success ({success_count})', 'Failure': f'Failure ({failure_count})'})
        return fig


# Callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id="payload-slider", component_property="value")])
def update_scatter_chart(selected_site, selected_payload_range):
    # Filter the dataframe based on the selected launch site
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]
        title = 'Correlation between Payload and Success for all Sites'
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= selected_payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= selected_payload_range[1])]
        title = f'Payload vs Launch Outcome for {selected_site}'

    # Create a scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category', title=title,
                     labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'})

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()