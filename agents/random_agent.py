import random
from agents.base_agent import BaseAgent


class RandomAgent(BaseAgent):
    def select_action(self, observation):
        return random.choice(["BUY", "SELL", "HOLD"])
    
    def update(self, reward, next_observation):
        pass

    def reset(self):
        pass