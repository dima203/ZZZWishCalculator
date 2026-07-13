import pytest
from datetime import date, timedelta
from core.wish_calculator import ZZZGachaCalculator
from core.pull_calculator import ZZZPullCalculator, Currency, PullCalculationResult


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
        """Test that probability increases during soft pity (75-89)."""
        calc = ZZZGachaCalculator(current_pity=74)
        prob_75 = calc.probability_at_least_one(1)  # First pull at 75
        calc2 = ZZZGachaCalculator(current_pity=88)
        prob_89 = calc2.probability_at_least_one(1)  # First pull at 89
        assert prob_75 < prob_89

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
            start_date=start
        )
        assert calc.currency.pulls == 5
        assert calc.currency.polychromes == 1000
        assert calc.currency.monochromes == 50
        assert calc.currency.subscription_days == 15
        assert calc.days == 60
        assert calc.start_date == start

    def test_calculate_only_current_pulls(self):
        """Test calculation with only current pulls."""
        calc = ZZZPullCalculator(current_pulls=10, days=0)
        result = calc.calculate()
        assert result.total_pulls == 10
        assert result.from_current_pulls == 10
        assert result.from_current_polychromes == 0
        assert result.from_current_monochromes == 0

    def test_calculate_from_polychromes(self):
        """Test conversion of polychromes to pulls."""
        calc = ZZZPullCalculator(current_polychromes=320, days=0)  # 2 pulls
        result = calc.calculate()
        assert result.from_current_polychromes == 2
        assert result.total_pulls == 2

    def test_calculate_from_monochromes(self):
        """Test conversion of monochromes to pulls (1:1 with polychromes)."""
        calc = ZZZPullCalculator(current_monochromes=160, days=0)  # 1 pull
        result = calc.calculate()
        assert result.from_current_monochromes == 1
        assert result.total_pulls == 1

    def test_calculate_daily_tasks(self):
        """Test daily task polychrome income."""
        calc = ZZZPullCalculator(days=7)  # 7 days * 60 = 420 polychromes = 2 pulls
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

    def test_weekly_missions(self):
        """Test weekly mission income."""
        calc = ZZZPullCalculator(days=14)  # 2 weeks
        result = calc.calculate()
        assert result.from_weekly_missions == 5  # 2 * 420 / 160 = 5.25 -> 5

    def test_zero_hollow(self):
        """Test Zero Hollow income."""
        calc = ZZZPullCalculator(days=14)  # 2 weeks
        result = calc.calculate()
        assert result.from_zero_hollow == 2  # 2 * 160 / 160 = 2

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
            days=30
        )
        result = calc.calculate()
        # Total = current_pulls + (all_polychromes // 160) + monthly_shop
        # = 5 + (160+160+1800+2700+1680+640)//160 + 5
        # = 5 + 7140//160 + 5
        # = 5 + 44 + 5 = 54
        expected = 54
        assert result.total_pulls == expected

    def test_get_detailed_breakdown(self):
        """Test detailed breakdown dictionary."""
        calc = ZZZPullCalculator(current_pulls=5, days=0)
        breakdown = calc.get_detailed_breakdown()
        assert breakdown["Текущие крутки"] == 5
        assert breakdown["Итого круток"] == 5
        assert "Дней в расчёте" in breakdown

    def test_days_calculated_in_result(self):
        """Test days_calculated field in result."""
        calc = ZZZPullCalculator(days=45)
        result = calc.calculate()
        assert result.days_calculated == 45

    def test_total_polychromes_earned(self):
        """Test total polychromes earned calculation."""
        calc = ZZZPullCalculator(days=7)
        result = calc.calculate()
        # 7*60 (daily) + 0*90 (sub, default 0 days) + 1*420 (weekly) + 1*160 (zero)
        expected = 420 + 0 + 420 + 160
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
        calc = ZZZPullCalculator(
            current_pulls=5,
            current_polychromes=320,
            days=0
        )
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