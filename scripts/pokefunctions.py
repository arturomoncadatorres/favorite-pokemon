# -*- coding: utf-8 -*-
"""
pokefunctions.py
Functions to complement the analysis of the favorite_pokemon repository.

Created on Sat Jul  6 19:59:26 2019
@author: Arturo Moncada-Torres
arturomoncadatorres@gmail.com
"""


#%% Preliminaries
import requests
from PIL import Image
from io import BytesIO


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