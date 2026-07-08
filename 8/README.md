# Network Congestion Simulation System

**Department of Computer Science, Caleb University, Lagos**
**Final Year Project – 2025**

A Python-based discrete-event simulation system for analysing network congestion in Nigerian urban telecommunications networks. Models Poisson traffic generation, FIFO queuing, and multi-node network topologies, validated against M/M/1 queuing theory. Includes a full Flask web application for browser-based simulation control and result visualisation.

---

## Quick Start

### 1. Install Python
Make sure you have **Python 3.9 or newer** installed.
Check by running:
```
python --version
```

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Start the web application
```
python app.py
```
Then open your browser and go to:
```
http://localhost:5000
```

### 4. (Optional) Load demo data
To pre-fill the app with 5 ready-made simulation runs:
```
python seed_data.py
```

### 5. (Optional) Run from the command line instead
```
python main.py
```
This runs the full pipeline (validation + experiments) and saves plots to the `outputs/` folder.

---

## Project Structure

```
project/
│
├── app.py                  # Flask web application
├── main.py                 # Command-line entry point
│
├── packet.py               # Packet dataclass
├── fifo_queue.py           # Finite FIFO buffer
├── poisson_traffic.py      # Poisson packet generator
├── network_node.py         # Network node (buffer + server)
├── simulation_engine.py    # Simulation orchestrator
│
├── config.py               # All simulation parameters
├── validation.py           # M/M/1 theory validation
├── experiments.py          # Load-level experiment runner
├── visualisation.py        # Matplotlib chart generation
├── utils.py                # Logging and helper functions
│
├── templates/              # HTML pages (Flask/Jinja2)
│   ├── base.html           # Shared layout (navbar, footer)
│   ├── index.html          # Home page
│   ├── simulate.html       # Run simulation form
│   ├── results.html        # Results page with chart
│   ├── history.html        # All past runs
│   ├── admin.html          # Admin dashboard
│   └── about.html          # About / project info
│
├── static/
│   ├── css/style.css       # Custom stylesheet
│   └── js/main.js          # JavaScript (auto-poll)
│
├── outputs/                # Generated plots and CSV files
│   ├── performance_summary.png
│   ├── mm1_validation.png
│   ├── replication_distributions.png
│   ├── throughput_line.png
│   ├── results_raw.csv
│   └── results_summary.csv
│
├── instance/
│   └── simulation_results.db   # SQLite database (auto-created)
│
├── seed_data.py            # Loads demo simulation runs into DB
├── generate_chapters.py    # Generates Chapters 4 and 5 Word doc
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Web Application Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Overview, stats, recent runs |
| Run Simulation | `/simulate` | Configure and launch a simulation |
| Results | `/results/<id>` | View chart and table for a run |
| History | `/history` | All past simulation runs |
| Admin | `/admin` | Manage runs, view system stats |
| About | `/about` | Project info and architecture |

---

## Command-Line Options

```
python main.py                    # Full pipeline (validation + experiments)
python main.py --validate-only    # M/M/1 validation only
python main.py --experiment-only  # Skip validation, run experiments only
python main.py --debug            # Verbose logging
python main.py --seed 123         # Custom random seed
python main.py --output-dir out   # Custom output folder
```

---

## Simulation Parameters (config.py)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `arrival_rate` | 0.8 pkt/s | Packet arrival rate λ |
| `service_rate` | 1.0 pkt/s | Node service rate μ |
| `num_nodes` | 3 | Nodes in the network chain |
| `buffer_size` | 50 packets | Max queue depth per node |
| `duration` | 500 s | Simulated time per replication |
| `num_replications` | 5 | Independent runs per load level |
| `load_levels` | 0.5, 0.8, 1.0, 1.2 | Traffic load multipliers |

---

## M/M/1 Validation

With λ = 0.8 and μ = 1.0:

| Metric | Theory | Simulation | Error |
|--------|--------|------------|-------|
| Mean sojourn E[T] | 5.0000 s | 4.5061 s | 9.88% ✓ |
| Server utilisation ρ | 0.8000 | 0.7990 | 0.13% ✓ |

Error threshold: < 10% — **PASSED**

---

## Experiment Results Summary

| Load | Avg Delay | Loss Ratio | Throughput | Queue Length |
|------|-----------|------------|------------|--------------|
| 50% | 1.67 s | 0.00% | 0.48 pkt/s | 0.93 pkts |
| 80% | 3.66 s | 0.00% | 0.74 pkt/s | 2.56 pkts |
| 100% | 6.57 s | 0.16% | 0.88 pkt/s | 7.72 pkts |
| 120% | 8.24 s | 5.09% | 0.94 pkt/s | 16.12 pkts |

---

## Dependencies

```
simpy==4.1.1        # Discrete-event simulation
numpy==1.26.4       # Numerical computation
pandas==2.2.2       # Data manipulation
matplotlib==3.9.0   # Chart generation
scipy==1.13.1       # Confidence intervals
flask               # Web framework
flask-sqlalchemy    # Database ORM
```

Install all with:
```
pip install -r requirements.txt
```

---

## How to Take Screenshots (for your report)

1. Run `python app.py`
2. Open `http://localhost:5000` in your browser
3. For each page below, press:
   - **Windows**: `Windows key + Shift + S` → drag to select area → paste into Word
   - **Mac**: `Cmd + Shift + 4` → drag to select area
4. Pages to screenshot:

| Figure | URL |
|--------|-----|
| Figure 4.2 – Home Page | `localhost:5000` |
| Figure 4.3 – Simulate Page | `localhost:5000/simulate` |
| Figure 4.4 – Results Page | `localhost:5000/results/1` |
| Figure 4.5 – History Page | `localhost:5000/history` |
| Figure 4.6 – Admin Page | `localhost:5000/admin` |

The two remaining figures (`performance_summary.png` and `mm1_validation.png`) are already saved in the `outputs/` folder — insert them directly into Word.
