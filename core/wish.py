from dataclasses import dataclass

from .drop import Drop


@dataclass
class Wish:
    drop: Drop
