from datetime import date

import pytest

from core.pull_calculator import ZZZPullCalculator
from core.wish_calculator import ZZZGachaCalculator


class TestZZZGachaCalculator:
    """Tests for ZZZGachaCalculator - gacha probability calculations."""

    def test_init_valid_parameters(self):
        """Test initialization with valid parameters."""
        calc = ZZZGachaCalculator(current_pity=0, guarantee=False)
        assert calc.current_pity == 0
        assert calc.guarantee is False

    def test_init_with_guarantee(self):
        """Test initialization with guarantee active."""
        calc = ZZZGachaCalculator(current_pity=50, guarantee=True)
        assert calc.current_pity == 50
        assert calc.guarantee is True

    def test_init_invalid_pity_too_low(self):
        """Test initialization fails with negative pity."""
        with pytest.raises(ValueError, match="current_pity must be between 0 and 89"):
            ZZZGachaCalculator(current_pity=-1)

    def test_init_invalid_pity_too_high(self):
        """Test initialization fails with pity > 89."""
        with pytest.raises(ValueError, match="current_pity must be between 0 and 89"):
            ZZZGachaCalculator(current_pity=90)

    def test_probability_at_least_one_zero_pulls(self):
        """Test probability with 0 pulls is 0."""
        calc = ZZZGachaCalculator(current_pity=0)
        assert calc.probability_at_least_one(0) == 0.0

    def test_probability_at_least_one_at_pity_90(self):
        """Test probability at pity 89 with 1 pull is 50% (hard pity = guaranteed legendary, 50/50 for event)."""
        calc = ZZZGachaCalculator(current_pity=89)
        # Hard pity guarantees legendary (100%), but 50/50 for event character
        assert abs(calc.probability_at_least_one(1) - 0.5) < 1e-10

    def test_probability_at_least_one_with_guarantee(self):
        """Test probability with guarantee active."""
        calc = ZZZGachaCalculator(current_pity=0, guarantee=True)
        prob = calc.probability_at_least_one(1)
        assert abs(prob - 0.006) < 1e-10  # Base rate with guarantee

    def test_probability_at_least_one_increases_with_pulls(self):
        """Test probability increases with more pulls."""
        calc = ZZZGachaCalculator(current_pity=0)
        prob_10 = calc.probability_at_least_one(10)
        prob_50 = calc.probability_at_least_one(50)
        prob_90 = calc.probability_at_least_one(90)
        assert prob_10 < prob_50 < prob_90

    def test_probability_k_zero_event(self):
        """Test probability of exactly 0 event characters."""
        calc = ZZZGachaCalculator(current_pity=0)
        prob = calc.probability_k(10, 0)
        assert 0 <= prob <= 1

    def test_probability_k_invalid_k(self):
        """Test probability_k returns 0 for invalid k."""
        calc = ZZZGachaCalculator(current_pity=0)
        assert calc.probability_k(10, -1) == 0.0
        assert calc.probability_k(10, 11) == 0.0

    def test_get_distribution_sum_to_one(self):
        """Test that distribution sums to 1."""
        calc = ZZZGachaCalculator(current_pity=0)
        dist = calc.get_distribution(10)
        assert abs(sum(dist) - 1.0) < 1e-10

    def test_get_distribution_length(self):
        """Test distribution length is pulls + 1."""
        calc = ZZZGachaCalculator(current_pity=0)
        dist = calc.get_distribution(5)
        assert len(dist) == 6

    def test_soft_pity_increase(self):
        """Test that probability increases during soft pity (74-89)."""
        calc = ZZZGachaCalculator(current_pity=74)
        prob_75 = calc.probability_at_least_one(1)  # First pull at 75
        calc2 = ZZZGachaCalculator(current_pity=88)
        prob_89 = calc2.probability_at_least_one(1)  # First pull at 89
        assert prob_75 < prob_89

    def test_soft_pity_curve_starts_at_74(self):
        """Community-estimated ramp: 6.6% at 74, +6 p.p. per pull, 100% at 90."""
        calc = ZZZGachaCalculator(current_pity=0)
        assert calc.prob_legendary[73] == pytest.approx(0.006)
        assert calc.prob_legendary[74] == pytest.approx(0.066)
        assert calc.prob_legendary[75] == pytest.approx(0.126)
        assert calc.prob_legendary[89] == pytest.approx(0.966)
        assert calc.prob_legendary[90] == 1.0

    def test_soft_pity_first_pull_probability(self):
        """At pity 73 the 74th pull has 6.6% S-rank chance (3.3% for the featured agent)."""
        calc = ZZZGachaCalculator(current_pity=73)
        assert calc.probability_at_least_one(1) == pytest.approx(0.033)

    def test_hard_pity_at_90(self):
        """Test hard pity at 90 pulls guarantees legendary (50/50 for event)."""
        calc = ZZZGachaCalculator(current_pity=89)
        prob = calc.probability_at_least_one(1)
        assert abs(prob - 0.5) < 1e-10

    def test_50_50_without_guarantee(self):
        """Test 50/50 mechanic when no guarantee."""
        calc = ZZZGachaCalculator(current_pity=0, guarantee=False)
        # Probability of getting event char in 1 pull = 0.6% * 0.5 = 0.3%
        prob_event = calc.probability_k(1, 1)
        assert abs(prob_event - 0.003) < 1e-10

    def test_guarantee_after_non_event(self):
        """Test guarantee activates after non-event legendary."""
        calc = ZZZGachaCalculator(current_pity=0, guarantee=False)
        dist = calc.get_distribution(90)
        # With 90 pulls, should have some probability of getting event char
        # even after a non-event (guarantee kicks in)
        prob_at_least_one = 1 - dist[0]
        assert prob_at_least_one > 0.5  # Should be decent chance with 90 pulls


class TestWEngineBanner:
    """Tests for the W-Engine channel: 80 pity, 75/25 featured rate."""

    def test_spec_and_soft_pity(self):
        calc = ZZZGachaCalculator(banner="w_engine")
        assert calc.hard_pity == 80
        assert calc.featured_rate == pytest.approx(0.75)
        assert calc.prob_legendary[64] == pytest.approx(0.006)
        assert calc.prob_legendary[65] == pytest.approx(0.066)
        assert calc.prob_legendary[79] == pytest.approx(0.906)
        assert calc.prob_legendary[80] == 1.0

    def test_75_25_without_guarantee(self):
        calc = ZZZGachaCalculator(banner="w_engine")
        assert calc.probability_k(1, 1) == pytest.approx(0.0045)

    def test_hard_pity_featured_chance(self):
        calc = ZZZGachaCalculator(current_pity=79, banner="w_engine")
        assert calc.probability_k(1, 1) == pytest.approx(0.75)

    def test_guarantee_on_w_engine(self):
        calc = ZZZGachaCalculator(banner="w_engine", guarantee=True)
        assert calc.probability_k(1, 1) == pytest.approx(0.006)

    def test_pity_validation(self):
        with pytest.raises(ValueError, match="current_pity must be between 0 and 79"):
            ZZZGachaCalculator(current_pity=80, banner="w_engine")

    def test_unknown_banner(self):
        with pytest.raises(ValueError, match="unknown banner"):
            ZZZGachaCalculator(banner="bangboo")


class TestZZZPullCalculator:
    """Tests for ZZZPullCalculator - pull income calculations."""

    def test_init_defaults(self):
        """Test initialization with defaults."""
        calc = ZZZPullCalculator()
        assert calc.currency.pulls == 0
        assert calc.currency.polychromes == 0
        assert calc.currency.monochromes == 0
        assert calc.currency.subscription_days == 0
        assert calc.days == 30

    def test_init_with_values(self):
        """Test initialization with custom values."""
        start = date(2024, 1, 15)
        calc = ZZZPullCalculator(
            current_pulls=5,
            current_polychromes=1000,
            current_monochromes=50,
            subscription_days=15,
            days=60,
            start_date=start,
        )
        assert calc.currency.pulls == 5
        assert calc.currency.polychromes == 1000
        assert calc.currency.monochromes == 50
        assert calc.currency.subscription_days == 15
        assert calc.days == 60
        assert calc.start_date == start

    def test_calculate_only_current_pulls(self):
        """Test calculation with only current pulls."""
        calc = ZZZPullCalculator(current_pulls=10, days=0, start_date=date(2026, 1, 5))
        result = calc.calculate()
        assert result.total_pulls == 10
        assert result.from_current_pulls == 10
        assert result.from_current_polychromes == 0
        assert result.from_current_monochromes == 0

    def test_calculate_from_polychromes(self):
        """Test conversion of polychromes to pulls."""
        calc = ZZZPullCalculator(current_polychromes=320, days=0, start_date=date(2026, 1, 5))  # 2 pulls
        result = calc.calculate()
        assert result.from_current_polychromes == 2
        assert result.total_pulls == 2

    def test_calculate_from_monochromes(self):
        """Test conversion of monochromes to pulls (1:1 with polychromes)."""
        calc = ZZZPullCalculator(current_monochromes=160, days=0, start_date=date(2026, 1, 5))  # 1 pull
        result = calc.calculate()
        assert result.from_current_monochromes == 1
        assert result.total_pulls == 1

    def test_calculate_daily_tasks(self):
        """Test daily task polychrome income."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=7)  # 7 * 60 = 420 = 2 pulls
        result = calc.calculate()
        assert result.from_daily_tasks == 2

    def test_calculate_subscription(self):
        """Test subscription polychrome income."""
        calc = ZZZPullCalculator(subscription_days=10, days=30)
        result = calc.calculate()
        # 10 days * 90 = 900 polychromes = 5 pulls
        assert result.from_subscription == 5
        assert result.from_subscription_polychromes == 900

    def test_subscription_limited_by_days(self):
        """Test subscription limited by calculation period."""
        calc = ZZZPullCalculator(subscription_days=60, days=30)
        result = calc.calculate()
        # Only 30 days counted
        assert result.from_subscription_polychromes == 90 * 30

    def test_ridu_weekly(self):
        """Test Ridu Weekly income (60 polychromes per week)."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=21)
        result = calc.calculate()
        assert result.from_ridu_weekly == 1  # 3 * 60 / 160 = 1.125 -> 1

    def test_hollow_zero(self):
        """Test Hollow Zero income (160 polychromes per week)."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=14)
        result = calc.calculate()
        assert result.from_hollow_zero == 2  # 2 * 160 / 160 = 2

    def test_shiyu_defense(self):
        """Test Shiyu Defense Critical Node (780 polychromes per 14-day rotation)."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=28)
        result = calc.calculate()
        assert result.from_shiyu_defense == 9  # 2 * 780 / 160 = 9.75 -> 9

    def test_deadly_assault(self):
        """Test Deadly Assault (300 polychromes per 14-day rotation)."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=28)
        result = calc.calculate()
        assert result.from_deadly_assault == 3  # 2 * 300 / 160 = 3.75 -> 3

    def test_endgame_rotations_require_full_period(self):
        """Endgame income starts only after a complete 14-day rotation."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=13)
        result = calc.calculate()
        assert result.from_shiyu_defense == 0
        assert result.from_deadly_assault == 0

    def test_monthly_shop_pulls(self):
        """Test monthly shop pulls."""
        # Start on 1st of month, 30 days = covers 1st of next month too
        start = date(2024, 1, 1)
        calc = ZZZPullCalculator(start_date=start, days=35)
        result = calc.calculate()
        # Should get pulls for Jan 1 and Feb 1
        assert result.from_monthly_shop == 10  # 2 * 5

    def test_monthly_shop_single_month(self):
        """Test monthly shop within single month."""
        start = date(2024, 1, 15)
        calc = ZZZPullCalculator(start_date=start, days=30)
        result = calc.calculate()
        # Only Feb 1st falls in period
        assert result.from_monthly_shop == 5

    def test_total_pulls_calculation(self):
        """Test total pulls combines all sources correctly."""
        calc = ZZZPullCalculator(
            current_pulls=5,
            current_polychromes=160,
            current_monochromes=160,
            subscription_days=30,
            days=30,
            start_date=date(2026, 1, 5),
        )
        result = calc.calculate()
        # 30 daily (1800) + 30 subscription (2700) + 4 Ridu (240) + 4 Hollow (640)
        # + 2 Shiyu (1560) + 2 Deadly Assault (600) = 7540 earned.
        # Current: 5 pulls + (160+160+7540)//160 + 5 shop = 5 + 49 + 5 = 59.
        assert result.total_pulls_min == 45
        assert result.total_pulls_max == 59
        assert result.total_pulls == result.total_pulls_max

    def test_total_pulls_range_excludes_endgame(self):
        """The lower bound excludes Shiyu Defense and Deadly Assault."""
        calc = ZZZPullCalculator(days=14, start_date=date(2026, 1, 5))
        result = calc.calculate()
        # Base: daily 840 + Ridu 120 + Hollow 320 = 1280 -> 8 pulls.
        # Full: + Shiyu 780 + Deadly 300 = 2360 -> 14 pulls.
        assert (result.total_pulls_min, result.total_pulls_max) == (8, 14)

    def test_short_period_has_no_range(self):
        """Without a full 14-day rotation the range collapses."""
        calc = ZZZPullCalculator(days=13, start_date=date(2026, 1, 5))
        result = calc.calculate()
        assert result.total_pulls_min == result.total_pulls_max

    def test_get_detailed_breakdown(self):
        """Test detailed breakdown dictionary."""
        calc = ZZZPullCalculator(current_pulls=5, days=0, start_date=date(2026, 1, 5))
        breakdown = calc.get_detailed_breakdown()
        assert breakdown["Текущие крутки"] == 5
        assert breakdown["Итого круток (мин.)"] == 5
        assert breakdown["Итого круток (макс.)"] == 5
        assert "Ridu Weekly" in breakdown
        assert "Shiyu Defense (макс.)" in breakdown
        assert "Deadly Assault (макс.)" in breakdown
        assert "Итого круток (мин.)" in breakdown
        assert "Дней в расчёте" in breakdown

    def test_days_calculated_in_result(self):
        """Test days_calculated field in result."""
        calc = ZZZPullCalculator(days=45)
        result = calc.calculate()
        assert result.days_calculated == 45

    def test_total_polychromes_earned(self):
        """Test total polychromes earned calculation."""
        calc = ZZZPullCalculator(start_date=date(2026, 1, 5), days=7)
        result = calc.calculate()
        # 7*60 daily + 1*60 Ridu + 1*160 Hollow + no full endgame rotation
        expected = 420 + 60 + 160
        assert result.total_polychromes_earned == expected

    def test_total_monochromes_used(self):
        """Test total monochromes used calculation."""
        calc = ZZZPullCalculator(current_monochromes=1000, days=30)
        result = calc.calculate()
        # Should not use more monochromes than available
        assert result.total_monochromes_used <= 1000

    def test_negative_pulls_raises_error(self):
        """Test that negative current_pulls raises error."""
        with pytest.raises(ValueError):
            ZZZPullCalculator(current_pulls=-1)

    def test_negative_polychromes_raises_error(self):
        """Test that negative polychromes raises error."""
        with pytest.raises(ValueError):
            ZZZPullCalculator(current_polychromes=-1)

    def test_negative_monochromes_raises_error(self):
        """Test that negative monochromes raises error."""
        with pytest.raises(ValueError):
            ZZZPullCalculator(current_monochromes=-1)


class TestEdgeCases:
    """Edge case tests for both calculators."""

    def test_wish_calculator_max_pulls(self):
        """Test wish calculator with maximum pulls (90)."""
        calc = ZZZGachaCalculator(current_pity=0)
        dist = calc.get_distribution(90)
        assert len(dist) == 91
        assert sum(dist) == pytest.approx(1.0)

    def test_pull_calculator_zero_days(self):
        """Test pull calculator with zero days."""
        calc = ZZZPullCalculator(current_pulls=5, current_polychromes=320, days=0, start_date=date(2026, 1, 5))
        result = calc.calculate()
        assert result.total_pulls == 7  # 5 + 2
        assert result.days_calculated == 0

    def test_pull_calculator_leap_year_february(self):
        """Test monthly shop calculation across February in leap year."""
        start = date(2024, 1, 30)  # Leap year
        calc = ZZZPullCalculator(start_date=start, days=5)
        result = calc.calculate()
        # Should catch Feb 1
        assert result.from_monthly_shop == 5

    def test_wish_calculator_probability_bounds(self):
        """Test all probabilities are within [0, 1]."""
        calc = ZZZGachaCalculator(current_pity=50)
        for pulls in [1, 10, 50, 90]:
            prob = calc.probability_at_least_one(pulls)
            assert 0 <= prob <= 1

    def test_wish_calculator_distribution_non_negative(self):
        """Test all distribution values are non-negative."""
        calc = ZZZGachaCalculator(current_pity=0)
        dist = calc.get_distribution(50)
        for val in dist:
            assert val >= -1e-10  # Allow tiny floating point errors
