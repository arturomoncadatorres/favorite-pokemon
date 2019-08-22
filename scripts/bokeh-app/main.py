# -*- coding: utf-8 -*-
"""
To run this on a bokeh server, in a command prompt run
bokeh serve --show favorite_pokemon_ui.py

Created on Sun Aug 18 19:07:52 2019
@author: Arturo Moncada-Torres
arturomoncadatorres@gmail.com
"""
import pandas as pd
import numpy as np
import pathlib

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.layouts import layout, row, column
from bokeh.models import ColumnDataSource
from bokeh.models import Range1d, Panel, Tabs, FactorRange
from bokeh.models import Arrow, NormalHead
from bokeh.models import Legend, LegendItem
from bokeh.models import DatetimeTickFormatter
from bokeh.models.tools import HoverTool
from bokeh.models.widgets import Div, Select

from . import pokefunctions

# Define paths.
PATH_DATA = pathlib.Path(r"../../data")
PATH_OUTPUT = pathlib.Path(r"../../output")
if not PATH_OUTPUT.exists():
    PATH_OUTPUT.mkdir()

# Define parameters.
POKEMON_PANEL_WIDTH = 200
PLOT_HEIGHT = 350


#%%

# Preparing the data is time consuming. Thus, we save the processed data and load it if possible.
df = pokefunctions.read_raw_data(PATH_DATA/'responses.xlsx')

# Preparing the data is time consuming. Thus, we save the processed data and load it if possible.
if (PATH_DATA/'df_ranked.csv').exists():
    
    df_ranked = pd.read_csv(PATH_DATA/'df_ranked.csv', index_col=0)
else:
    # Add additional columns.
    df['sprite_source'] = df.index.map(pokefunctions.get_sprite_url)
    df['generation_color'] = df['generation'].map(lambda x: pokefunctions.generation_palette()[x])

    # Add ranking information and sort again by Pokemon number.
    df_ranked = pokefunctions.rank_raw_data(df)
    
    df_ranked.to_csv(PATH_DATA/'df_ranked.csv')

df = df_ranked.sort_index()

#
df_votes = pokefunctions.read_votes(PATH_DATA/'responses.xlsx')
df_votes_init = pokefunctions.process_pokemon_votes(df_votes, 'Bulbasaur')
df_votes_max = pokefunctions.process_pokemon_votes(df_votes, 'Charizard')


#%%
# Define tools.
tools = ['pan', 'zoom_in', 'zoom_out', 'wheel_zoom', 'reset']

initial_number = 1
initial_name = df.loc[initial_number, 'name']
initial_generation = df.loc[initial_number, 'generation']
initial_votes = df.loc[initial_number, 'votes']
initial_ranking_overall = df.loc[initial_number, 'ranking_overall']
initial_ranking_generation = df.loc[initial_number, 'ranking_generation']


# Create Pokemon display (sprite and info).
sprite = Div(text="""{}""".format(pokefunctions.get_sprite_html_text(initial_number, alt=initial_name, width=150)), width=POKEMON_PANEL_WIDTH, height=int(PLOT_HEIGHT*.35))

info = Div(text="""
<h3>{0}. {1}</h3>
<table style="width:100%">
  <tr>
    <td><b>Generation:</b></td>
    <td>{2:.0f}</td>
  </tr>
  <tr>
    <td><b>Votes:</b></td>
    <td>{3:.0f}</td>
  </tr>
  <tr>
    <td><b>Overall ranking:</b></td>
    <td>{4:.0f}</td>
  </tr>
  <tr>
    <td><b>Generation ranking:</b></td>
    <td>{5:.0f}</td>
  </tr>
</table>
""".format(initial_number, initial_name, initial_generation, initial_votes, initial_ranking_overall, initial_ranking_generation), width=POKEMON_PANEL_WIDTH, height=int(PLOT_HEIGHT*.6))

# Create Select.
select = Select(title="Pokemon:", value=df['name'].tolist()[0], options=df['name'].tolist())

# Create the "Overall" plot.
source_overall = ColumnDataSource(df_ranked[['name', 'votes', 'generation', 'generation_color', 'ranking_overall', 'ranking_generation', 'sprite_source']])
pokemon_names = source_overall.data['name']
pokemon_votes = source_overall.data['votes']

# Notice that initializing the figure with y_range=pokemon_names 
# doesn't allow the option to bound the plot.
p_overall = figure(y_range=FactorRange(factors=pokemon_names, bounds=(0, len(pokemon_names))), 
                   x_axis_label='Votes', plot_height=PLOT_HEIGHT, tools=tools)
r_overall = p_overall.hbar(y='name', left=0, right='votes', height=1, color='generation_color', source=source_overall)
p_overall.x_range = Range1d(0, max(pokemon_votes)*1.05, bounds=(0, max(pokemon_votes)*1.05))
p_overall.ygrid.grid_line_color = None
y_coord = len(df_ranked) - initial_ranking_overall + 0.5
arrow_overall = Arrow(end=NormalHead(line_color='red', fill_color='red', line_width=0, size=10, line_alpha=0.75, fill_alpha=0.75), 
                      line_color='red', line_width=2.5, line_alpha=0.75, 
                      x_start=initial_votes + max(pokemon_votes)*0.05, x_end=initial_votes, 
                      y_start=y_coord, y_end=y_coord)
p_overall.add_layout(arrow_overall)

legend = Legend(items=[
    LegendItem(label='1', renderers=[r_overall], index=6),
    LegendItem(label='2', renderers=[r_overall], index=37),
    LegendItem(label='3', renderers=[r_overall], index=1),
    LegendItem(label='4', renderers=[r_overall], index=10),
    LegendItem(label='5', renderers=[r_overall], index=2),
    LegendItem(label='6', renderers=[r_overall], index=14),
    LegendItem(label='7', renderers=[r_overall], index=8),
], title='Generation', location='bottom_right')
p_overall.add_layout(legend)

hover_overall = HoverTool(mode='hline')
hover_overall.tooltips = """
<table style="width:175px">
  <tr>
    <th>@name</th>
    <td rowspan=4><image src=@sprite_source alt="" width="75"/></td>
  </tr>
  <tr>
    <td><strong>Generation: </strong>@generation</td>
  </tr>
  <tr>
    <td><strong>Votes: </strong>@votes</td>
  </tr>
  <tr>
    <td><strong>Ranking: </strong>@ranking_overall</td>
  </tr>
</table>
"""
p_overall.add_tools(hover_overall)
    
    
# Create the "Generation" plot.
df_generation = df_ranked.query('generation==' + str(initial_generation))
source_generation = ColumnDataSource(df_generation[['name', 'votes', 'generation_color', 'ranking_generation', 'sprite_source']])
pokemon_names_gen = source_generation.data['name']
pokemon_votes_gen = source_generation.data['votes']

p_generation = figure(y_range=FactorRange(factors=pokemon_names_gen, bounds=(0, len(pokemon_names_gen))), 
                      x_axis_label='Votes', plot_height=PLOT_HEIGHT, tools=tools)
r_generation = p_generation.hbar(y='name', left=0, right='votes', height=1, color='generation_color', source=source_generation)
p_generation.x_range = Range1d(0, max(pokemon_votes_gen)*1.05, bounds=(0, max(pokemon_votes_gen)*1.05))
p_generation.ygrid.grid_line_color = None
y_coord = pokemon_names_gen.tolist().index(initial_name) + 0.5

pokemon_names_gen.tolist()
arrow_generation = Arrow(end=NormalHead(line_color='red', fill_color='red', line_width=0, size=10, line_alpha=0.75, fill_alpha=0.75), 
                      line_color='red', line_width=2.5, line_alpha=0.75, 
                      x_start=initial_votes + max(pokemon_votes_gen)*0.05, x_end=initial_votes, 
                      y_start=y_coord, y_end=y_coord)
p_generation.add_layout(arrow_generation)
hover_generation = HoverTool(mode='hline')
hover_generation.tooltips = """
<table style="width:175px">
  <tr>
    <th>@name</th>
    <td rowspan=4><image src=@sprite_source alt="" width="75"/></td>
  </tr>
  <tr>
    <td><strong>Votes: </strong>@votes</td>
  </tr>
  <tr>
    <td><strong>Ranking: </strong>@ranking_generation</td>
  </tr>
</table>
"""
p_generation.add_tools(hover_generation)


# Create the "Votes in time" plot.
source_time = ColumnDataSource(df_votes_init[['timestamp', 'timestamp_h', 'vote']])
timestamp = source_time.data['timestamp']
votes = source_time.data['vote']
max_votes = max(df_votes_max['vote'])
color = pokefunctions.get_sprite_color(pokefunctions.get_sprite(initial_number))

p_time = figure(plot_height=PLOT_HEIGHT, x_axis_type='datetime', x_axis_label="Time", y_axis_label="Votes", tools=tools)
# Notice how we need to give a huge width value since the datetime axis has a resolution of miliseconds.
# See https://stackoverflow.com/questions/45711567/categorical-y-axis-and-datetime-x-axis-with-bokeh-vbar-plot
r_time = p_time.vbar(x='timestamp', bottom=0, top='vote', width=3600000, line_color='#696969', fill_color=color, source=source_time)

p_time.x_range = Range1d(df_votes_init['timestamp'].min(), df_votes_init['timestamp'].max(), bounds=(df_votes_init['timestamp'].min(), df_votes_init['timestamp'].max()))
p_time.y_range = Range1d(0, max_votes*1.05, bounds=(0, max_votes*1.05))

x_formatter = DatetimeTickFormatter(minutes=['%H:%M'], 
                                    hours=['%H:%M'], 
                                    days=['%H:%M'], 
                                    months=['%H:%M'], 
                                    years=['%H:%M'])
p_time.xaxis.formatter = x_formatter
hover_time = HoverTool(mode='vline')
hover_time.tooltips = """
<table style="width:100px">
  <tr>
    <td><strong>Time: </strong>@timestamp_h h</td>
  </tr>
  <tr>
    <td><strong>Votes: </strong>@vote</td>
  </tr>
</table>
"""
p_time.add_tools(hover_time)


# Create tabs.
tab1 = Panel(child=p_overall, title="Overall")
tab2 = Panel(child=p_generation, title="Generation")
tab3 = Panel(child=p_time, title="Votes in time")
tabs = Tabs(tabs=[tab1, tab2, tab3])



def update(attr, old, new):
    
    Pokemon = select.value
    
    # Get Pokemon of interest values.
    pokemon_number = df.index[df.loc[:, 'name'] == Pokemon].tolist()[0]
    pokemon_name = df.loc[pokemon_number, 'name']
    pokemon_generation = df.loc[pokemon_number, 'generation']
    pokemon_votes = df.loc[pokemon_number, 'votes']
    pokemon_ranking_overall = df.loc[pokemon_number, 'ranking_overall']
    pokemon_ranking_generation = df.loc[pokemon_number, 'ranking_generation']
    
    # Update Pokemon panel.
    sprite.text = """{}""".format(pokefunctions.get_sprite_html_text(pokemon_number, alt=pokemon_name, width=150))
    info.text="""
    <h3>{0}. {1}</h3>
    <table style="width:100%">
      <tr>
        <td><b>Generation:</b></td>
        <td>{2:.0f}</td>
      </tr>
      <tr>
        <td><b>Votes:</b></td>
        <td>{3:.0f}</td>
      </tr>
      <tr>
        <td><b>Overall ranking:</b></td>
        <td>{4:.0f}</td>
      </tr>
      <tr>
        <td><b>Generation ranking:</b></td>
        <td>{5:.0f}</td>
      </tr>
    </table>
    """.format(pokemon_number, pokemon_name, pokemon_generation, pokemon_votes, pokemon_ranking_overall, pokemon_ranking_generation)
    
    # Update overall.
    y_coord = len(df) - pokemon_ranking_overall + 0.5
    arrow_overall.x_start = pokemon_votes + max(df['votes'])*0.05
    arrow_overall.x_end = pokemon_votes
    arrow_overall.y_start = y_coord
    arrow_overall.y_end = y_coord
        
    # Update generation.
    df_generation_ = df_ranked.query('generation=="' + str(pokemon_generation) + '"')
    source_generation_ = ColumnDataSource(df_generation_[['name', 'votes', 'generation_color', 'ranking_generation', 'sprite_source']])
    pokemon_names_gen_ = source_generation_.data['name']
    pokemon_votes_gen_ = source_generation_.data['votes']

    p_generation.x_range.bounds = (0, max(pokemon_votes_gen_)*1.05)
    p_generation.x_range.update(start=0, end=max(pokemon_votes_gen_)*1.05)
    p_generation.y_range.bounds = (0, len(pokemon_names_gen_))
    p_generation.y_range.factors = list(pokemon_names_gen_)
    
    r_generation.data_source.data.update(source_generation_.data)

    y_coord = pokemon_names_gen_.tolist().index(pokemon_name) + 0.5
    arrow_generation.x_start = pokemon_votes + source_generation_.data['votes'].max()*0.05
    arrow_generation.x_end = pokemon_votes
    arrow_generation.y_start = y_coord
    arrow_generation.y_end = y_coord

    # Update votes in time.
    df_votes_ = df_votes.query('vote=="' + pokemon_name + '"')
    df_votes_ = df_votes_.groupby(pd.Grouper(key='timestamp', freq='1h')).count()
    df_votes_['timestamp'] = df_votes_.index
    df_votes_['timestamp_h'] = df_votes_[['timestamp']].timestamp.dt.strftime('%H:%M')
    df_votes_.index = np.arange(0, len(df_votes_))

    source_time_ = ColumnDataSource(df_votes_[['timestamp', 'timestamp_h', 'vote']])
    votes = source_time_.data['vote']
    color = pokefunctions.get_sprite_color(pokefunctions.get_sprite(pokemon_number))
    r_time.data_source.data.update(source_time_.data)
    r_time.glyph.fill_color = color


select.on_change('value', update) 
l = layout(row(column(sprite, info, select), tabs), sizing_mode='stretch_width')
curdoc().add_root(l)
