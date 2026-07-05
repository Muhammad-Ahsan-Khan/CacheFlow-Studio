# CacheFlow Studio

CacheFlow Studio is a redesigned COAL cache hit/miss simulator. It preserves the original FIFO and LRU logic while providing two interfaces:

- **MASM/Irvine32 console engine** for the assembly-language project requirement.
- **Professional web dashboard** for live visualization, evaluation, and report export.

## Main Features

- FIFO and LRU replacement policies
- 20-value main memory and five-line cache
- Live cache hit/miss classification
- Main-memory and cache visualization
- Hits, misses, total accesses, and hit-ratio metrics
- Live terminal output while the dashboard is running
- Optional random seed for repeatable demonstrations
- JSON report export
- Responsive white-and-blue branded UI
- No third-party Python dependencies

## Project Structure

```text
CacheFlow_Studio/
├── assembly/
│   ├── CacheFlowEngine.asm
│   └── modules/
│       ├── CacheFlowModel.inc
│       ├── CacheRuntime.inc
│       ├── CachePolicies.inc
│       └── ConsoleViews.inc
├── web/
│   ├── cacheflow_core.py
│   ├── console_runner.py
│   ├── dashboard_server.py
│   └── static/
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── tests/
├── docs/
├── start_dashboard.bat
├── start_dashboard.ps1
└── start_console.bat
```

## Run the Web Dashboard on Windows

### Easiest method

1. Install Python 3.10 or newer if it is not already installed.
2. Extract the project ZIP.
3. Double-click `start_dashboard.bat`.
4. The dashboard should open at `http://127.0.0.1:8080`.
5. Keep the terminal open. Every browser event is printed there too.

### Command-line method

```powershell
python web\dashboard_server.py --open
```

No `pip install` command is needed.

## Run the Python Console Version

```powershell
python web\console_runner.py --policy fifo --accesses 30 --seed 42
python web\console_runner.py --policy lru --accesses 30 --seed 42
```

## Build the MASM/Irvine32 Version

1. Open a configured Visual Studio/Irvine32 MASM project.
2. Copy the `assembly` folder into the project directory.
3. Add `CacheFlowEngine.asm` as the main source file.
4. Keep the `modules` folder beside it so the relative `INCLUDE` paths remain valid.
5. Build for **Win32/x86**, not x64.
6. Ensure the normal Irvine32 include and library paths are configured.

## Run Automated Tests

From the project root:

```powershell
python -m unittest discover -s tests -v
```

## Important Architecture Note

Web browsers cannot directly execute MASM code that depends on Irvine32. The MASM version remains the assembly implementation, while the local dashboard uses a Python engine with the same cache model and replacement rules. The server streams each step to the webpage and prints it to the terminal, providing the requested dual presentation.

See `docs/PHASE_REPORT.md` for the completed work and `docs/ALGORITHM_MAPPING.md` for logic mapping.
