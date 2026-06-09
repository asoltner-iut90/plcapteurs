from heuristics.heuristic import Heuristic
import parse_data
import solver
import os
import time
import subprocess
import datetime


class TimeoutException(Exception):
    pass


class Tester:
    def __init__(self, heuristic: Heuristic ,logs=True ,verbose=False, timeout=None):
        self.verbose = verbose
        self.heuristic = heuristic
        self.logs = logs
        self.timeout = timeout

        # Configuration de l'enregistrement des logs
        self.log_dir = "logs"
        os.makedirs(self.log_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        heuristic_name = self.heuristic.__class__.__name__
        base_name = f"{heuristic_name}_{timestamp}"
        
        filename = os.path.join(self.log_dir, f"{base_name}.log")
        counter = 1
        while os.path.exists(filename):
            filename = os.path.join(self.log_dir, f"{base_name}_{counter}.log")
            counter += 1
            
        self.log_filename = filename
        
        # Obtenir les paramètres de l'heuristique
        params_str = ", ".join(f"{k}={v}" for k, v in self.heuristic.__dict__.items())
        if not params_str:
            params_str = "Aucun (valeurs par défaut ou pas de paramètres d'instance)"
            
        # Obtenir le hash git
        git_hash = self._get_git_hash()
        
        # Écriture de l'en-tête du fichier log
        with open(self.log_filename, "w", encoding="utf-8") as f:
            f.write(f"=== Rapport d'exécution ===\n")
            f.write(f"Heuristique : {heuristic_name}\n")
            f.write(f"Paramètres  : {params_str}\n")
            f.write(f"Commit Git  : {git_hash}\n")
            f.write(f"Date/Heure  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"===========================\n\n")

    def _get_git_hash(self) -> str:
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            status = subprocess.check_output(
                ["git", "status", "--porcelain"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            if status:
                git_hash += " (dirty)"
            return git_hash
        except Exception:
            return "N/A (Git non initialisé ou non installé)"

    def _log(self, message: str):
        if self.logs:
            with open(self.log_filename, "a", encoding="utf-8") as f:
                f.write(message + "\n")

    def _run_solver(self, file_path: str) -> dict:
        data = parse_data.parse_sensor_data(file_path)

        self.heuristic.solve(data)
        configurations_pool = self.heuristic.get_pool()
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
        
        msg_start = f"Exécution du test : {file_path}"
        print(msg_start)
        self._log(msg_start)

        start_time = time.time()
        # Initialisation du pool sur l'heuristique
        self.heuristic.current_pool = []
        try:
            if self.timeout and self.timeout > 0:
                import signal
                def handler(signum, frame):
                    raise TimeoutException("Limite de temps dépassée (Timeout)")
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(self.timeout)

            try:
                res = self._run_solver(file_path)
            finally:
                if self.timeout and self.timeout > 0:
                    import signal
                    signal.alarm(0)

            elapsed = time.time() - start_time
            obtained = res["objective"]

            expected, diff_str = self._get_expected_and_diff(obtained, out_file)
            expected_val = expected if expected is not None else "N/A"

            obtained_str = f"{obtained:.3f}" if isinstance(obtained, (int, float)) else str(obtained)
            expected_str = f"{expected_val:.3f}" if isinstance(expected_val, (int, float)) else str(expected_val)
            
            msg_result = f"Terminé en {elapsed:.2f}s | Obtenu: {obtained_str} (Attendu: {expected_str}) | Différence: {diff_str}"
            print(msg_result)
            self._log(msg_result)

            # Préparation de l'ordonnancement complet pour le fichier log (et optionnellement la console)
            schedule_lines = ["Ordonnancement choisi par le solveur :"]
            has_active_config = False
            for config, duration in res["schedule"].items():
                if duration and duration > 1e-5:
                    schedule_lines.append(f"  - Capteurs {list(config)} activés pendant {duration:.2f} unités de temps")
                    has_active_config = True

            if not has_active_config:
                schedule_lines.append("  - Aucune configuration active trouvée.")
            
            schedule_text = "\n".join(schedule_lines)
            
            # Affichage console si verbose=True
            if self.verbose:
                print(schedule_text)
                print()
            
            # Écriture systématique dans le log
            self._log(schedule_text)
            self._log("") # Ligne vide pour aérer

            return res["status"], elapsed, obtained, res["schedule"]

        except Exception as e:
            elapsed = time.time() - start_time
            pool = getattr(self.heuristic, "get_pool", lambda: [])()
            if pool:
                try:
                    print(f"Interruption détectée ({e}). Résolution partielle avec {len(pool)} configurations...")
                    data = parse_data.parse_sensor_data(file_path)
                    results = solver.solve_sensor_scheduling(data["lifetimes"], data["sensors"], pool)
                    obtained = results["objective"]
                    
                    expected, diff_str = self._get_expected_and_diff(obtained, out_file)
                    expected_val = expected if expected is not None else "N/A"
                    
                    obtained_str = f"{obtained:.3f}" if isinstance(obtained, (int, float)) else str(obtained)
                    expected_str = f"{expected_val:.3f}" if isinstance(expected_val, (int, float)) else str(expected_val)
                    
                    msg_result = f"Terminé (Partiel - Interrompu) en {elapsed:.2f}s | Obtenu: {obtained_str} (Attendu: {expected_str}) | Différence: {diff_str}"
                    print(msg_result)
                    self._log(msg_result)
                    
                    schedule_lines = ["Ordonnancement choisi par le solveur (Partiel) :"]
                    has_active_config = False
                    for config, duration in results["schedule"].items():
                        if duration and duration > 1e-5:
                            schedule_lines.append(f"  - Capteurs {list(config)} activés pendant {duration:.2f} unités de temps")
                            has_active_config = True
                    if not has_active_config:
                        schedule_lines.append("  - Aucune configuration active trouvée.")
                    
                    schedule_text = "\n".join(schedule_lines)
                    if self.verbose:
                        print(schedule_text)
                        print()
                    self._log(schedule_text)
                    self._log("")
                    
                    return "Timeout/Partial", elapsed, obtained, results["schedule"]
                except Exception as solve_err:
                    print(f"Erreur lors de la résolution partielle : {solve_err}")
            
            err_msg = f"Erreur lors de l'exécution de {file_path} : {e}"
            print(err_msg + "\n")
            self._log(err_msg + "\n")
            return "Error", elapsed, None, None

    def execute_all_tests(self):
        results = []
        for i in range(1, 6):
            res = self.execute_test(i)
            results.append(res)
        return results
