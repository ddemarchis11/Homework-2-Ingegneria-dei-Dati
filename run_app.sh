#!/usr/bin/env bash
set -euo pipefail

APP_FILE="user_interface.py"
ELASTIC_DIR="./elastic-start-local"
START_SCRIPT="$ELASTIC_DIR/start.sh"
STOP_SCRIPT="$ELASTIC_DIR/stop.sh"
INDEX_SCRIPT="indexer.py"
ES_URL="${ES_URL:-http://localhost:9200}"

STREAMLIT_PID=""

function check_docker {
  if ! docker info >/dev/null 2>&1; then
    echo "Docker not executing, running..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
      open --background -a Docker
      echo "Waiting for Docker to be ready.."
      until docker info >/dev/null 2>&1; do
        sleep 2
      done
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
      sudo systemctl start docker
      echo "Waiting Docker to be ready.."
      until docker info >/dev/null 2>&1; do
        sleep 2
      done
    else
      echo "Sistema not recognized, open Docker manually."
      exit 1
    fi
  fi
  echo "Docker is running."
}

function start_elastic {
  echo "Executing Elasticsearch: $START_SCRIPT ..."
  bash "$START_SCRIPT"
}

function stop_elastic {
  echo "Stopping Elasticsearch..."
  bash "$STOP_SCRIPT" || true
}

function wait_for_elastic {
  echo "Waiting for ElasticSearch to be ready on $ES_URL ..."
  until curl -s "$ES_URL/_cluster/health?wait_for_status=yellow&timeout=30s" | grep -q '"status"'; do
    sleep 2
  done
  echo "Elasticsearch ready."
}

function build_index {
  echo "Executing indexing with $INDEX_SCRIPT ..."
  ES_URL="$ES_URL" python3 "$INDEX_SCRIPT"
  echo "Indexing completed."
}

function stop_docker_daemon {
  echo "Closing Docker..."
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    sudo systemctl stop docker || true
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    osascript -e 'quit app "Docker"' || true
  fi
  echo "Docker closed (or closing)."
}

function cleanup {
  echo
  echo "Stop triggered, executing cleanup..."
  if [[ -n "${STREAMLIT_PID:-}" ]] && ps -p "$STREAMLIT_PID" >/dev/null 2>&1; then
    echo "Ending Streamlit (PID $STREAMLIT_PID)..."
    kill "$STREAMLIT_PID" 2>/dev/null || true
    sleep 1
  fi

  stop_elastic
  stop_docker_daemon
  echo "Cleanup completed!"
}


trap cleanup INT TERM EXIT

check_docker
start_elastic
wait_for_elastic
build_index
echo "Waiting for Streamlit UI..."
streamlit run "$APP_FILE" &
STREAMLIT_PID=$!

wait "$STREAMLIT_PID"