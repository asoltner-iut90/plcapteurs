from heuristic import Heuristic
import parse_data
import solver
import os
import time


class Tester:
    def __init__(self, heuristic: Heuristic, verbose=False):
        self.verbose = verbose
        self.heuristic = heuristic

    def _run_solver(self, file_path: str) -> dict:
        data = parse_data.parse_sensor_data(file_path)

        configurations_pool = self.heuristic.solve(data)
        best_config = min(configurations_pool, key=len) if configurations_pool else []

        results = solver.solve_sensor_scheduling(data["lifetimes"], data["sensors"], configurations_pool)
        return {
            "best_config": best_config,
            "status": results["status"],
            "objective": results["objective"],
            "schedule": results["schedule"]
        }

    def _get_expected_and_diff(self, obtained: float, out_file: str) -> tuple:
        if os.path.exists(out_file):
            try:
                with open(out_file, 'r') as f:
                    expected = float(f.read().strip())
                if expected != 0:
                    diff_pct = ((obtained - expected) / expected) * 100
                    diff_str = f"{diff_pct:+.2f}%"
                else:
                    diff_str = "0.00%" if obtained == 0 else "N/A"
                return expected, diff_str
            except Exception:
                pass
        return None, "N/A"

    def execute_test(self, n: int):
        file_path = f"tests/{n:02d}.in"
        out_file = file_path.rsplit('.', 1)[0] + ".out"
        print(f"Exécution du test : {file_path}")

        start_time = time.time()
        try:
            res = self._run_solver(file_path)
            elapsed = time.time() - start_time
            obtained = res["objective"]

            expected, diff_str = self._get_expected_and_diff(obtained, out_file)
            expected_val = expected if expected is not None else "N/A"

            print(f"Terminé en {elapsed:.2f}s | Obtenu: {obtained:2f} (Attendu: {expected_val}) | Différence: {diff_str}")

            if self.verbose:
                print("Ordonnancement choisi par le solveur :")
                has_active_config = False
                for config, duration in res["schedule"].items():
                    if duration and duration > 1e-5:
                        print(f"  - Capteurs {list(config)} activés pendant {duration:.2f} unités de temps")
                        has_active_config = True

                if not has_active_config:
                    print("  - Aucune configuration active trouvée.")
            print()

        except Exception as e:
            print(f"Erreur lors de l'exécution de {file_path} : {e}\n")

    def execute_all_tests(self):
        for i in range(1, 6):
            self.execute_test(i)
