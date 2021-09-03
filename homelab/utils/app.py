from abc import ABC, abstractmethod
from typing import List
from homelab.utils.k8s import K8s


class App(ABC):
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        pass

    @abstractmethod
    def deploy(self, k8s: K8s, config: dict):
        pass
