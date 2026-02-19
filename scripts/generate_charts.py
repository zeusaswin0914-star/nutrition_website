netstat -ano | findstr ":5000"
"""Generate sample diet charts and save PNG files to static/charts.

Run:
  python scripts/generate_charts.py

This will create `static/charts/<timestamp>/` with PNG files you can open locally.
"""
import os
import sys
import base64
from datetime import datetime

# ensure project root is on sys.path so imports work when run as a script
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from diet_chart_generator import generate_complete_diet_chart


def _save_data_uri(data_uri, path):
    # data:image/png;base64,AAAA
    assert data_uri.startswith('data:'), 'Not a data URI'
    header, b64 = data_uri.split(',', 1)
    data = base64.b64decode(b64)
    with open(path, 'wb') as f:
        f.write(data)


def main():
    out_dir = os.path.join('static', 'charts', datetime.now().strftime('%Y%m%d_%H%M%S'))
    os.makedirs(out_dir, exist_ok=True)

    sample = {
        'calories': 2200,
        'macros': {'carbs': 0.5, 'protein': 0.2, 'fat': 0.3},
        'lab_values': {'HGB': 13.0, 'SGP': 90.0, 'TCP': 180.0},
        'deficiencies': [],
        'normal_ranges': {},
        'food_reco': {}
    }

    charts = generate_complete_diet_chart(sample)

    saved = []
    for key, uri in charts.items():
        fname = f"{key}.png"
        path = os.path.join(out_dir, fname)
        try:
            _save_data_uri(uri, path)
            saved.append(path)
        except Exception as e:
            print('Failed to save', key, e)

    print('Saved charts:')
    for p in saved:
        print(' -', os.path.abspath(p))


if __name__ == '__main__':
    main()
