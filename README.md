# AI Phishing Detection Engine (Backend Solution)

This directory contains the Dockerized Python Flask API for the AI Phishing Detection Engine. The solution implements a 3-class Random Forest Classifier for immediate domain classification and a Suspected Domain Monitoring component.

## Environment Required to Run Model

The only prerequisite environment needed is **Docker**.

## Instructions for Executing the Solution

Follow these steps to set up, run, and test the solution:

### 1. Pre-requisite: Model Generation
Before building the Docker image, ensure the model artifact exists. This is done by running the provided script, which generates the model and saves it to `model/final_phishing_model_pipeline.joblib`.

```bash
# This command must be run once to ensure the model file exists
python generate_model.py