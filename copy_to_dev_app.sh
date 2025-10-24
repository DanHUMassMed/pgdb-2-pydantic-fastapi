#!/bin/bash
DEV_APP_BACKEND_DIR=~/Code/Vibe_Coding/evaliaplatform/backend
cp -f generated/app/schemas/*.py ${DEV_APP_BACKEND_DIR}/app/schemas/
cp -f generated/app/models/*.py ${DEV_APP_BACKEND_DIR}/app/models/
cp -f generated/app/crud/*.py ${DEV_APP_BACKEND_DIR}/app/crud/

DEV_APP_FRONTEND_DIR=~/Code/Vibe_Coding/evaliaplatform/frontend/app/src
cp -f generated/types/*.ts ${DEV_APP_FRONTEND_DIR}/types/

