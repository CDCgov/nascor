import functools
import itertools
import re
from typing import Iterable, Literal, Self, Tuple

Unit = Literal["year", "month", "week"]


@functools.total_ordering
class Age:
    def __init__(self, n: int, unit: Unit):
        """
        An age is a duration of time

        Args:
            n: number of units of time
            unit: one of `"year"`, `"month"`, or `"week"`
        """
        assert n >= 0
        self.n = n
        self.unit = unit

    def _get_cmp(self, other: Self) -> Tuple[int, int]:
        """
        To enable comparison of ages, convert, where possible, into a
        pair of values in the the same units.
        """
        if self.unit == other.unit:
            return (self.n, other.n)
        elif self.n == 0 and other.n == 0:
            return (0, 0)
        elif self.unit == "year" and other.unit == "month":
            return (self.n * 12, other.n)
        elif self.unit == "month" and other.unit == "year":
            return (self.n, other.n * 12)
        else:
            raise ValueError(f"Cannot compare {self} and {other}")

    def __eq__(self, other: Self) -> bool:
        n1, n2 = self._get_cmp(other)
        return n1 == n2

    def __lt__(self, other: Self) -> bool:
        if self.n == 0 and other.n > 0:
            return True
        else:
            n1, n2 = self._get_cmp(other)
            return n1 < n2

    def __repr__(self) -> str:
        return f"Age(n={self.n}, unit='{self.unit}')"

    def __hash__(self) -> int:
        return hash((self.n, self.unit))


class AgeRange:
    def __init__(self, lower: Age, upper: Age | None):
        """
        An age range is an ordered pair of ages

        Args:
            lower: lower limit of the age range
            upper: upper limit of the range. `None` means no upper limit.
        """
        if upper is not None:
            assert lower < upper

        self.lower = lower
        self.upper = upper

    def is_in(self, other: Self) -> bool:
        """Is this range inside another range?"""
        return other.lower <= self.lower and (
            # upper infinite ranges are OK
            (self.upper is None and other.upper is None)
            # finite fits inside infinite
            or (self.upper is not None and other.upper is None)
            or (
                # if both are finite, do the normal comparison
                self.upper is not None
                and other.upper is not None
                and self.upper <= other.upper
            )
        )

    def subdivide(self, cuts: list[Age]) -> list[Self]:
        """Break this range down into smaller ranges"""
        assert len(cuts) >= 2
        assert cuts[0] == self.lower
        assert cuts[-1] == self.upper

        return [type(self)(lower, upper) for lower, upper in itertools.pairwise(cuts)]

    def __repr__(self) -> str:
        return f"AgeRange({self.lower}, {self.upper})"

    def __eq__(self, other: Self) -> bool:
        return self.lower == other.lower and self.upper == other.upper


"""
The master list of age ranges we can parse.

Each element is a tuple of
- A regex which can extract the single age or the lower/upper ages and
- A Callable which returns an AgeRange
"""
PARSERS = (
    (
        re.compile(r"^(\d+) years?$"),
        lambda x: AgeRange(Age(int(x[0]), "year"), Age(int(x[0]) + 1, "year")),
    ),
    (
        re.compile(r"^(\d+)\+ years?$"),
        lambda x: AgeRange(Age(int(x[0]), "year"), None),
    ),
    (
        re.compile(r"^(\d+)-(\d+) years?$"),
        lambda x: AgeRange(Age(x[0], "year"), Age(int(x[1]) + 1, "year")),
    ),
    (
        re.compile(r"^(\d+)-<(\d+) years?$"),
        lambda x: AgeRange(Age(int(x[0]), "year"), Age(int(x[1]), "year")),
    ),
    (
        re.compile(r"^(\d+) months?-(\d+) years?$"),
        lambda x: AgeRange(Age(int(x[0]), "month"), Age(int(x[1]) + 1, "year")),
    ),
    (
        re.compile(r"^(\d+) months?-<(\d+) years?$"),
        lambda x: AgeRange(Age(int(x[0]), "month"), Age(int(x[1]), "year")),
    ),
    (
        re.compile(r"^(\d+)-(\d+) months?$"),
        lambda x: AgeRange(Age(int(x[0]), "month"), Age(int(x[1]) + 1, "month")),
    ),
    (
        re.compile(r"^(\d+)-<(\d+) months?$"),
        lambda x: AgeRange(Age(int(x[0]), "month"), Age(int(x[1]), "month")),
    ),
)


class ParseFailure:
    def __init__(self, string: str):
        self.string = string

    def __str__(self):
        return f"Failured to parse age range: '{self.string}'"


def parse_range(x: str) -> AgeRange | ParseFailure:
    """
    Parse an age range string

    Args:
        x: string

    Returns: an `AgeRange`, or a `ParseFailure`
    """
    for regex, value_fun in PARSERS:
        if match := regex.fullmatch(x):
            return value_fun(match.groups())

    return ParseFailure(x)


def tile(parts: Iterable[AgeRange], whole: AgeRange) -> bool:
    """
    Does a set of `AgeRange`s cover another `AgeRange`, with no gaps or overlap?

    Args:
        parts: member `AgeRange`s
        whole: larger `AgeRange`

    Returns: boolean
    """
    parts = sorted(parts, key=lambda x: x.lower)

    lower_match = parts[0].lower == whole.lower
    upper_match = parts[-1].upper == whole.upper
    middle_matches = [
        parts[i].upper == parts[i + 1].lower for i in range(len(parts) - 1)
    ]

    return lower_match and upper_match and all(middle_matches)
