#!/bin/bash
# PersonaSay Development Server Manager

PORT=8000
PID_FILE=".dev_server.pid"

start() {
    # Check if already running
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "[ERROR] Server already running (PID: $(cat $PID_FILE))"
        echo "        Run: ./dev.sh stop"
        exit 1
    fi
    
    # Check if port is in use
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "[ERROR] Port $PORT is already in use"
        echo "        Run: lsof -i :$PORT  # to see what's using it"
        echo "        Or:  lsof -ti :$PORT | xargs kill  # to kill it"
        exit 1
    fi
    
    echo "[INFO] Starting development server on port $PORT..."
    python3 app/server.py &
    echo $! > "$PID_FILE"
    echo "[SUCCESS] Server started (PID: $(cat $PID_FILE))"
    echo "          Logs: tail -f server.log"
    echo "          Stop: ./dev.sh stop"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            rm "$PID_FILE"
            echo "[SUCCESS] Server stopped"
        else
            rm "$PID_FILE"
            echo "[WARNING] PID file existed but process not found"
        fi
    else
        echo "[ERROR] No server running (no PID file found)"
        
        # Check if something is on the port anyway
        PORT_PID=$(lsof -ti :$PORT 2>/dev/null)
        if [ ! -z "$PORT_PID" ]; then
            echo "[WARNING] But port $PORT is in use by PID: $PORT_PID"
            echo "          Kill it with: kill $PORT_PID"
        fi
    fi
}

status() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "[RUNNING] Server is running (PID: $(cat $PID_FILE))"
    else
        echo "[STOPPED] Server is not running"
        [ -f "$PID_FILE" ] && rm "$PID_FILE"
    fi
    
    # Check what's on the port
    echo ""
    echo "Port $PORT status:"
    PORT_INFO=$(lsof -i :$PORT 2>/dev/null)
    if [ ! -z "$PORT_INFO" ]; then
        echo "$PORT_INFO"
    else
        echo "  Port is free"
    fi
}

restart() {
    echo "[INFO] Restarting server..."
    stop
    sleep 2
    start
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "PersonaSay Development Server Manager"
        echo ""
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the development server"
        echo "  stop    - Stop the development server"
        echo "  restart - Restart the development server"
        echo "  status  - Check if server is running"
        echo ""
        echo "Examples:"
        echo "  ./dev.sh start"
        echo "  ./dev.sh status"
        echo "  ./dev.sh stop"
        exit 1
        ;;
esac



