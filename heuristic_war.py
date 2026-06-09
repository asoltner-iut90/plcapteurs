import os
import sys
import time

# Add heuristics folder to sys.path to allow sibling imports (e.g. from heuristic import Heuristic)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "heuristics")))

from tester import Tester

from heuristics.random_pruning import RandomPruning
from heuristics.column import ColumnGeneration
from heuristics.dual_weights import DualWeightsHeuristic
from heuristics.matheuristic import Matheuristic

def load_expected_values():
    expected = {}
    for i in range(1, 6):
        out_file = f"tests/{i:02d}.out"
        if os.path.exists(out_file):
            try:
                with open(out_file, 'r') as f:
                    val = float(f.read().strip())
                    expected[i] = val
            except Exception:
                expected[i] = None
        else:
            expected[i] = None
    return expected

def print_markdown_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    header_str = "| " + " | ".join(f"{str(h).ljust(widths[idx])}" for idx, h in enumerate(headers)) + " |"
    sep_str = "|-" + "-|-".join("-" * widths[idx] for idx in range(len(headers))) + "-|"
    print(header_str)
    print(sep_str)
    
    for row in rows:
        row_str = "| " + " | ".join(f"{str(val).ljust(widths[idx])}" for idx, val in enumerate(row)) + " |"
        print(row_str)

def main():
    expected_values = load_expected_values()
    
    heuristics_to_run = [
        ("RandomPruning", RandomPruning()),
        ("ColumnGeneration", ColumnGeneration()),
        ("DualWeights", DualWeightsHeuristic()),
        ("Matheuristic", Matheuristic())
    ]
    
    results_by_heuristic = {}
    
    print("=" * 60)
    print("DÉBUT DES COMBATS D'HEURISTIQUES")
    print("=" * 60)
    
    for name, heuristic in heuristics_to_run:
        print(f"\n>>> Évaluation de l'heuristique : {name}")
        print("-" * 50)
        # Disable logging to avoid creating 10 separate log files per run, keeping verbose off
        tester = Tester(heuristic, logs=False, verbose=False, timeout=180)
        test_results = tester.execute_all_tests()
        results_by_heuristic[name] = test_results
        
    print("\n" + "=" * 60)
    print("FIN DE L'ÉVALUATION - RAPPORTS FINAUX")
    print("=" * 60)
    
    # Build Objectives Table
    headers_obj = ["Heuristique"]
    for i in range(1, 6):
        exp = expected_values[i]
        exp_str = f"{exp:.3f}" if exp is not None else "N/A"
        headers_obj.append(f"Test {i} (Att: {exp_str})")
        
    rows_obj = []
    for name in results_by_heuristic:
        row = [name]
        for idx, res in enumerate(results_by_heuristic[name]):
            status, elapsed, obtained, schedule = res
            if obtained is None:
                row.append("Erreur")
            else:
                exp = expected_values[idx + 1]
                if exp is not None and exp != 0:
                    diff_pct = ((obtained - exp) / exp) * 100
                    row.append(f"{obtained:.3f} ({diff_pct:+.2f}%)")
                else:
                    row.append(f"{obtained:.3f}")
        rows_obj.append(row)
        
    print("\n### Valeurs Objectifs Obtenues & Écarts (Diff %)")
    print_markdown_table(headers_obj, rows_obj)
    
    # Build Times Table
    headers_time = ["Heuristique"] + [f"Test {i}" for i in range(1, 6)]
    rows_time = []
    for name in results_by_heuristic:
        row = [name]
        for res in results_by_heuristic[name]:
            status, elapsed, obtained, schedule = res
            row.append(f"{elapsed:.2f}s")
        rows_time.append(row)
        
    print("\n### Temps d'Exécution")
    print_markdown_table(headers_time, rows_time)

if __name__ == "__main__":
    main()
