# -*- coding: utf-8 -*-
"""
pokefunctions.py
Functions to complement the analysis of the favorite_pokemon repository.

Created on Sat Jul  6 19:59:26 2019
@author: Arturo Moncada-Torres
arturomoncadatorres@gmail.com
"""


#%% Preliminaries
import pandas as pd
import numpy as np
import requests
from PIL import Image
from io import BytesIO


#%%
def generation_palette():
    """
    Get color palette for Pokemon generations.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dictionary
        Keys are ints corresponding to the generation.
        Values are strings with hexadecimal color code.
        
    Notes
    -----
    Colors were obtain from Bulbapedia
    https://bulbapedia.bulbagarden.net/wiki/Generation
    """
    return {1:'#ACD36C',
            2:'#DCD677',
            3:'#9CD7C8', 
            4:'#B7A3C3', 
            5:'#9FCADF', 
            6:'#DD608C', 
            7:'#E89483'}


#%%
def type_palette():
    """
    Get color palette for Pokemon types.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dictionary
        Keys are strings corresponding to the type.
        Values are strings with hexadecimal color code.
        
    Notes
    -----
    Colors were obtain from Bulbapedia
    https://bulbapedia.bulbagarden.net/wiki/Type
    """
    return {'normal':'#A8A878',
            'fire':'#F08030',
            'fighting':'#C03028',
            'water':'#6890F0',
            'flying':'#A890F0',
            'grass':'#78C850',
            'poison':'#A040A0',
            'electric':'#F8D030',
            'ground':'#E0C068',
            'psychic':'#F85888',
            'rock':'#B8A038',
            'ice':'#98D8D8',
            'bug':'#A8B820',
            'dragon':'#7038F8',
            'ghost':'#705898',
            'dark':'#705848',
            'steel':'#B8B8D0',
            'fairy':'#EE99AC'}
            
       
#%%
def read_raw_data(path_data_file):
    """
    Read raw data file.
    
    Parameters
    ----------
    path_data_file: string or pathlib.Path
        Path to the Excel file with the results.
    
    Returns
    -------
    df_raw: pandas DataFrame
        DataFrame with favorite Pokemon survey results. It has columns:
            name        Pokemon name
            votes       Number of votes the Pokemon received
            types       Pokemon types
            generation  Generation
            family      Pokemon's family (first evolution)
        
    Notes
    -----
    Data was collected by mamamia1001 in the reddit survey
    "Testing the "Every Pokemon is someone's favorite hypothesis"
    https://www.reddit.com/r/pokemon/comments/c04rvq/survey_testing_the_every_pok%C3%A9mon_is_someones/
    """
    
    # Read data.
    df_raw = pd.read_excel(path_data_file, sheet_name='Results', usecols='A:E')
    
    # Rename columns.
    df_raw.rename(columns={'Results in full':'name', 'Unnamed: 1':'votes', 'Unnamed: 2':'types', 'Unnamed: 3':'generation', 'Unnamed: 4':'family'}, inplace=True)

    # Shift the index by 1, so that it matches the Pokemon number.
    df_raw.index = df_raw.index + 1
    
    # Remove any potential NaN.
    df_raw.dropna(inplace=True)
    
    # Make sure generation is int.
    df_raw['generation'] = df_raw['generation'].astype(int)

    return df_raw


#%%
def rank_raw_data(df):
    """
    Rank a raw data Data Frame and add relevant columns.
    
    Parameters
    ----------
    df: pandas DataFrame
    
    Returns
    -------
    df_ranked: pandas DataFrame
        Ranked DataFrame. Least popular Pokemon are on the top, most popular
        on the bottom. Furthermore, the following columns are added to the
        original one:
            ranking_overall     Overall ranking of the Pokemon
            ranking_generation  Ranking of the Pokemon in its generation
    """
    
    # Sort by popularity.
    df_ranked = df.sort_values('votes', ascending=True)
    
    # Add general ranking.
    df_ranked['ranking_overall'] = np.arange(1, len(df_ranked) + 1)[::-1]
    
    # Add generation ranking.
    df_ranked['ranking_generation'] = df_ranked.groupby('generation')['votes'].rank(method='first', ascending=False)

    return df_ranked


#%%
def read_votes(path_data_file):
    """
    Read data file with the survey's votes.
    
    Parameters
    ----------
    path_data_file: string or pathlib.Path
        Path to the Excel file with the votes.
    
    Returns
    -------
    df_raw: pandas DataFrame
        DataFrame with favorite Pokemon survey votes. It has columns:
            timestamp   Time when the vote was casted
            vote        Name of the Pokemon that was voted
        
    Notes
    -----
    Data was collected by mamamia1001 in the reddit survey
    "Testing the "Every Pokemon is someone's favorite hypothesis"
    https://www.reddit.com/r/pokemon/comments/c04rvq/survey_testing_the_every_pok%C3%A9mon_is_someones/
    """
    
    # Read data.
    df_votes = pd.read_excel(path_data_file, sheet_name='Form Responses 1')
    
    # Rename columns.
    df_votes.rename(columns={'Timestamp':'timestamp', 'What is your favourite Pokémon?':'vote'}, inplace=True)

    # Remove any potential NaN.
    df_votes.dropna(inplace=True)
    
    return df_votes


#%%
def process_pokemon_votes(df_votes, pokemon_name):
    """
    Processon a votes DataFrame for a specific Pokemon.
    
    Parameters
    ----------
    df: pandas DataFrame
        Original votes DataFrame (obtained using read_votes)
        
    pokemon_name: string
        Pokemon name of interest
    
    Returns
    -------
    df_votes_pokemon: pandas DataFrame
        DataFrame with Pokemon of interest votes in time.
    """
    
    df_votes_pokemon = df_votes.query('vote=="' + pokemon_name + '"')
    df_votes_pokemon = df_votes_pokemon.groupby(pd.Grouper(key='timestamp', freq='1h')).count()
    df_votes_pokemon['timestamp'] = df_votes_pokemon.index
    df_votes_pokemon['timestamp_h'] = df_votes_pokemon[['timestamp']].timestamp.dt.strftime('%H:%M')
    df_votes_pokemon.index = np.arange(0, len(df_votes_pokemon))
    
    return df_votes_pokemon


#%%            
def get_pokeball_location():
    """
    Get the location of the pokeball image. This one is used as a sprite
    when the actual Pokemon sprite is not found.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    string
        Path to the pokeball image.
        Do NOT use a pathlib.Path, since it isn't JSON serializable.
    """
    return '../images/pokeball.png'


#%%
def get_sprite_url(pokemon_number):
    """
    Get a Pokemon URL pointing to its sprite.
    
    Parameters
    ----------
    pokemon_number: int
        Pokemon number (from the national Pokedex) to get sprite HTML text.
    
    Returns
    -------
    sprite_url: string
        URL pointing to the Pokemon sprite. If request is unsuccessful, 
        it returns path pointing to pokeball image in local directory.
        For example:
        
        Successful call:
        https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png
        
        Unsuccessful call:
        ../images/pokeball.png
        
    Notes
    -----
    Sprites are obtained using PokeAPI (https://pokeapi.co/)
    """
    # Construct URL.
    pokemon_url = 'https://pokeapi.co/api/v2/pokemon/' + str(pokemon_number) + '/'
    
    # Make request. Proceed only if request was successful.
    pokemon_response = requests.get(pokemon_url)
    if (pokemon_response.status_code >= 200) & (pokemon_response.status_code <= 299):
        
        pokemon_json = pokemon_response.json()
        try:
            # Try to make image request.
            sprite_url = pokemon_json['sprites']['front_default']
            sprite_response = requests.get(sprite_url)
        except:
            # If extracting URL from JSON doesn't work, create a synthetic
            # response with a fault status code.
            sprite_response = requests.Response
            sprite_response.status_code = 0
        
        # If request was successful, do nothing. sprite_url is fine.
        if (sprite_response.status_code >= 200) & (sprite_response.status_code <= 299):
            pass
            
        # If request wasn't successful, return text pointing to local pokeball.
        else:
            sprite_url = get_pokeball_location()
            
 
    # If request wasn't successful, return text pointing to local pokeball.
    else:
        sprite_url = get_pokeball_location()
        
        
    return sprite_url


#%%
def get_sprite(pokemon_number):
    """
    Get a Pokemon sprite.
    
    Parameters
    ----------
    pokemon_number: int
        Pokemon number (from the national Pokedex) to get sprite.
    
    Returns
    -------
    sprite: PIL image
        Pokemon sprite. If request was unsuccesful, returned sprite
        corresponds to pokeball image (see get_pokeball_location).
        
    Notes
    -----
    Sprites are obtained using PokeAPI (https://pokeapi.co/)
    """

    # Try image request.
    try:
        sprite_response = requests.get(get_sprite_url(pokemon_number))
        # If request is successful, return sprite.
        if (sprite_response.status_code >= 200) & (sprite_response.status_code <= 299):
            sprite = Image.open(BytesIO(sprite_response.content))
            
        # If request wasn't successful, return pokeball.
        else:
            sprite = Image.open(get_pokeball_location())            

    # If there was an error when making request, return pokeball.        
    except:
        sprite = Image.open(get_pokeball_location()) 
        
    return sprite


#%%
def get_sprite_color(sprite):
    """
    Get the most regular color of a Pokemon sprite.
    
    Parameters
    ----------
    sprite: PIL image
        Pokemon sprite (read from a png image).
    
    Returns
    -------
    color_hex: string
        String with the hexadecimal representation of the most common
        color of the Pokemon sprite.
    """

    # Make sure input sprite has P mode (8-bit pixels)
    # See https://pillow.readthedocs.io/en/5.1.x/handbook/concepts.html#modes
    if sprite.mode != 'P':
        sprite = sprite.convert('P')
        
    # Convert to RGB.
    sprite_rgb = sprite.convert('RGB')
    
    # Get the sprite's color composition.
    colors = sorted(sprite_rgb.getcolors())
    
    # Get the most common color.
    color = colors[-1][1]
    
    # If the most common color is black (probably background),
    # chose the second most common color.
    if color == (0, 0, 0):
        color = colors[-2][1]
    
    # Convert to hex.
    color_hex = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

    return color_hex


#%%
def get_sprite_html_text(pokemon_number, alt='', width=100):
    """
    Get a Pokemon HTML text pointing to its sprite (to be used in the
    favorite_pokemon_ui).
    
    Parameters
    ----------
    pokemon_number: int
        Pokemon number (from the national Pokedex) to get sprite HTML text.
        
    alt: string (optional)
        Alternate text for the image.
        
    width: int (optional) [pixels]
        Sprite width in pixels. Default value is 100.
    
    Returns
    -------
    sprite_html_text: string
        HTML text pointing to its sprite. If request is unsuccessful, 
        it returns text pointing to pokeball image (see
        get_pokeball_location). For example:
        
        Successful call:
        <img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/7.png" alt="" width=100px>
        
        Unsuccessful call:
        <img src="../images/pokeball.png" alt="pokeball" width=100px>
        
    Notes
    -----
    Sprites are obtained using PokeAPI (https://pokeapi.co/)
    """
    
    # Get sprite URL.
    sprite_url = get_sprite_url(pokemon_number)

    # Modify alt text if needed.
    if 'pokeball' in str(sprite_url):
        alt = 'pokeball'

    sprite_html_text = '<img src="{0}" alt="{1}" width={2}px>'.format(sprite_url, alt, width)
        
    return sprite_html_text
