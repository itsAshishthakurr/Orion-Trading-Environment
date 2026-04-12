class BaseAgent:
    def select_action(self, observation):
        raise NotImplementedError

    def update(self, reward, next_observation):
        pass

    def reset(self):
        pass
    