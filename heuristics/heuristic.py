from abc import ABC, abstractmethod

class Heuristic(ABC):
    @abstractmethod
    def solve(self, parsed_data: dict) -> list[list[int]]:
        """
        Prend les données parsées et retourne un pool de configurations (liste de listes).
        """
        pass
