#!/bin/bash
PORT=8000
SEARCH_PROCESS="uvicorn"

# Returns the PID of a process listening on a specific port
get_port_in_use() {
    local port="$1"

    if [ "$port" == "NONE" ]; then
        echo ""
        return 0
    fi

    lsof -i :${port} | grep LISTEN|grep IPv4| awk '{print $2}' | xargs
}

stop() {
	if [ -n "${PROCESS_ID}" ]; then
      echo "Stopping ${PROCESS_NAME} with PID:[${PROCESS_ID}]"
		safe_kill ${PROCESS_ID}
		safe_kill ${PORT_IN_USE}
	else
       echo "${PROCESS_NAME} is not running."
	    if [ -n "${PORT_IN_USE}" ]; then
   	    echo "However ${PROCESS_NAME} port is blocked. Stopping blocking process PID:[${PORT_IN_USE}]"
			 safe_kill ${PORT_IN_USE}
       fi
	fi

}

PORT_IN_USE=$(get_port_in_use "$PORT")
PROCESS_ID=$(get_process_id "$SEARCH_PROCESS")
stop
sleep 2

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000