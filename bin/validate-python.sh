#!/bin/bash

echo "[i] ============================"
echo "[i] Starting pyright validation:"

pyright --project pyrightconfig.json 2>/dev/null

if [ $? -ne 0 ]; then
    echo "[!] Validation error with pyright. Cancel commit"
    exit 1
fi

echo "[i] Successfully completed pyright validation"
echo ""
echo "[i] ==========================="
echo "[i] Starting flake8 validation:"

flake8 2>/dev/null

if [ $? -ne 0 ]; then
    echo "[!] Validation error with flake8. Cancel commit"
    exit 1
fi

echo "[i] Successfully completed flake8 validation"
