# python-data

A containerized Python environment for processing files with pandas.

## Project Structure

```
python-data
├── .devcontainer/
│   ├── devcontainer.json            # VS Code dev container configuration
│   └── Dockerfile                   # Dockerfile for the dev container (matches app Dockerfile)
├── .vscode/
│   ├── extensions.json              # Recommended VS Code extensions
│   └── settings.json                # Workspace-specific settings
├── data/                            # Data input/output files are stored here. .gitignored.
├── src/
│   └── combine_workbook_sheets.py   # Combine sheets within an Excel workbook based on `key` column.
│   └── drop_incomplete.py           # Simple script to remove incomplete rows.
│   └── web_inventory_cleanup.py     # Multi-step cleanup: Removes duplicates, assets, matched redirects, deep subdirectory paths.
│                                      Groups by status code and tagging based on identified patterns.
│                                      Attempts to reduce multiple rows per canonical instance.
├── .gitignore                       # Ignore directories and files from being included in a Git repository.
├── Dockerfile                       # Dockerfile for building the application image
├── entrypoint.sh                    # Terminal prompt script.
├── README.md                        # Project documentation
└── requirements.txt                 # Python dependencies
```

## Prerequisites

- [Colima](https://github.com/abiosoft/colima) installed and running (as a Docker backend for macOS)
- [Docker CLI](https://docs.docker.com/get-docker/) installed
- [Visual Studio Code](https://code.visualstudio.com/) with the recommended workplace extensions

## Setup Instructions

1. **Clone the Repository**  
   Clone this repository to your local machine:

   ```
   git clone <repository-url>
   cd python-data
   ```

2. **Start Colima**  
   Make sure Colima is running before building or running containers:

   ```
   colima start
   ```

3. **Build the Docker Image**  
   Build the Docker image for the application:

   ```
   docker build -t python-data .
   ```

4. **Run the Docker Container**  
   To process CSV files and persist output to your local `data` directory, run:

   ```
   docker run -it --rm -v "$(pwd)/data":/app/data python-data
   ```

   > This mounts your local `data` folder into the container at `/app/data`.

5. **(Optional) Use the Dev Container in VS Code**

   - Open this folder in VS Code.
   - When prompted, "Reopen in Container" to develop inside the dev container.
   - The dev container matches your runtime environment and mounts the `data` folder for persistence.

6. **(Optional) Shut Down Colima**  
   If you want to stop all containers and free up system resources:
   ```
   colima stop
   ```

## Notes

- The `data` directory is mounted into the container for input/output file persistence.
- The dev container setup ensures your development environment matches your production container.
- All dependencies are managed via `requirements.txt`.

---
