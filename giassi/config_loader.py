import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

class Config:
    def __init__(self, config_path: str = "/home/gabriel/Documentos/giassi_mcp/giassi/config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    @property
    def base_url(self) -> str:
        return self._config["base_url"]

    @property
    def selectors(self) -> Dict[str, Any]:
        return self._config["selectors"]

    @property
    def timeouts(self) -> Dict[str, int]:
        return self._config["timeouts"]

    @property
    def browser_args(self) -> List[str]:
        return self._config["browser_args"]

    @property
    def viewport(self) -> Dict[str, int]:
        return self._config["viewport"]

    @property
    def user_agent(self) -> str:
        return self._config["user_agent"]