#!/usr/bin/env python3
"""CLI to analyze a blood report file (PDF/PNG/JPG) and print lab assessments.

Usage:
  python scripts/analyze_report.py /path/to/report.pdf --age adult
"""
import argparse
import sys
import os

# Ensure project root is on sys.path so imports work when this script
# is executed from the `scripts/` directory.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ocr_helper import extract_blood_report_text, parse_lab_values, assess_lab_values
from recommendation_engine import get_recommendations_for_assessment, generate_meal_plan_recommendation


def print_section(title):
    print('\n' + '=' * 60)
    print(title)
    print('-' * 60)


def main():
    p = argparse.ArgumentParser(description='Analyze a blood report file and print nutrition recommendations')
    p.add_argument('file', help='Path to report file (PDF/PNG/JPG)')
    p.add_argument('--age', default='adult', help='Age category: toddler, child, teen, adult, senior')
    p.add_argument('--save', help='Optional path to save text output')
    args = p.parse_args()

    path = args.file
    age = args.age

    print(f'Analyzing: {path} (age category: {age})')

    txt = extract_blood_report_text(path)
    if not txt:
        print('No text extracted from file or extraction failed.')
        sys.exit(2)

    lab_values = parse_lab_values(txt)

    print_section('Parsed Lab Values')
    if lab_values:
        for k, v in lab_values.items():
            print(f'{k}: {v}')
    else:
        print('No lab values detected.')

    assessments = assess_lab_values(lab_values, age)
    print_section('Assessments')
    if assessments:
        for a in assessments:
            print(f"{a['test']}: {a['value']} {a['unit']} — {a['status']} (range {a['normal_range']})")
    else:
        print('No assessments available.')

    try:
        recs = get_recommendations_for_assessment(assessments, age)
    except Exception as e:
        recs = {'test_recommendations': [], 'age_guidance': {}, 'general_tips': []}
        print(f'Failed to generate recommendations: {e}')

    print_section('Recommendations (Summary)')
    if recs.get('test_recommendations'):
        for r in recs['test_recommendations']:
            print(f"{r['test']} ({r['status']}): {r.get('issue','')}")
            if r.get('foods'):
                print('  Foods:', ', '.join(r['foods']))
            if r.get('actions'):
                print('  Actions:', ', '.join(r['actions']))
            print('')
    else:
        print('No test-specific recommendations.')

    print_section('Age-specific Guidance')
    ag = recs.get('age_guidance') or {}
    if ag:
        print(ag.get('focus',''))
        print('Key nutrients:', ', '.join(ag.get('key_nutrients',[])))
    else:
        print('No age guidance.')

    print_section('General Tips')
    for t in recs.get('general_tips', []):
        print('-', t)

    # Show a sample meal plan (best-effort)
    try:
        meal_plan = generate_meal_plan_recommendation(recs, age)
        print_section('Sample Meal Plan (per age group)')
        meals = meal_plan.get('breakfast') or meal_plan
        # If returned structure contains meal keys directly
        if isinstance(meal_plan, dict) and 'meals' in meal_plan:
            meals = meal_plan['meals']
            times = meal_plan.get('times')
            calmap = meal_plan.get('calories_per_meal')
            for m, items in meals.items():
                time = times.get(m) if times else ''
                cal = f" [{calmap.get(m)} kcal]" if calmap else ''
                print(f"{m.capitalize()} {time}{cal}:")
                for it in items:
                    print('  -', it)
        else:
            # older structure: expect breakfast/lunch/dinner keys
            for m, items in meal_plan.items():
                if isinstance(items, list):
                    print(f"{m.capitalize()}:")
                    for it in items:
                        print('  -', it)
    except Exception as e:
        print('Failed to generate meal plan:', e)

    if args.save:
        try:
            with open(args.save, 'w', encoding='utf-8') as fh:
                fh.write(txt)
            print(f'Extracted text saved to {args.save}')
        except Exception as e:
            print('Failed to save extracted text:', e)

if __name__ == '__main__':
    main()
