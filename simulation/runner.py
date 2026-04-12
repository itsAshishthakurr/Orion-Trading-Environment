from agents.random_agent import RandomAgent 
from agents.smart_agent import SmartAgent
from agents.learning_agent import LearningAgent
from env.environment import TradingEnvironment
from grader import Grader
from leaderboard import Leaderboard


class Runner:
    def __init__(self, task):
        self.task = task

    def run_episode(self, agent, train=True):
        env = TradingEnvironment(self.task)

        obs = env.reset()
        agent.reset()

        initial_value = env.state.balance
        step_rewards = []
        action_log = []
        invalid_count = 0

        

        total_reward = 0

        while True:
            action = agent.select_action(obs)

            next_obs, reward, done = env.step(action)

            step_rewards.append(reward.total)
            action_log.append(action)

            if "invalid" in reward.penalties:
                invalid_count += 1
  

            if train:
                agent.update(reward, next_obs)

            obs = next_obs
            total_reward += reward.total

            if done:
                break

        # Portfolio value = cash + value of held shares
        final_value = env.state.balance + env.state.holdings * env.state.price

        stats = {
            "final_balance": final_value,
            "step_rewards": step_rewards,
            "action_log": action_log,
            "invalid_count": invalid_count,
            "difficulty": self.task.get("name", "unknown")
            }

        grader = Grader()

        result = grader.evaluate(
            agent.__class__.__name__,
            initial_value,
            stats
            )
        
        result["action_log"] = action_log
        result["step_rewards"] = step_rewards
        result["initial_balance"] = initial_value


        return result

    def run_all_agents(self):
        agents = {
            "Random": RandomAgent(),
            "Smart": SmartAgent(),
            "Learning": LearningAgent()
        }

        results = []

        for name, agent in agents.items():

            #  TRAIN ONLY LEARNING AGENT
            if name == "Learning":
                for _ in range(20000):   
                    self.run_episode(agent, train=True)

            
                agent.epsilon = 0.05

            # evaluation = NO learning
            result = self.run_episode(agent, train=False)

            results.append(result)


        lb = Leaderboard()
        lb.display(results, self.task.get("name", "unknown"))


        return results