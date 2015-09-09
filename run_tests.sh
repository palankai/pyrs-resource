#!/bin/bash

set -e

if [ "$1" = "" ]; then
    python -m unittest discover .

    ./test_set_trace.sh

    flake8 pyrs
else
    python -m unittest $@
fi
