# MediAlloc 🏥

A smart hospital bed allocation system built with Python and Streamlit, using the **Fractional Knapsack Algorithm** to optimally assign bed-days to patients based on medical severity and treatment duration.

---

## What It Does

Given a set of patients with varying conditions and a fixed hospital bed capacity, MediAlloc determines who gets admitted — prioritising patients who yield the highest medical benefit per bed-day used.

---

## Features

| Feature | Description |
|---|---|
| Patient Queue | Add patients manually, randomly, or from a built-in sample dataset |
| Severity Levels | Critical / High / Moderate / Low, auto-assigned by condition or manually overridden |
| Bed Allocation | Runs the Fractional Knapsack algorithm to allocate bed-days optimally |
| Step-by-Step View | See each greedy decision the algorithm makes, in order |
| Live Statistics | Tracks total patients, allocated, rejected, utilisation %, and benefit score |
| Remove Patients | Remove individual patients from the queue before running allocation |

---

## Algorithm

MediAlloc uses the **Fractional Knapsack (Greedy)** approach:

1. Compute **Ratio = Severity ÷ Treatment Days** for each patient (value density).
2. **Sort descending** by ratio — highest priority gets beds first.
3. Iterate through sorted list: if the patient fits in remaining capacity → **Allocate**, otherwise → **Reject**.
4. **Time complexity:** O(n log n) for sorting + O(n) for the greedy pass.

> Unlike the 0/1 Knapsack, this implementation does not split patients fractionally — a patient is either fully allocated or rejected. The "fractional" name refers to the ratio-based greedy selection strategy.

---

## Tech Stack

- **Python 3.x**
- **Streamlit** — UI and interactivity
- **Pandas** — table rendering and styling
- **dataclasses** — patient data modeling

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/medialoc.git
cd medialoc

# 2. Install dependencies
pip install streamlit pandas

# 3. Run the app
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## Usage

1. **Configure** total beds and average stay in the sidebar.
2. **Add patients** by name, age, and condition — or click **Random** / **Load Sample Patients**.
3. Click **⚡ Run Allocation Algorithm** to allocate beds.
4. View results across three tabs:
   - **Patient Queue** — full list with severity and status
   - **Allocation Results** — ranked output with utilisation stats
   - **Algorithm Steps** — step-by-step greedy execution trace

---

## Medical Conditions Supported

| Condition | Severity | Est. Days |
|---|---|---|
| Cardiac Arrest | 10 | 7 |
| Stroke | 9 | 10 |
| Trauma / Accident | 9 | 8 |
| Respiratory Failure | 8 | 6 |
| Sepsis | 8 | 9 |
| Diabetes Crisis | 7 | 4 |
| Hypertension Crisis | 7 | 3 |
| Appendicitis | 6 | 3 |
| Pneumonia | 6 | 7 |
| Fracture | 5 | 5 |
| Minor Surgery | 3 | 2 |
| Observation | 2 | 1 |

Severity can be overridden per patient using the sidebar slider.

---

## Authors


- Meeta Patil


---

## License

Free to use and modify for personal or college projects. Credit appreciated but not required.
