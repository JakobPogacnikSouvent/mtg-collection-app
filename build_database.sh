#! /bin/bash

# TODO: remove old file
wget https://archive.scryfall.com/json/scryfall-default-cards.json
python3 minimalDb.py
#TODO: rename created db