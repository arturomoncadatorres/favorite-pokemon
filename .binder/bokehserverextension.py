# -*- coding: utf-8 -*-
"""
bokehserverextension.py
File needed to serve Bokeh app through a Binder server. See
https://github.com/binder-examples/bokeh

Created on Tue Aug 20 23:50:56 2019
@author: Arturo Moncada-Torres
arturomoncadatorres@gmail.com
"""

from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    """serve the bokeh-app directory with bokeh server"""
    Popen(["bokeh", "serve", "bokeh-app", "--allow-websocket-origin=*"])