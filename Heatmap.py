import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import pandas as pd

import plotly.graph_objs as go

from datetime import datetime, timedelta

#Import data
data = pd.read_csv("./data.csv", index_col="video_id")

#Set correct data types
type_int_list = ["views", "likes", "dislikes", "comment_count"]
for column in type_int_list:
    data[column] = data[column].astype(int)
type_str_list = ["category_name"]
for column in type_str_list:
    data[column] = data[column].astype(str)

#Format dates
data["trending_date"] = pd.to_datetime(data["trending_date"], format="%y.%d.%m")
data["trending_date"] = pd.to_datetime(data["trending_date"]).dt.strftime('%Y-%m-%d')
data['trending_date'] = pd.to_datetime(data['trending_date'])
data["publish_time"] = pd.to_datetime(data["publish_time"], format="%Y-%m-%d")
data['publish_time'] = data['publish_time'].astype(str).str[:-6]
data['publish_time'] = pd.to_datetime(data['publish_time'])

#Available countries
countries = [
  {"label": "United states", "value": "US"},
  {"label": "Canada", "value": "CA"},
  {"label": "Germany", "value": "DE"},
  {"label": "France", "value": "FR"},
  {"label": "Great Britain", "value": "GB"},
  {"label": "India", "value": "IN"},
  {"label": "Japan", "value": "JP"},
  {"label": "South Korea", "value": "KR"},
  {"label": "Mexico", "value": "MX"},
  {"label": "Russia", "value": "RU"}
]

#All categories
categories = data["category_name"].unique() 

#Options for parameters dropdown
parameters = [
  {"label": "Views", "value": "views"},
  {"label": "Comments", "value": "comment_count"},
  {"label": "Likes", "value": "likes"},
  {"label": "Sum of videos", "value": "count"}
]

#Publish date within this period
publishParameters = [
  {"label": "All", "value": "all"},
  {"label": "Week", "value": "week"},
  {"label": "Month", "value": "month"},
  {"label": "3 months", "value": "3months"},
  {"label": "Year", "value": "year"}
]

#Application
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title= "DataViz"
app.layout = dbc.Container([
  html.Br(),
  dbc.Row([
    dbc.Col([
      html.H1("Following YouTube trends"),
      html.P("Data Visualization course project")
    ])
  ]),
  html.Br(),
  html.Br(),
  
  dbc.Row([
    dbc.Col([
      html.H6("Select country"),
      dcc.Dropdown(
        id="countriesDropdown",
        options=countries,
        value=countries[0]["value"],
        clearable=False
      ),
      html.Br(),
      html.H6("Select categories"),
      dcc.Dropdown(
        id="categoriesDropdown",
        options=[{"label": i, "value": i} for i in categories],
        multi=True,
        value=categories,
        placeholder="Select a category"
      ),
    ],width=10),
  ],justify='center'),
  html.Br(),

  dbc.Row([
    dbc.Col([
      html.Div(id="graph", children=[dcc.Graph(id="heatmap")])
    ],width=10),
    dbc.Col([
      html.Br(),
      html.Br(),
      html.H6("Parameters"),
      html.Br(),
      html.P("Value:"),
      dcc.Dropdown(
        id="parametersDropdown",
        options=parameters,
        value=parameters[0]["value"],
        clearable=False
      ),
      html.Br(),
      html.P("Published within:"),
      dcc.Dropdown(
        id="videopublishDropdown",
        options=publishParameters,
        value=publishParameters[0]["value"],
        clearable=False
      )
    ],width=2)
  ]),

  html.Br(),
  dbc.Row([
    dbc.Col(id="table",width=12)
  ],justify='center') 
])

@app.callback(Output("graph", "style"), [Input("categoriesDropdown","value")])
def hide_graph(input):
    if input:
        return {"display":"block"}
    else:
        return {"display":"none"}

@app.callback(Output("heatmap","figure"),[
  Input("countriesDropdown","value"),
  Input("categoriesDropdown","value"),
  Input("parametersDropdown","value"),
  Input("videopublishDropdown","value")])
def update_graph(countriesDropdown,categoriesDropdown,parametersDropdownValue,videopublishDropdown):
  #Set country
  countryData = data[data["country"] == countriesDropdown]

  #Filter by publish date
  def publishfilter(filter):
    switcher={
      "all":countryData,
      "week":countryData[countryData['publish_time'] > (countryData['trending_date'] -timedelta(days=7))],
      "month":countryData[countryData['publish_time'] > (countryData['trending_date'] - timedelta(days=30))],
      "3months":countryData[countryData['publish_time'] > (countryData['trending_date'] - timedelta(days=90))],
      "year":countryData[countryData['publish_time'] > (countryData['trending_date'] - timedelta(days=365))],
    }
    return switcher.get(filter)
  filteredData = publishfilter(videopublishDropdown)

  #Add a count column for grouped video count
  filteredData['count'] = filteredData.groupby(["category_name","trending_date"])['views'].transform('count')

  #Count average grouped by category name and trending date
  meanData = round(filteredData.groupby(["category_name","trending_date"], as_index=False).mean())

  #Select rows where category name is in categories dropdown list
  graphData = meanData[meanData["category_name"].isin(categoriesDropdown)]

  figure = {
    "data": [go.Heatmap(
      x=graphData["trending_date"],
      y=graphData["category_name"],
      z=graphData[parametersDropdownValue],
      hovertemplate='Trending date: %{x}<br>Category: %{y}<br>Average: %{z}<extra></extra>',
      colorscale=[
        [0, "rgb(255,247,236)"],
        [0.06, "rgb(254,232,200)"],
        [0.08, "rgb(253,212,158)"],
        [0.1, "rgb(253,187,132)"],
        [0.15, "rgb(252,141,89)"],
        [0.2, "rgb(239,101,72)"],
        [0.3, "rgb(215,48,31)"],
        [0.5, "rgb(179,0,0)"],
        [0.8,"rgb(127,0,0)"],
        [1,"rgb(103,0,13)"]
      ],
    )],
    "layout": go.Layout(
      height = 600,
      legend=dict(x=-.1, y=1.2),
      margin=dict(t=50, b=50),
      xaxis = dict(
        rangeselector=dict(
          buttons=list([
            dict(count=7,
              label="week",
              step="day",
              stepmode="backward"),
            dict(count=1,
              label="month",
              step="month",
              stepmode="backward"),
            dict(count=3,
              label="3m",
              step="month",
              stepmode="backward"),
            dict(step="all")
          ]),
        ),
        type="date",
        rangeslider=dict(
          visible = True
        ),
      ),
      yaxis = dict(
        categoryorder = "category descending",
        showgrid=False,
        fixedrange=True,
        automargin=True,
        tickvals=meanData["category_name"],
        titlefont=dict(size=20),
      )
    )
  }

  return figure

@app.callback(Output("table", "children"), [
  Input("heatmap","clickData"),
  Input("countriesDropdown","value"),
  Input("parametersDropdown","value")]
)
def generate_table(clickData,countriesDropdown,parametersDropdown):
  if clickData is not None:
    #If not empty z
    if 'z' in clickData['points'][0].keys():
      #Filter by inputs
      tableData = data.loc[(data["trending_date"] == clickData["points"][0]["x"]) &
        (data["category_name"] == clickData["points"][0]["y"]) & 
        (data["country"] == countriesDropdown)]
      
      #Format date
      tableData["publish_time"] = pd.to_datetime(tableData["publish_time"], format="%y.%d.%m")
      tableData["publish_time"] = pd.to_datetime(tableData["publish_time"]).dt.strftime('%Y-%m-%d')

      #Sort values from min to max
      if parametersDropdown == "count":
        sortedtableData = tableData.sort_values(by=["channel_title"])
      else:
        sortedtableData = tableData.sort_values(by=[parametersDropdown])

      #Format table data
      del sortedtableData['country']
      del sortedtableData['category_name']
      del sortedtableData['trending_date']
      sortedtableData.columns = ["Title","Channel","Upload date","Views","Likes","Dislikes","Comments"]
      

      return html.Div(children=[
        html.H5("Trending videos in '"+clickData["points"][0]["y"]+"'"),
        html.P("Date: "+clickData["points"][0]["x"]),
        dbc.Table.from_dataframe(sortedtableData, bordered=True, hover=True,responsive=False),
        html.Br(),
        html.Br()
      ])

if __name__ == "__main__":
  app.run_server(debug=False)