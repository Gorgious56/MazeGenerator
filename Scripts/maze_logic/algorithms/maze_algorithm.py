from random import seed


class MazeAlgorithm:
    def __init__(self, _seed=None, _max_steps=0):
        self._seed = _seed
        seed(self._seed)
        self.__max_steps = 100000 if _max_steps <= 0 else _max_steps
        self.__steps = 0

    def must_break(self):
        return self.__steps >= self.__max_steps

    def next_step(self):
        self.__steps += 1
