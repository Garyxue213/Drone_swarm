#!/bin/bash
# Automatically change to the frontend dashboard directory
cd "$(dirname "$0")/dashboard"

# Install requirements and run
npm install
npm run dev
