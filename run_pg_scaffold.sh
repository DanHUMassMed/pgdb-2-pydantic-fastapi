#!/bin/bash
DB_URL="postgresql://app_user:user_passw0rd@localhost/poster_judging_db"
OUTPUT_DIR="./generated"
clear
PYTHONPATH=./src python -m pg_scaffold --pgdb ${DB_URL} --output ${OUTPUT_DIR}
