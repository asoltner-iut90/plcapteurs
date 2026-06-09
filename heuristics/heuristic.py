from abc import ABC, abstractmethod

class Heuristic(ABC):
    def __init__(self):
        self.current_pool = []

    def get_pool(self) -> list[list[int]]:
        if not hasattr(self, 'current_pool'):
            self.current_pool = []
        return self.current_pool

    @abstractmethod
    def solve(self, parsed_data: dict) -> None:
        """
        Prend les données parsées et met à jour le pool interne (self.current_pool).
        Ne retourne rien. Utiliser get_pool() pour récupérer les résultats.
        """
        pass
