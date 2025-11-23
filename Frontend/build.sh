#!/bin/bash

echo "Installing dependencies..."
npm ci

echo "Building frontend..."
npm run build

echo "Build completed successfully!"