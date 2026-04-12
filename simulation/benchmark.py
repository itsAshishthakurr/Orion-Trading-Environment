from simulation.runner import Runner
from tasks.tasks import TASKS


class Benchmark:
    def run(self):
        final_results = {}

        for name, task in TASKS.items():

            task["name"] = name
            runner = Runner(task)

            results = runner.run_all_agents()
            final_results[name] = results

        self._print_results(final_results)

        return final_results

    def _print_results(self, results):
        print("\n===== ORION BENCHMARK =====\n")

        for task, res in results.items():
            print(f"\nTask: {task}")

            for r in res:
                print(f" {r['agent']:<10} → {r['score']:.2f}")