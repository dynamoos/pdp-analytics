import datetime
from dataclasses import dataclass
from datetime import date
from typing import Tuple


@dataclass(frozen=True)
class Period:
    """Value object representing a time period"""

    year: int
    month: int

    def __post_init__(self):
        if self.year < 2020 or self.year > 2100:
            raise ValueError(f"Invalid year: {self.year}")

        if self.month < 1 or self.month > 12:
            raise ValueError(f"Invalid month: {self.month}")

    @classmethod
    def from_date(cls, date_obj: date) -> "Period":
        return cls(year=date_obj.year, month=date_obj.month)

    @property
    def formatted(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"

    @property
    def month_name(self) -> str:
        months = {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }
        return months[self.month]

    def get_date_range(self) -> Tuple[date, date]:
        start_date = date(self.year, self.month, 1)

        if self.month == 12:
            end_date = date(self.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = date(self.year, self.month + 1, 1) - datetime.timedelta(days=1)

        return start_date, end_date

    def __str__(self) -> str:
        return self.formatted
