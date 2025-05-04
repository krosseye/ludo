#############################################################################
##
## Copyright (C) 2025 Killian-W.
## All rights reserved.
##
## This file is part of the Ludo project.
##
## Licensed under the MIT License.
## You may obtain a copy of the License at:
##     https://opensource.org/licenses/MIT
##
## This software is provided "as is," without warranty of any kind.
##
#############################################################################

import json
from typing import Any, Dict

from utilities.helpers import load_json

from ..constants import DEFAULT_USER_CONFIG


class UserConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.default_config = DEFAULT_USER_CONFIG
        self.config_path = None
        self.user_config = None

    def has_config(self):
        return self.config_path is not None and self.user_config is not None

    def set_config_file(self, config_file_path):
        self.config_path = config_file_path
        self.user_config = self._load_user_config()

    def _load_user_config(self) -> Dict[str, Any]:
        """Load user config if exists, otherwise return empty dict"""
        try:
            return load_json(self.config_path)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def get(self, key: str) -> Any:
        """Get a config value, falling back to default if not in user config"""
        return self.user_config.get(key, self.default_config.get(key))

    def set(self, key: str, value: Any):
        """Set a user config value"""
        self.user_config[key] = value

    def save(self):
        """Save user config to file"""
        with open(self.config_path, "w") as f:
            json.dump(self.user_config, f, indent=4)

    def __getitem__(self, key: str) -> Any:
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        self.set(key, value)

    def copy(self) -> Dict[str, Any]:
        """Return a full config dict combining defaults with user overrides"""
        combined = self.default_config.copy()
        combined.update(self.user_config)
        return combined


user_config = UserConfig()
