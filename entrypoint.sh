#!/bin/bash

echo "Available Python scripts in /app/src:"
scripts=($(ls /app/src/*.py 2>/dev/null))

if [ ${#scripts[@]} -eq 0 ]; then
  echo "No Python scripts found in /app/src"
  exit 1
fi

filenames=()
for path in "${scripts[@]}"; do
  filenames+=("$(basename "$path")")
done

PS3="Choose a script to run: "
while true; do
  select script in "${filenames[@]}"; do
    if [[ -n "$script" ]]; then
      echo "Running $script..."
      exec python "/app/src/$script"
    else
      echo "Invalid selection. Please choose a valid number."
      break
    fi
  done
done
