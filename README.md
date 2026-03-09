## Project Title
Sparse Identification of Nonlinear Vehicle Dynamics via SINDy with Physics-Informed Priors

## Overview
This project focuses on extracting physically meaningful governing differential equations from noisy racing telemetry data (MoTeC) using the SINDy (Sparse Identification of Nonlinear Dynamics) algorithm. The ultimate goal is to establish a Physics-Informed ML framework that bridges the gap between high-fidelity data-driven discovery and the rigorous interpretability of classical physics.

## Methodology:
Data Cleaning: A Savitzky-Golay (SG) filter is employed to suppress measurement noise while preserving high-frequency transient dynamics, ensuring robust numerical differentiation.

Interpretability & Validation: The sparse structures discovered by SINDy are cross-validated against theoretical vehicle models. This process ensures physical consistency and enhances the model's interpretability and generalization performance.


## Installation & Usage:
### Prerequisites
- Python 3.8+
- Dependencies: `pip install pandas numpy scipy pysindy matplotlib`

### Execution
1. Place raw MoTeC CSV files in the `./data` folder.
2. Run the automated pipeline:
**Option A: Auto-detect (Default)**
Simply run the main script. The program will automatically locate and process the **most recently added** `.csv` file in the `./data` directory. This is ideal for rapid iterative testing.
```bash
python main.py
```
**Option B: Specify a target file**
For reproducible experiments or analyzing specific track sessions, pass the relative path of the data file as an argument:
```bash
python main.py data/red_bull_ring-porsche_718_cayman_gt4.csv
```

## Results:
Currently unavailable

## Project Structure:
├── data/               # Raw MoTeC telemetry (.csv)
├── processed_data/     # Cleaned data after SG filtering
├── src/                
│   ├── process_data.py # Data parsing, unit conversion & SG filter
│   └── run_sindy.py    # SINDy model fitting & library setup
├── main.py             
└── notebooks/          # Exploratory analysis & visualization


## Acknowledgment: 
Algorithm: Powered by the PySINDy library (Brunton et al.).

AI Disclosure: AI-assisted coding tools were used for workflow scaffolding and refactoring. All core physical logic, coordinate transformations, and derivative auditing were performed independently by the author.

## Updates: 
* **[2026-03-08] v0.1.0 - Framework Initialization & Physics-Informed Tuning**
Established the initial data pipeline and SINDy pipeline. The model fidelity (R² score) was systematically improved through the following experimental iterations:

* **R² = 0.0976 (Baseline)**: Initialized the framework and ran vanilla SINDy directly on raw telemetry data.
* **R² = 0.1349 (Physics-Informed I/O)**: Manually decoupled independent variables (control inputs: Steering, Throttle, Brake) and dependent variables (states: G-forces, Speed, Yaw) based on vehicle dynamics principles.
* **R² = 0.2560 (Signal Processing)**: Integrated a Savitzky-Golay (SG) filter to suppress high-frequency sensor noise while preserving the transient peaks crucial for derivative calculations.
* **R² = 0.2953 (Addressing Coefficient Scaling)**: Identified a critical algorithmic bottleneck: large magnitudes of high-speed $V^2$ terms resulted in extremely small coefficients, which were prematurely zeroed out by the STLSQ threshold. Introduced specific aerodynamic scaling/priors to force the retention of drag-related terms.
* **R² = 0.4334 (Experimental Control & Clean Data)**: 
    * *Observation*: The initial dataset (GT3 at Nürburgring GP, 50-min race) contained too many unobserved latent variables (fuel weight reduction, tire thermal degradation, track bumpiness, and dirty air from dogfights).
    * *Action*: Switched the baseline dataset to a controlled environment (Porsche 718 GT4 Clubsport at Red Bull Ring, continuous practice laps with heavy fuel and stable conditions). 
    * *Result*: Stripping away complex aero and degradation noise allowed the model to successfully capture the core mechanical dynamics.

## Future Work:
The current R² = 0.4334 proves the viability of SINDy on clean mechanical grip regimes. The next phases will focus on subsystem decoupling and progressive complexity:

1.  **Phase 1: Mechanical Grip Optimization (Current Focus)**
    * Utilize lower-aero vehicles (e.g., GT4 or BMW M2 CS) to isolate and maximize the fitting accuracy of pure mechanical dynamics (tire slip, load transfer).
2.  **Phase 2: Sub-system Decoupling**
    * Stop fitting the entire vehicle state simultaneously. Instead, decouple the model into **Longitudinal Dynamics** (Throttle/Brake vs. G_LON) and **Lateral Dynamics** (Steering vs. G_LAT & Yaw Rate) to refine the sparse libraries independently.
3.  **Phase 3: High-Downforce & Complex Aero Integration**
    * Once the decoupled mechanical baseline achieves a high R², re-introduce GT3 data. 
    * Formulate specific physics-constrained equations to account for complex aerodynamic phenomena (e.g., pitch-dependent downforce shifts).
