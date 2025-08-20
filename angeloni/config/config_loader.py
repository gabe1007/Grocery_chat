import yaml
from typing import Dict, Any, List
from pathlib import Path

class AngeloniConfig:
    """
    Configuration loader for Angeloni scraper settings.
    This class loads configuration settings from a YAML file and provides
    convenient property accessors for different configuration sections.
    The configuration file path can be specified during initialization,
    or it will default to 'angeloni_config.yaml' in the same directory as this script.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the configuration loader.
        """
        if config_path is None:
            script_dir = Path(__file__).parent
            config_path = script_dir / "angeloni_config.yaml"
        
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file.
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    @property
    def base_url(self) -> str:
        """
        Get the base URL for the application.
        """
        return self._config["base_url"]
    
    @property
    def selectors(self) -> Dict[str, Any]:
        """
        Get CSS selectors for web scraping.
        """
        return self._config["selectors"]
    
    @property
    def timeouts(self) -> Dict[str, int]:
        """
        Get timeout values for various operations.
        """
        return self._config["timeouts"]
    
    @property
    def browser_args(self) -> List[str]:
        """
        Get browser launch arguments.
        """
        return self._config["browser_args"]
    
    @property
    def viewport(self) -> Dict[str, int]:
        """
        Get browser viewport dimensions.
        """
        return self._config["viewport"]
    
    @property
    def user_agent(self) -> str:
        """
        Get the user agent string for HTTP requests.
        """
        return self._config["user_agent"]