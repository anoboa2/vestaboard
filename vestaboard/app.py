from typing import List, Optional, Literal, Union, Annotated
import os

import requests
from pydantic import BaseModel, Field, computed_field

from .models import Row, Board, Device, Characters
from .utils import convert_to_character_code

VESTABOARD_API_KEY = os.getenv("VESTABOARD_API_KEY")

class BaseInstallable(BaseModel):
    name: str
    description: str
    device: Device
    next_refresh_increment: int = 0