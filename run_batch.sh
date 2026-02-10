#!/bin/bash

set -u

LOG_FILE="batch_execution.log"
TOPICS=(
  "Epitalon (старение и теломеры)"
  "Urolithin A (митохондрии)"
  "Dasatinib+Quercetin (сенолитики)"
  "Semaglutide (нейропротекция 2025)"
  "Methylene Blue (память и энергия)"
  "GHK-Cu (регенерация)"
  "Fisetin (очистка клеток)"
  "Tesofensine (дофамин и вес)"
  "PE-22-28 (пептид-антидепрессант)"
  "Ca-AKG (эпигенетика)"
)

log_line() {
  local message="$1"
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$message" >> "$LOG_FILE"
}

for topic in "${TOPICS[@]}"; do
  log_line "START topic: ${topic}"
  if PYTHONUNBUFFERED=1 python3 research_auto_ai.py --topic "$topic" >> "$LOG_FILE" 2>&1; then
    log_line "SUCCESS topic: ${topic}"
  else
    log_line "ERROR topic: ${topic}"
  fi
  sleep 10
done

echo "Конвейер завершен. Проверь batch_execution.log"
