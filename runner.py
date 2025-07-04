# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 21:20:16 2025

@author: BlankAdventure
"""
from nicegui import ui
from hogtown import app
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-db', default=None, help='URL to db. Defaults to memory is not specfified.')
parser.add_argument('-r','--route', help='Optional non-default route to host the site')
args = parser.parse_args()

# The idea below is that if a non-default route is provided, then the 
# the default route (/) will just redirect to github.
if args.route:
    print(f'setting new route: {args.route}')
    app.site_base = args.route
    
    @ui.page('/')
    def redir():
        ui.navigate.to('https://github.com/blankAdventure/')         
else:
    print('Using default route')

# if a db path is provided, use it. Otherwise run app with in-memory db.    
if args.db:
    print(f'Running with persisted db: {args.db}')
    app.run_app(args.db)
else:
    print('Running with memory db')
    app.run_app_memory()
    
ui.run(storage_secret='testtest', reload=False, port=5000)



