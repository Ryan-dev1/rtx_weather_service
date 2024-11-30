name: Run Script

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg espeak

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'  # Specify the Python version

      - name: Install Python packages
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run script
        run: python main.py

      - name: Upload log file
        uses: actions/upload-artifact@v3
        with:
          name: log-file
          path: log.txt
