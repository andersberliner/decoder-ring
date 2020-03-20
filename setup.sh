#!/bin/bash

# Globally install virtualenv
pip install virtualenv

# Create the virtual environment
virtualenv decoder

# Install the requirements
source decoder/bin/activate
pip install -r requirements.txt
