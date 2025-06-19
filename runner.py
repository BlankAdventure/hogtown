# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 21:20:16 2025

@author: BlankAdventure
"""
from nicegui import ui
from hogtown import app

app.site_base = '/h3'
app.run_app_memory()
ui.run(storage_secret='testtest')