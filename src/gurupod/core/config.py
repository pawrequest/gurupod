from __future__ import annotations

import shutil
import sys
import tomllib
from pathlib import Path

from loguru import logger


def get_config(conf_path, default_config, data_dir):
    if conf_path.exists():
        with open(conf_path, "rb") as f:
            guru_conf = tomllib.load(f)
            logger.info(f"Loaded config from {conf_path}", bot_name="BOOT")

    else:
        with open(default_config, "wb") as f:
            guru_conf = tomllib.load(f)
            logger.info(f"Loaded default config from {default_config}", bot_name="BOOT")
            logger.info(
                f"Initialising with default values:\n{[f"{k} = {v}" for k, v in guru_conf.items()]}", bot_name="BOOT"
            )
            Path.mkdir(data_dir, exist_ok=True)
            shutil.copy(default_config, conf_path)

    return guru_conf

    # breaks docker-compose build #
    # else:
    #     logger.warning(f"Config file not found at {conf_path}", bot_name="BOOT")
    #     existing_configs = [p for p in default_configs if p.exists()]
    #
    #     if len(existing_configs) == 1:
    #         default_config_path = existing_configs[0]
    #
    #     elif len(existing_configs) > 1:
    #         logger.warning(f"Multiple default config files found: {existing_configs}", bot_name="BOOT")
    #         for num, conf in enumerate(existing_configs, start=1):
    #             logger.info(f"({num}.) - {conf}")
    #         chosen = int(input("Choose one of the above config files:"))
    #         default_config_path = existing_configs[chosen - 1]
    #     else:
    #         sys.exit("No config files found")

    # with open(default_config_path, "rb") as f:
    #     def_conf = tomllib.load(f)
