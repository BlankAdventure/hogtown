# -*- coding: utf-8 -*-
"""
Created on Sat Jun 14 14:05:19 2025

@author: Patrick
"""

import pytest
from nicegui.testing import User
from main import run_app_memory
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

