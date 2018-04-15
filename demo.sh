#!/bin/bash
printf "\nDo you have coordinates and want to see how predictor works?\nIf so, type 'predictor'.\nDo you want try image labeling tool?\nIf so, type 'ilt'\n"

read ans

if [[ "$ans" == "predictor" ]]; then
        python3 main.py
elif [[ "$ans" == "ilt" ]]; then
        python3 labeling_tool.py
else
        echo "Invalid input."
fi
