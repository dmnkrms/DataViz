import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import plotly.graph_objs as go

from datetime import datetime, timedelta

#Options for parameters dropdown
countries = [
  {"label": "United states", "value": "USvideos.csv"},
  {"label": "Canada", "value": "CAvideos.csv"},
  {"label": "Germany", "value": "DEvideos.csv"},
  {"label": "France", "value": "FRvideos.csv"},
  {"label": "Great Britain", "value": "GBvideos.csv"},
  {"label": "India", "value": "INvideos.csv"},
  {"label": "Japan", "value": "JPvideos.csv"},
  {"label": "South Korea", "value": "KRvideos.csv"},
  {"label": "Mexico", "value": "MXvideos.csv"},
  {"label": "Russia", "value": "RUvideos.csv"}
]

categories = ['People & Blogs','Entertainment', 'Comedy', 'Science & Technology', 'Film & Animation', 'News & Politics', 'Sports', 'Music', 'Pets & Animals',
 'Education', 'Howto & Style', 'Autos & Vehicles', 'Travel & Events', 'Gaming', 'Nonprofits & Activism', 'Shows', 'Movies','Trailers']

parameters = [
  {"label": "Views", "value": "views"},
  {"label": "Comments", "value": "comment_count"},
  {"label": "Likes", "value": "likes"},
  {"label": "Sum of videos", "value": "count"}
]
publishParameters = [
  {"label": "All", "value": "all"},
  {"label": "Week", "value": "week"},
  {"label": "Month", "value": "month"},
  {"label": "3 months", "value": "3months"},
  {"label": "Year", "value": "year"}
]

#Application
app = dash.Dash()
app.layout = html.Div([
  html.H1("Youtube data"),
  html.Div(children=[
    dcc.Dropdown(
      id="countriesDropdown",
      options=countries,
      value=countries[0]["value"],
      clearable=False
    ),
    dcc.Dropdown(
      id="categoriesDropdown",
      options=[{"label": i, "value": i} for i in categories],
      multi=True,
      value=categories,
      placeholder="Select a category"
    ),
    dcc.Dropdown(
      id="parametersDropdown",
      options=parameters,
      value=parameters[0]["value"],
      clearable=False
    ),
    dcc.Dropdown(
      id="videopublishDropdown",
      options=publishParameters,
      value=publishParameters[0]["value"],
      clearable=False
    )]
  ),
  
  html.Div(id="graph", children=[dcc.Graph(id="heatmap")])
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
  #Data import
  data = pd.read_csv(f"./Youtube/{countriesDropdown}", index_col="video_id")
  #data = pd.read_csv("./test2.csv", index_col="video_id")

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

  #Filter by publish date
  def publishfilter(filter):
    switcher={
      "all":data,
      "week":data[data['publish_time'] > (data['trending_date'] -timedelta(days=7))],
      "month":data[data['publish_time'] > (data['trending_date'] - timedelta(days=30))],
      "3months":data[data['publish_time'] > (data['trending_date'] - timedelta(days=90))],
      "year":data[data['publish_time'] > (data['trending_date'] - timedelta(days=365))],
    }
    return switcher.get(filter)
  filteredData = publishfilter(videopublishDropdown)

  #Add a count column for grouped video count
  filteredData['count'] = filteredData.groupby(["category_name","trending_date"])['views'].transform('count')

  #Count average grouped by category name and trending date
  meanData = round(filteredData.groupby(["category_name","trending_date"], as_index=False).mean())

  meanData.to_csv(r"C:\Users\rumsa\Desktop\DaViz project\pandas.csv")

  #Select rows where category name is in categories dropdown list
  graphData = meanData[meanData["category_name"].isin(categoriesDropdown)]

  figure = {
    "data": [go.Heatmap(
      x=graphData["trending_date"],
      y=graphData["category_name"],
      z=graphData[parametersDropdownValue],
      hovertemplate='Trending date: %{x}<br>Category: %{y}<br>Average: %{z}<extra></extra>',
      #Why low ones blue, 
      colorscale=[[0, "rgb(12,51,131)"], [0.04, "rgb(10,136,186)"], [0.1, "rgb(242,211,56)"], [0.2, "rgb(242,143,56)"],[0.4, "rgb(217,30,50)"], [1, "rgb(217,30,30)"]]
    )],
    "layout": go.Layout(
      height = 600,
      legend=dict(x=-.1, y=1.2),
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

if __name__ == "__main__":
  app.run_server(debug=True)