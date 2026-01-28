import functools
import itertools
from typing import Literal, Self, Tuple


@functools.total_ordering
class Age:
    def __init__(self, x: int, metric: Literal["year", "month", "week"]):
        """
        An age is a duration of time

        Args:
            x: number of units of time
            metric: unit
        """
        self.x = x
        self.metric = metric

    def _get_cmp(self, other: Self) -> Tuple[int, int]:
        if self.metric == other.metric:
            return (self.x, other.x)
        elif self.x == 0 and other.x == 0:
            return (0, 0)
        elif self.metric == "year" and other.metric == "month":
            return (self.x * 12, other.x)
        elif self.metric == "month" and other.metric == "year":
            return (self.x, other.x * 12)
        else:
            raise ValueError(f"Cannot compare {self} and {other}")

    def __eq__(self, other: Self) -> bool:
        x1, x2 = self._get_cmp(other)
        return x1 == x2

    def __lt__(self, other: Self) -> bool:
        x1, x2 = self._get_cmp(other)
        return x1 < x2

    def __repr__(self) -> str:
        return f"Age(x={self.x}, metric='{self.metric}')"

    def __hash__(self) -> int:
        return hash((self.x, self.metric))


class AgeGroup:
    def __init__(self, start: Age, end: Age):
        """
        An age group is an ordered pair of ages

        Args:
            start: lower end of the age range
            end: upper end of the range
        """
        assert start < end
        self.start = start
        self.end = end

    def is_in(self, other: Self) -> bool:
        """Is this range inside another range?"""
        return other.start <= self.start and self.end <= other.end

    def subdivide(self, cuts: list[Age]) -> list[Self]:
        """Break this range down into smaller ranges"""
        assert len(cuts) >= 2
        assert cuts[0] == self.start
        assert cuts[-1] == self.end

        return [type(self)(start, end) for start, end in itertools.pairwise(cuts)]

    def __repr__(self) -> str:
        return f"AgeGroup({self.start}, {self.end})"

    def __eq__(self, other: Self) -> bool:
        return self.start == other.start and self.end == other.end
