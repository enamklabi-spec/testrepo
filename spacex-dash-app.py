# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
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
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                html.Div([
        html.Label("Select Launch Site:", style={'fontWeight': 'bold', 'fontSize': 16}),
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'}
            ] + [
                {'label': site, 'value': site} 
                for site in spacex_df['Launch Site'].unique()
            ],
            value='ALL',
            placeholder="Select a launch site...",
            searchable=True,
            clearable=False,
            style={'width': '60%', 'margin': 'auto'}
        )
    ], style={'textAlign': 'center', 'padding': '20px'}),
    
    html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'fontWeight': 'bold', 'fontSize': 16}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
        min=0,
        max=10000,
        step=100,
        value=[min_payload, max_payload],
        marks={
            0: '0 kg',
            2500: '2500 kg',
            5000: '5000 kg',
            7500: '7500 kg',
            10000: '10000 kg'
        },
        tooltip={"placement": "bottom", "always_visible": True}
    ),
    html.Br(),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    """
    Render a pie chart showing success/failure distribution based on selected site
    
    Parameters:
    selected_site (str): The selected launch site from dropdown
    
    Returns:
    fig: Plotly pie chart figure
    """
    
    # Check if ALL sites were selected or just a specific launch site
    if selected_site == 'ALL':
        # If ALL sites are selected, use all rows in the dataframe
        filtered_df = spacex_df
        title = 'Total Success Launches for All Sites'
        
        # Create pie chart showing total success launches (class=1) vs failures (class=0)
        success_count = len(filtered_df[filtered_df['class'] == 1])
        failure_count = len(filtered_df[filtered_df['class'] == 0])
        
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success (class=1)', 'Failure (class=0)'],
            title=title,
            color=['Success (class=1)', 'Failure (class=0)'],
            color_discrete_map={
                'Success (class=1)': '#2ECC71',
                'Failure (class=0)': '#E74C3C'
            },
            hole=0.3
        )
        
        # Update layout for better visualization
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
        fig.update_layout(
            showlegend=True,
            height=450,
            width=600,
            annotations=[{
                'text': f'Total: {len(filtered_df)}',
                'x': 0.5,
                'y': 0.5,
                'font_size': 16,
                'showarrow': False
            }]
        )
        
    else:
        # If a specific launch site is selected, filter the dataframe first
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        title = f'Success vs Failed Launches for {selected_site}'
        
        # Calculate success and failure counts for the selected site
        success_count = len(filtered_df[filtered_df['class'] == 1])
        failure_count = len(filtered_df[filtered_df['class'] == 0])
        
        # Create pie chart showing success and failure counts for selected site
        fig = px.pie(
            values=[success_count, failure_count],
            names=['Success (class=1)', 'Failure (class=0)'],
            title=title,
            color=['Success (class=1)', 'Failure (class=0)'],
            color_discrete_map={
                'Success (class=1)': '#2ECC71',
                'Failure (class=0)': '#E74C3C'
            },
            hole=0.3
        )
        
        # Update layout for better visualization
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value'
        )
        fig.update_layout(
            showlegend=True,
            height=450,
            width=600,
            annotations=[{
                'text': f'Total: {len(filtered_df)}',
                'x': 0.5,
                'y': 0.5,
                'font_size': 16,
                'showarrow': False
            }]
        )
    
    return fig
    


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    """
    Update scatter chart based on selected site and payload range
    """
    # Extract payload range
    low, high = payload_range
    
    # Filter data by payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Filter by site if not 'ALL'
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f"Success vs Payload Mass - {selected_site}"
    else:
        title = "Success vs Payload Mass - All Sites"
    
    # Create scatter plot
    if len(filtered_df) > 0:
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='class',
            color_continuous_scale=['#E74C3C', '#2ECC71'],
            title=title,
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'Launch Outcome (0=Fail, 1=Success)'
            },
            hover_data=['Launch Site', 'Flight Number'],
            size='Payload Mass (kg)',
            size_max=15,
            opacity=0.7
        )
        
        # Update layout
        fig.update_layout(
            height=500,
            width=900,
            plot_bgcolor='white',
            xaxis=dict(
                title='Payload Mass (kg)',
                gridcolor='lightgray',
                range=[low, high]
            ),
            yaxis=dict(
                title='Launch Outcome',
                tickvals=[0, 1],
                ticktext=['Failure (0)', 'Success (1)'],
                gridcolor='lightgray',
                range=[-0.5, 1.5]
            ),
            showlegend=False
        )
        
        # Add jitter to y-axis to better visualize overlapping points
        fig.update_traces(
            marker=dict(line=dict(width=1, color='DarkSlateGrey')),
            selector=dict(mode='markers')
        )
        
    else:
        # Empty plot if no data
        fig = px.scatter(
            title="No data available for selected range",
            width=900,
            height=500
        )
        fig.update_layout(
            xaxis=dict(range=[low, high]),
            yaxis=dict(range=[-0.5, 1.5])
        )
    
    return fig

# Run the app
def check_port_usage():
    """Check if port 8050 is in use"""
    try:
        if sys.platform.startswith('win'):
            # Windows
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if ':8050' in line and 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    print(f"⚠️ Port 8050 is being used by PID: {pid}")
                    return pid
        else:
            # Unix/Linux/Mac
            result = subprocess.run(['lsof', '-i', ':8050'], capture_output=True, text=True)
            if result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'LISTEN' in line:
                        parts = line.split()
                        pid = parts[1]
                        print(f"⚠️ Port 8050 is being used by PID: {pid}")
                        return pid
    except:
        print("⚠️ Could not check port usage")
    return None

# Check port
pid = check_port_usage()
if pid:
    print(f"Process with PID {pid} is using port 8050")
    # Kill the process (uncomment the next line to actually kill it)
    # os.system(f"kill -9 {pid}")
else:
    print("✅ Port 8050 is free")



if __name__ == '__main__':
    app.run(port=8050, host='0.0.0.0')

#debug=True


