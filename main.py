import argparse
from simulation.benchmark import Benchmark
from simulation.runner import Runner
from tasks.tasks import TASKS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--difficulty", type=str, default="all")

    args = parser.parse_args()

    if args.difficulty == "all":
        benchmark = Benchmark()
        benchmark.run()
    else:
        task = TASKS.get(args.difficulty)

        if not task:
            print("Invalid difficulty")
            return

        runner = Runner(task)
        results = runner.run_all_agents()

        print(f"\nResults for {args.difficulty}:\n")
        for k, v in results.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()