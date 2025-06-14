import datetime
from dataclasses import dataclass
from datetime import date


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

    def get_date_range(self) -> tuple[date, date]:
        start_date = date(self.year, self.month, 1)

        if self.month == 12:
            end_date = date(self.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = date(self.year, self.month + 1, 1) - datetime.timedelta(days=1)

        return start_date, end_date
