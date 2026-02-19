**Project Overview**
- **Repo purpose:** A small Flask app that estimates daily calories and generates simple nutrition recommendations from user inputs and lab biomarkers. Key pieces: `app.py` (Flask), `model_train.py` (creates `calorie_model.pkl`), `nutrition_engine.py` (lab analysis + food recommendations), and data ingestion scripts (`read_lab.py`).

**Quick Start (Windows PowerShell)**
- **Create venv & install:**
  - `python -m venv env1` (or reuse provided `env1`)
  - `env1\Scripts\Activate.ps1; pip install -r requirements.txt`
- **Generate model artifact:** `python model_train.py` -> creates `calorie_model.pkl` in repo root.
- **Prepare lab dataset (if you have source files):** `python read_lab.py` -> requires `lab.sas` and `lab.dat`, outputs `lab_clean.csv`.
- **Run the web app:** `python app.py` (Flask runs with `debug=True` by default).

**Important File Relationships & Data Flow**
- `read_lab.py` parses `lab.sas` + `lab.dat` to produce `lab_clean.csv` used by `nutrition_engine.py`.
- `model_train.py` trains a scikit-learn pipeline and saves `(model, num_cols, medians)` into `calorie_model.pkl` with `joblib.dump`.
- `app.py` loads `calorie_model.pkl` via `joblib.load` and calls `model.predict(user_data)`; it also calls `analyze_biomarkers` and `recommend_foods` from `nutrition_engine.py`.

**Project-specific patterns & gotchas (discoverable)**
- Model artifact shape: `calorie_model.pkl` holds a tuple `(model, num_cols, medians)` — code expects to unpack three elements when loading.
- Feature mismatch risk: `model_train.py`'s `num_cols` includes many columns (e.g., `sex`, `activity`, `hemoglobin`, etc.) while `app.py` currently constructs `user_data = np.array([[age, height, weight]])` (only 3 values). Agents should either update the model training to match the minimal input or adapt `app.py` to supply the full feature vector (using medians from the saved artifact).
- `nutrition_engine.py` behavior: it will silently run in “basic mode” if `lab_clean.csv` is missing. It exposes `analyze_biomarkers(values)` and `recommend_foods(deficiencies)` as the integration surface used by `app.py`.
- File names and locations are significant: `calorie_model.pkl` and `lab_clean.csv` are loaded by relative path from the repo root at runtime.

**Developer Workflows**
- Rebuild model (dev): `python model_train.py` — inspect printed `✔ calorie_model.pkl created successfully!`.
- Recreate lab CSV (when you have raw data): `python read_lab.py` — script exits if `lab.sas` or `lab.dat` are missing.
- Run app for manual testing: `python app.py` then open `http://127.0.0.1:5000/`.

**Debugging tips**
- If `joblib.load("calorie_model.pkl")` fails: confirm the file exists and was created by `model_train.py` and that you're running from repo root.
- If predictions raise shape errors: check `num_cols` inside the saved artifact; construct an input vector matching `num_cols` order (use medians for missing numerical features).
- For missing lab features: `read_lab.py` logs available columns and saves only found nutritional biomarkers to `lab_clean.csv`.

**Where to make changes**
- Add features or change the model: edit `model_train.py` (data generation → columns → model pipeline) and regenerate `calorie_model.pkl`.
- Change nutrition rules: edit `nutrition_engine.py` (`NORMAL_RANGES`, `FOOD_RECO`, and `analyze_biomarkers`).
- Change web UI: `templates/index.html` (form field names must match what `app.py` reads).

**Examples (snippets agents may use)**
- Load model and medians to fill missing features:
  ```py
  model, num_cols, medians = joblib.load("calorie_model.pkl")
  # build input dict with medians for missing fields
  inp = {c: medians.get(c, 0) for c in num_cols}
  inp.update({'age': age, 'height': height, 'weight': weight})
  X = [inp[c] for c in num_cols]
  pred = model.predict([X])
  ```

**Files to inspect first (for contributors)**
- `app.py`, `model_train.py`, `nutrition_engine.py`, `read_lab.py`, `templates/index.html`, `requirements.txt`.

If anything is unclear or you want this condensed further (or expanded into contributor docs / a checklist), tell me which part to polish next.