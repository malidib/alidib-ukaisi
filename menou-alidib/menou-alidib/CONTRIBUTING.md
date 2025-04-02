# Contributing Guide

This document contain notes and instructions for anyone maintaining or developing the evaluation.

## Maintenance Details

The eval does not rely on external data sources in order to run, but you might want to replace the dummy datasets with your own real world data.
Maintenance level should be low due to no dependencies on external packages that might break compatibility in the future.
The utils are in their own file, and so are the prompts, making maintenance easier.
The only thing to keep in mind is running create_dataset.py when you modify phase_1.py.

## Testing Details

The eval has no external package dependencies. The only environment variables that need to be set are LLMs API keys. 
The 2 modules (phase_1 and phase_2) can be tested separately or together on the included dummy data using :
python create_dataset.py   #(optional if phase_1 is unmodified)
inspect eval ./phase_1.py  --model openai/o3-mini
inspect eval ./phase_2.py  --model openai/o3-mini   # this will run both phase_1 and phase_2

## Developer Contact Details

Mohamad Ali-Dib
malidib@nyu.edu
mmalidib@gmail.com
