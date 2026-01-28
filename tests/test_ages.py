import pytest

from nascor import Age, AgeGroup


def test_trivial():
    assert Age(2, "week") == Age(2, "week")


def test_comparable():
    assert Age(1, "year") == Age(12, "month")


def test_incomparable():
    with pytest.raises(ValueError):
        _ = Age(1, "year") < Age(52, "week")


def test_age_group_is_in():
    assert AgeGroup(Age(0, "month"), Age(1, "month")).is_in(
        AgeGroup(Age(0, "year"), Age(1, "year"))
    )


class TestSubdivide:
    def test_one_year_into_months(self):
        assert AgeGroup(Age(0, "year"), Age(1, "year")).subdivide(
            [Age(m, "month") for m in range(13)]
        ) == [AgeGroup(Age(m, "month"), Age(m + 1, "month")) for m in range(12)]

    def test_years_into_months_and_years(self):
        # subdivide into months *and* years
        age_groups = AgeGroup(Age(0, "year"), Age(4, "year")).subdivide(
            [Age(m, "month") for m in range(12)] + [Age(y, "year") for y in range(1, 5)]
        )
        # at first, it's month by month
        assert age_groups[0] == AgeGroup(Age(0, "month"), Age(1, "month"))
        # then there's a transition, where we note 1 year = 12 months
        assert age_groups[-4] == AgeGroup(Age(11, "month"), Age(1, "year"))
        assert age_groups[-4] == AgeGroup(Age(11, "month"), Age(12, "month"))
        # and after that it's in years
        assert age_groups[-1] == AgeGroup(Age(3, "year"), Age(4, "year"))
