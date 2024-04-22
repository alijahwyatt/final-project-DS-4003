# %%
#import dependencies
from dash import Dash, dcc, html, Input, Output, callback, dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# %%
#read in df
df = pd.read_csv("data.csv")
df.head()

# %%
#load CSS stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# %%
#initialize app and server
app = Dash(__name__, external_stylesheets=stylesheets)
server = app.server

# %%
#print min and max car years for layout 
min_year = df['model_year'].min()
max_year = df['model_year'].max()

#round down the minimum year to the nearest decade
rounded_min_year = (min_year // 10) * 10

#round up the maximum year to the nearest decade and then add 5
rounded_max_year = (((max_year + 5) // 10) * 10) + 5

# %%
#make sure brands are sorted alphabetically case insensitive and default brand is first brand
sorted_brands = sorted(df['brand'].unique(), key=lambda x: x.lower())
first_brand = sorted_brands[0]


# %%
#define color schemes for graphs
colors = [     '#EF553B', #red
               '#377eb8', #blue
               '#999999', #silver 
               '#54A24B', #dark green
               '#F58518', #orange
               '#EECA3B'] #yellow

# %%
#create app layout
app.layout = html.Div([
    #create headers
    html.H4("Used Vehicle Listings Dashboard",  style={'backgroundColor': '#EF553B', 'color': 'black', 'padding': '10px'}), 
    html.H6("Gain Insight and Data on Pre-Owned Vehicles"),

    #multi-select dropdown
    html.Div([
        html.Label("Select Vehicle Brands:"),
        dcc.Dropdown(
            id='brand-dropdown-multi',
            options=[{'label': brand, 'value': brand} for brand in sorted_brands],
            value=[sorted_brands[0]],  
            multi=True,
            clearable=False,
            style={'width': '50%'}
        ),
        #declare bar chart
        dcc.Graph(id='mileage-bar-chart')
    ], style={'margin-bottom': '5px', 'margin-top': '20px'}),


    #year slider
    html.Div([
        html.Label("Select Range of Years:" ),
        dcc.RangeSlider(
            id='year-range-slider',
            min=min_year,
            max=max_year,
            step=1,
            value=[min_year, max_year],
            marks={year: str(year) for year in range(min_year, max_year + 1)},
        ),
        #declare scatterplot
        dcc.Graph(id='price-scatterplot')
    ], style={'margin': '20px'}),

    #single-select dropdown
    html.Div([
        html.Label("Select Brand:"),
        dcc.Dropdown(
            id='brand-dropdown-single',
            options=[{'label': brand, 'value': brand} for brand in sorted_brands],
            value=sorted_brands[0],
            clearable=False,
            style={'width': '25%'}
        ),
        #declare data table
        html.Div(id='data-table')
    ], style={'margin': '20px'})
], style={'backgroundColor': 'lightgrey'})

# %%
#callback for bar chart
@app.callback(
    Output('mileage-bar-chart', 'figure'),
    [Input('brand-dropdown-multi', 'value')]
)
def update_mileage_chart(selected_brands):
    #filter df to include selected brands
    filtered_df = df[df['brand'].isin(selected_brands)]

    #check if df is empty
    if filtered_df.empty:
        return go.Figure().update_layout(title_text="No data available for selected brands")

    #calculate average mileage
    avg_mileage = filtered_df.groupby(['brand', 'transmission'])['mileage'].mean().reset_index()

    #create faceted bar chart
    fig = px.bar(avg_mileage, x='brand', y='mileage', color='transmission',
                 facet_col='transmission',
                 title="Average Mileage by Vehicle Brand and Transmission Type",
                 labels={'mileage': 'Average Mileage (mi)', 'brand': 'Brand'},
                 color_discrete_sequence=colors)

    #update for readabilty
    fig.update_layout(
        xaxis_title="Brand",
        yaxis_title="Average Mileage",
        showlegend=True,
        paper_bgcolor='lightgrey',
        plot_bgcolor= 'lightgrey',
        title={
            'text': "Average Mileage by Vehicle Brand and Transmission Type",
            'x': 0.5,
            'y': 0.9,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
            'size': 19,
            'color': 'black'
        }
        }
    )

    return fig

# %%
#callback for scatterplot
@app.callback(
    Output('price-scatterplot', 'figure'),
    [Input('brand-dropdown-multi', 'value'),
     Input('year-range-slider', 'value')]
)
def update_price_graph(selected_brands, selected_years):
    filtered_df = df[(df['brand'].isin(selected_brands)) & 
                     (df['model_year'] >= selected_years[0]) & 
                     (df['model_year'] <= selected_years[1])]
    #check if df is empty
    if filtered_df.empty:
        return go.Figure().update_layout(title_text="No data available for selected criteria")
    #create scatterplot
    fig = px.scatter(filtered_df, x='model_year', y='price', color='brand',
                     hover_data=['model'], 
                     labels={'model_year': 'Model Year', 'price': 'Price ($)', 'model': 'Model'},
                     color_discrete_sequence=colors
                     
    )
    #keep it so x axis doesn't display half years
    fig.update_xaxes(
        tickmode='array',
        tickvals=[x for x in range(selected_years[0], selected_years[1] + 1)],
        ticktext=[str(x) for x in range(selected_years[0], selected_years[1] + 1)],
    )
    #add title to center and font change size
    fig.update_layout(
        paper_bgcolor='lightgrey',
        plot_bgcolor='lightgrey',
        title={
            'text': "Price Trends Over Selected Years",
            'x': 0.5,
            'y': 0.95,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {
            'size': 19,
            'color': 'black'
        }
        }
    )
    return fig

# %%
#callback for data table
@app.callback(
    Output('data-table', 'children'),
    [Input('brand-dropdown-single', 'value')]
)
def update_table(selected_brand):
    filtered_df = df[df['brand'] == selected_brand]
    
    #check if df is empty 
    if filtered_df.empty:
        return [html.H6(f"No data available for {selected_brand}", style={'text-align': 'center', 'font-weight': '400', 'font-size': '16px'})]
    
    #create data table and title
    return [
        html.H6(f"Data Table for {selected_brand} vehicles", style={'text-align': 'center'}),
        dash_table.DataTable(
            id='cars-table',
            columns=[{"name": i, "id": i} for i in filtered_df.columns],
            data=filtered_df.to_dict('records'),
            style_table={'height': '300px'},
            style_cell={'textAlign': 'left'},
            page_size=9
        )
    ]

# %%
#run app
if __name__ == '__main__':
    app.run_server(jupyter_mode='tab', debug=True, port=8051)


