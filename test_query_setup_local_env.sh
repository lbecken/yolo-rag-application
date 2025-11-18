#!/bin/bash

# create new virtual environment - mini conda
conda create -n yolo_rag_app python=3.11

# activate new env
conda activate yolo_rag_app

* install dependencies
pip install -r python-service/requirements.txt
