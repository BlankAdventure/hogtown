# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 14:05:19 2025

@author: Patrick
"""
import asyncio
import pytest
from nicegui.testing import User
from ..hogtown.app import run_app_memory

pytest_plugins = ['nicegui.testing.user_plugin']


@pytest.fixture
def user(user: User) -> User:
    run_app_memory()
    return user

async def test_click(user: User) -> None:
    await user.open('/')
    await user.should_see('About Hashing')

async def test_login(user: User) -> None:
    await user.open('/')
    await user.should_see('Login')
    user.find('Login').click()
    await user.should_see('Login')
    await user.should_see('Username')
    await user.should_see('Password')
    user.find('Username').type('admin')
    user.find('Password').type('12345')
    user.find('Login').click()
    await asyncio.sleep(2) #take a bit of time 
    await user.should_see('New Event')
    