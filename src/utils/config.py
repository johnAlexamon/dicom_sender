"""
Configuration handling for Alexamon DICOM Sender
"""

import os
import json
import logging

class ConfigManager:
    """Handles loading and saving application configuration"""
    
    def __init__(self):
        self.default_config = {
            "default_ip": "127.0.0.1",
            "default_port": "11112",
            "default_ae_title": "STORE_SCP"
        }
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default if not found"""
        # First try to find the config file in the project root
        possible_paths = [
            'config.json',  # Current directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json'),  # Project root if running from src
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')  # Src directory
        ]
        
        for config_path in possible_paths:
            try:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        logging.info(f"Loaded configuration from {config_path}")
                        return json.load(f)
            except Exception as e:
                logging.warning(f"Error reading config from {config_path}: {str(e)}")
        
        # Create default config if file doesn't exist
        # Try to save in project root
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json')
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.default_config, f, indent=4)
                logging.info(f"Created default configuration at {config_path}")
        except Exception as e:
            # Fall back to current directory
            config_path = 'config.json'
            with open(config_path, 'w') as f:
                json.dump(self.default_config, f, indent=4)
                logging.info(f"Created default configuration at current directory")
        
        return self.default_config

    def save_config(self, config):
        """Save configuration to the file"""
        # Try to find the existing config file
        possible_paths = [
            'config.json',  # Current directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json'),  # Project root if running from src
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')  # Src directory
        ]
        
        config_path = None
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        # If not found, save to project root
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config.json')
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
                logging.info(f"Saved settings to {config_path}")
                self.config = config
                return True
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")
            # Fall back to current directory
            try:
                with open('config.json', 'w') as f:
                    json.dump(config, f, indent=4)
                    logging.info("Saved settings to current directory")
                    self.config = config
                    return True
            except Exception as e2:
                logging.error(f"Failed to save config to fallback location: {str(e2)}")
                return False
    
    def get_value(self, key, default=None):
        """Get a configuration value by key"""
        return self.config.get(key, default) 