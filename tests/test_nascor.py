import pytest

from nascor import Age, AgeRange, ParseFailure, parse_range, tile


class TestAge:
    def test_trivial(self):
        assert Age(2, "week") == Age(2, "week")

    def test_comparable(self):
        assert Age(1, "year") == Age(12, "month")
        assert Age(0, "week") < Age(1, "year")

    def test_incomparable(self):
        with pytest.raises(ValueError):
            _ = Age(1, "year") < Age(52, "week")


class TestAgeRange:
    def test_equal(self):
        assert AgeRange(Age(0, "month"), Age(1, "year")) == AgeRange(
            Age(0, "week"), Age(12, "month")
        )

    def test_incomparable(self):
        with pytest.raises(ValueError):
            _ = AgeRange(Age(0, "year"), Age(1, "year")) == AgeRange(
                Age(0, "week"), Age(52, "week")
            )

    def test_age_group_is_in(self):
        assert AgeRange(Age(0, "month"), Age(1, "month")).is_in(
            AgeRange(Age(0, "year"), Age(1, "year"))
        )
        assert AgeRange(Age(0, "month"), Age(1, "month")).is_in(
            AgeRange(Age(0, "year"), None)
        )

    def test_one_year_into_months(self):
        assert AgeRange(Age(0, "year"), Age(1, "year")).subdivide(
            [Age(m, "month") for m in range(13)]
        ) == [AgeRange(Age(m, "month"), Age(m + 1, "month")) for m in range(12)]

    def test_years_into_months_and_years(self):
        # subdivide into months *and* years
        age_groups = AgeRange(Age(0, "year"), Age(4, "year")).subdivide(
            [Age(m, "month") for m in range(12)] + [Age(y, "year") for y in range(1, 5)]
        )
        # at first, it's month by month
        assert age_groups[0] == AgeRange(Age(0, "month"), Age(1, "month"))
        # then there's a transition, where we note 1 year = 12 months
        assert age_groups[-4] == AgeRange(Age(11, "month"), Age(1, "year"))
        assert age_groups[-4] == AgeRange(Age(11, "month"), Age(12, "month"))
        # and after that it's in years
        assert age_groups[-1] == AgeRange(Age(3, "year"), Age(4, "year"))


class TestParse:
    def test_years(self):
        assert parse_range("5 years") == AgeRange(Age(5, "year"), Age(6, "year"))

    def test_fail(self):
        assert isinstance(parse_range("foo"), ParseFailure)


class TestTile:
    def test_example(self):
        assert tile(
            [
                AgeRange(Age(0, "year"), Age(1, "year")),
                AgeRange(Age(1, "year"), Age(2, "year")),
                AgeRange(Age(2, "year"), Age(3, "year")),
            ],
            AgeRange(Age(0, "year"), Age(3, "year")),
        )

    def test_fail_on_overlap(self):
        assert not tile(
            [
                # 0-2 overlaps with 1-2
                AgeRange(Age(0, "year"), Age(2, "year")),
                AgeRange(Age(1, "year"), Age(2, "year")),
                AgeRange(Age(2, "year"), Age(3, "year")),
            ],
            AgeRange(Age(0, "year"), Age(3, "year")),
        )

    def test_fail_on_gap(self):
        assert not tile(
            [
                AgeRange(Age(0, "year"), Age(1, "year")),
                # missing 1-2
                AgeRange(Age(2, "year"), Age(3, "year")),
            ],
            AgeRange(Age(0, "year"), Age(3, "year")),
        )
