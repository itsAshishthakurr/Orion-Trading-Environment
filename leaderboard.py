class Leaderboard:
    def display(self, results, difficulty):
        print("\n" + "=" * 70)
        print(f"  ORION TRADING SIMULATION - {difficulty.upper()}")
        print("  (Reward = RL performance score, Profit = actual ₹ gain/loss)\n")
        print("=" * 70)

        # sort by score
        results = sorted(results, key=lambda r: r["score"], reverse=True)

        print(f"{'Rank':<6}{'Agent':<12}{'Reward':>10}{'Final Balance':>18}{'Profit':>12}")
        print("-" * 70)

        for i, r in enumerate(results, 1):
            profit = r["final_balance"] - r["initial_balance"]
            print(
                f"[{i}]   "
                f"{r['agent']:<12}"
                f"{r['score']:>10.2f}"
                f"{r['final_balance']:>18.2f}"
                f"{profit:12.2f}"
            )

        print("-" * 70)

        for r in results:
            if "action_log" in r and "step_rewards" in r:

                print(f"\n--- {r['agent']} STEP LOG (first 10 steps) ---")

                for i, (a, rew) in enumerate(zip(r["action_log"], r["step_rewards"])):
                    if i >= 10:
                      break
                    print(f"Step {i+1:>2}: {a:<5} | Reward: {rew:.2f}")
                
        print("\n" + "=" * 70)
        