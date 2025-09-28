#!/bin/bash

ensure_conda_env() {
    local target_env="$1"

    if [ -z "$target_env" ]; then
        echo "Usage: ensure_conda_env <env_name>"
        return 1
    fi

    if ! command -v conda &> /dev/null; then
        echo "conda is not installed or not in PATH"
        return 1
    fi

    # Load conda functions for activation
    source "$(conda info --base)/etc/profile.d/conda.sh"

    local active_env
    active_env=$(basename "$CONDA_PREFIX")

    if [ "$active_env" != "$target_env" ]; then
        echo "You are not in the '$target_env' environment. Activating it now..."
        conda activate "$target_env"
    else
        echo "You are already in the '$target_env' environment."
    fi
}

ensure_conda_env wormcat3-web
sleep 1

DB_URL="postgresql://app_user:user_passw0rd@localhost/evalia_db"
OUTPUT_DIR="./generated"
clear
PYTHONPATH=./src python -m pg_scaffold --pgdb ${DB_URL} --output ${OUTPUT_DIR}
