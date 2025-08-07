#!/bin/bash
DB_URL="postgresql://app_user:user_passw0rd@localhost/poster_judging"
OUTPUT_DIR="./app"
clear
PYTHONPATH=./src python -m pg_scaffold --pgdb ${DB_URL} --output ${OUTPUT_DIR}
