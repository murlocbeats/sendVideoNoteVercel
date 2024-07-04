#!/bin/bash

# Update package lists
apt-get update

# Install ffmpeg
apt-get install -y ffmpeg

# Verify installation
ffmpeg -version
