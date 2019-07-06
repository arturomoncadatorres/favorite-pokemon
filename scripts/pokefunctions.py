# -*- coding: utf-8 -*-
"""
pokefunctions.py
Group of functions to complement the analysis of favorite_pokemon.ipynb.

Created on Sat Jul  6 19:59:26 2019
@author: Arturo Moncada-Torres
arturomoncadatorres@gmail.com
"""


#%% Preliminaries
import requests
from PIL import Image
from io import BytesIO


#%%
def get_sprite(pokemon_number=7):
    """
    Fetch a Pokemon sprite.
    
    Parameters
    ----------
    pokemon_number: int
        Pokemon number (from the national Pokedex) to get sprite.
    
    Returns
    -------
    pokemon_image: PIL image
        Pokemon sprite.
        
    Notes
    ----------
    Sprites are obtained using PokeAPI (https://pokeapi.co/)
    """
    
    # Construct URL.
    pokemon_url = 'https://pokeapi.co/api/v2/pokemon/' + str(pokemon_number) + '/'
    
    # Make request. Proceed only if request was successful.
    pokemon_response = requests.get(pokemon_url)
    if (pokemon_response.status_code >= 200) & (pokemon_response.status_code <= 299):
        
        # Process JSON.
        pokemon_json = pokemon_response.json()
        pokemon_image_url = pokemon_json['sprites']['front_default']
        
        # Make image request.
        pokemon_image_response = requests.get(pokemon_image_url)
        if (pokemon_image_response.status_code >= 200) & (pokemon_image_response.status_code <= 299):
            pokemon_image = Image.open(BytesIO(pokemon_image_response.content))
            
        # If request wasn't successful, return None.
        else:
            pokemon_image = None            
            
    # If request wasn't successful, return None.
    else:
        pokemon_image = None
        
    return pokemon_image
