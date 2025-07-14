import datetime
import re
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field

from src.models.KPI import KPI


class Settings(BaseModel):
    MOVE_FILES_TO_PROCESSED_FOLDER: Optional[bool] = False
    ADD_TIMESTAMP_TO_PROCESSED_FILES: Optional[bool] = False
    CARD_IMAGE_FOLDER: Optional[Path] = Path("media/cards")
    INPUT_FOLDER: Optional[Path] = Path("input")
    OUTPUT_FOLDER: Optional[Path] = Path("output")
    LOG_TO_FILE: Optional[bool] = False
    SAVE_CACHE: Optional[bool] = False
    SAVE_CACHE_COPY_AS_CSV: Optional[bool] = False
    TIMESTAMP: Optional[str] = ""
    TIMESTAMP_LABEL: Optional[str] = ""
    INPUT_FILE_REGEX: Optional[re.Pattern] = re.compile(r"([2-9tjqka][hdcs]){3,5}_(call|fold|raise|check|bet|bet[0-9]{1,3})\.txt")
    KPIS: Optional[list[KPI]] = Field(default_factory=list)


file_path = Path("settings.yml")
if file_path.exists():
    yml_dict = yaml.safe_load(file_path.read_text())
    yml_dict["TIMESTAMP"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    yml_dict["TIMESTAMP_LABEL"] = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    SETTINGS = Settings(**yml_dict)
