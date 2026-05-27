#!/bin/bash
source "$(dirname "$0")/../config/setup.sh"

# execute tests
python3 -m unittest discover -s tests -p 'test_*.py'
