#!/bin/bash
DEV_APP_DIR=~/Code/Vibe_Coding/judging-app/backend
cp -f generated/app/schemas/*.py ${DEV_APP_DIR}/app/schemas/
cp -f generated/app/models/*.py ${DEV_APP_DIR}/app/models/
