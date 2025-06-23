# be/setup.py
from setuptools import setup, find_packages

setup(
  name='tgambler_common',
  version='0.1',
  packages=find_packages(include=['common', 'common.*']),
)
