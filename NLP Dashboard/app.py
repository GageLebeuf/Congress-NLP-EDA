# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 14:10:19 2021

@author: Gage
"""

import dash_core_components as dcc
import dash_html_components as html
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import geopandas
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt


# Load DF

os.chdir(r"C:\Users\Gage\Desktop\Academic\NLP Dashboard")

master_df = pd.read_csv('data/MasterDF.csv')

master_df = master_df[['user', 'name', 'text','party','text_clean', 'sentiment', 'Code']]



# Initialise the app
app = dash.Dash(__name__)

# Define the app
app.config.suppress_callback_exceptions = True
app.layout = html.Div(
                    children=[
                      html.Div(className='row',  # Define the row element
                               children=[
                                  html.Div(className='four columns div-user-controls', 
                                           children =[  html.H2('Exploratory Data Analysis of  Politician''s Tweets utilizing NLP'),
                                                        html.P('''This dashboard takes a word and plots the average sentiment of tweets containing the selected word '''),
                                                        html.P('''Please enter a word or phrase (Case-Sensitive):'''),
                                                        dcc.Input(id="user_input", debounce = True, type="text", placeholder="Please Input Search Word"),
                                                        html.P('_____________________________________________________________________________________________________'),
                                                        html.P(''),
                                                        html.P('Data set: Tweets from every member of congress during 2021'),
                                                        html.P('This dashboard lays out a geographical NLP driven analysis of political language'),
                                                        html.P('My hopes are to refine my ability to extract sentiment as well as develop a time series component to monitor changes in sentiment over time'),
                                                        html.P(''),
                                                        dcc.Graph(id='bar_graph_2', figure = {})
                                                        ]),  # Define the left element
                                 
                                  html.Div(className='eight columns div-for-charts bg-grey',
                                               children =[  dcc.Graph(id='bar_graph', figure = {}),
                                                            dcc.Graph(id ='country_graph', figure = {}),
                                                            
                                                            
                                                        
                                                                      ])  # Define the right element
                                                                                         ])
                                                                                         ])



@app.callback([Output('bar_graph', 'figure'),
               Output('bar_graph_2', 'figure'),
               Output('country_graph', 'figure')],
              [Input('user_input', 'value')])
                   
                  

def parsetweets(word_selection):

    
                      
    word = str(word_selection)
          
            
        
    # Extract tweets with selected word
            
    search_word = master_df[master_df['text'].str.contains(word)]
            
            
    # Average the sentiment per user for selected tweets
    search_word_user = search_word.groupby(search_word['user']).mean().head(15)
            
            #Plot results
    fig = go.Figure(px.bar(search_word_user, x = search_word_user.index, y = 'sentiment', title = str('Selected Word: ' + word)))
    
    search_word_party = search_word.groupby(search_word['party']).mean()
    
    fig2 = go.Figure(px.bar(search_word_party, x = search_word_party.index, y = 'sentiment', title = str('Democrat | Independent | Republican Sentiment:')))
    
    # Groups sentiment by state
    
    search_word_state = search_word.groupby(search_word['Code']).mean()
    
    countrygraph = px.choropleth(
        search_word_state, locations = search_word_state.index,
        locationmode = 'USA-states', 
        color = search_word_state['sentiment'],
        scope = 'usa',
        title = 'Sentiment for" +'
        
        )

    return fig, fig2, countrygraph
   

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)