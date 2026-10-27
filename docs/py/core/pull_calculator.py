from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class Currency:
    """Текущие ресурсы игрока."""

    pulls: int = 0
    polychromes: int = 0
    monochromes: int = 0
    subscription_days: int = 0


@dataclass
class PullCalculationResult:
    """Результат расчёта количества круток за период."""

    total_pulls: int
    total_pulls_min: int
    total_pulls_max: int
    from_current_pulls: int
    from_current_polychromes: int
    from_current_monochromes: int
    from_daily_tasks: int
    from_subscription: int
    from_monthly_shop: int
    from_ridu_weekly: int
    from_hollow_zero: int
    from_shiyu_defense: int
    from_deadly_assault: int
    from_subscription_polychromes: int
    total_polychromes_earned: int
    total_polychromes_earned_min: int
    total_monochromes_used: int
    days_calculated: int


class ZZZPullCalculator:
    """
    Калькулятор количества круток, которые можно получить за указанное время.

    Источники дохода:
    1. Ежедневные задания — 60 полихромов в день
    2. Подписка — 90 полихромов в день (учитывается оставшиеся дни подписки)
    3. Ridu Weekly — 60 полихромов в неделю
    4. Hollow Zero — 160 полихромов в неделю
    5. Shiyu Defense: Critical Node — до 780 полихромов за 14-дневную ротацию
    6. Deadly Assault — до 300 полихромов за 14-дневную ротацию
    7. Ежемесячный Signal Shop — 5 круток 1 числа (за Residual Signal)

    Shiyu Defense и Deadly Assault дают диапазон: нижняя граница — без эндгейма,
    верхняя — при полном клире обеих ротаций.

    Конвертация:
    - 1 крутка = 160 полихромов
    - 1 монохром = 1 полихром (1:1)
    """

    POLYCHROMES_PER_PULL: int = 160
    DAILY_TASK_POLYCHROMES: int = 60
    SUBSCRIPTION_POLYCHROMES_PER_DAY: int = 90
    MONTHLY_SHOP_PULLS: int = 5
    RIDU_WEEKLY_POLYCHROMES: int = 60
    HOLLOW_ZERO_POLYCHROMES: int = 160
    SHIYU_DEFENSE_POLYCHROMES: int = 780
    DEADLY_ASSAULT_POLYCHROMES: int = 300
    ENDGAME_ROTATION_DAYS: int = 14

    def __init__(
        self,
        current_pulls: int = 0,
        current_polychromes: int = 0,
        current_monochromes: int = 0,
        subscription_days: int = 0,
        days: int = 30,
        start_date: date | None = None,
    ) -> None:
        """
        :param current_pulls: Текущее количество круток
        :param current_polychromes: Текущее количество полихромов
        :param current_monochromes: Текущее количество монохромов
        :param subscription_days: Остаток дней подписки
        :param days: Количество дней для расчёта
        :param start_date: Дата начала расчёта (по умолчанию сегодня)
        """
        if current_pulls < 0:
            raise ValueError("current_pulls must be non-negative")
        if current_polychromes < 0:
            raise ValueError("current_polychromes must be non-negative")
        if current_monochromes < 0:
            raise ValueError("current_monochromes must be non-negative")
        if subscription_days < 0:
            raise ValueError("subscription_days must be non-negative")
        if days < 0:
            raise ValueError("days must be non-negative")

        self.currency: Currency = Currency(
            pulls=current_pulls,
            polychromes=current_polychromes,
            monochromes=current_monochromes,
            subscription_days=subscription_days,
        )
        self.start_date: date = start_date or date.today()
        self.days: int = days
        self.end_date: date = self.start_date + timedelta(days=days)

    def calculate(self) -> PullCalculationResult:
        """Рассчитывает общее количество круток за указанный период."""
        from_current_pulls = self.currency.pulls
        from_current_polychromes = self.currency.polychromes // self.POLYCHROMES_PER_PULL
        from_current_monochromes = self.currency.monochromes // self.POLYCHROMES_PER_PULL

        daily_task_polychromes = self.DAILY_TASK_POLYCHROMES * self.days

        subscription_days = min(self.currency.subscription_days, self.days)
        subscription_polychromes = self.SUBSCRIPTION_POLYCHROMES_PER_DAY * subscription_days

        weeks = self._count_weeks()
        rotations = self._count_endgame_rotations()
        ridu_weekly_polychromes = self.RIDU_WEEKLY_POLYCHROMES * weeks
        hollow_zero_polychromes = self.HOLLOW_ZERO_POLYCHROMES * weeks
        shiyu_defense_polychromes = self.SHIYU_DEFENSE_POLYCHROMES * rotations
        deadly_assault_polychromes = self.DEADLY_ASSAULT_POLYCHROMES * rotations

        monthly_shop_pulls = self._count_monthly_shop_pulls()

        base_polychromes_earned = (
            daily_task_polychromes + subscription_polychromes + ridu_weekly_polychromes + hollow_zero_polychromes
        )
        endgame_polychromes = shiyu_defense_polychromes + deadly_assault_polychromes
        total_polychromes_earned = base_polychromes_earned + endgame_polychromes

        max_polychromes_available = self.currency.polychromes + self.currency.monochromes + total_polychromes_earned
        min_polychromes_available = self.currency.polychromes + self.currency.monochromes + base_polychromes_earned

        max_pulls_from_polychromes = max_polychromes_available // self.POLYCHROMES_PER_PULL
        min_pulls_from_polychromes = min_polychromes_available // self.POLYCHROMES_PER_PULL

        total_pulls_min = from_current_pulls + min_pulls_from_polychromes + monthly_shop_pulls
        total_pulls_max = from_current_pulls + max_pulls_from_polychromes + monthly_shop_pulls

        return PullCalculationResult(
            total_pulls=total_pulls_max,
            total_pulls_min=total_pulls_min,
            total_pulls_max=total_pulls_max,
            from_current_pulls=from_current_pulls,
            from_current_polychromes=from_current_polychromes,
            from_current_monochromes=from_current_monochromes,
            from_daily_tasks=daily_task_polychromes // self.POLYCHROMES_PER_PULL,
            from_subscription=subscription_polychromes // self.POLYCHROMES_PER_PULL,
            from_monthly_shop=monthly_shop_pulls,
            from_ridu_weekly=ridu_weekly_polychromes // self.POLYCHROMES_PER_PULL,
            from_hollow_zero=hollow_zero_polychromes // self.POLYCHROMES_PER_PULL,
            from_shiyu_defense=shiyu_defense_polychromes // self.POLYCHROMES_PER_PULL,
            from_deadly_assault=deadly_assault_polychromes // self.POLYCHROMES_PER_PULL,
            from_subscription_polychromes=subscription_polychromes,
            total_polychromes_earned=total_polychromes_earned,
            total_polychromes_earned_min=base_polychromes_earned,
            total_monochromes_used=min(self.currency.monochromes, total_polychromes_earned + self.currency.polychromes),
            days_calculated=self.days,
        )

    def _count_weeks(self) -> int:
        """Подсчитывает количество полных недель в периоде."""
        return self.days // 7

    def _count_endgame_rotations(self) -> int:
        """Подсчитывает количество полных 14-дневных ротаций эндгейма."""
        return self.days // self.ENDGAME_ROTATION_DAYS

    def _count_monthly_shop_pulls(self) -> int:
        """Подсчитывает количество круток из ежемесячного магазина (1 число каждого месяца)."""
        pulls = 0
        current = self.start_date

        while current <= self.end_date:
            if current.day == 1:
                pulls += self.MONTHLY_SHOP_PULLS
            current += timedelta(days=1)

        return pulls

    def get_detailed_breakdown(self) -> dict[str, int]:
        """Возвращает подробную разбивку по источникам."""
        result = self.calculate()
        return {
            "Текущие крутки": result.from_current_pulls,
            "Из текущих полихромов": result.from_current_polychromes,
            "Из текущих монохромов": result.from_current_monochromes,
            "Ежедневные задания": result.from_daily_tasks,
            "Подписка": result.from_subscription,
            "Ridu Weekly": result.from_ridu_weekly,
            "Hollow Zero": result.from_hollow_zero,
            "Shiyu Defense (макс.)": result.from_shiyu_defense,
            "Deadly Assault (макс.)": result.from_deadly_assault,
            "Ежемесячный магазин": result.from_monthly_shop,
            "Итого полихромов заработано": result.total_polychromes_earned,
            "Итого полихромов без эндгейма": result.total_polychromes_earned_min,
            "Итого круток (мин.)": result.total_pulls_min,
            "Итого круток (макс.)": result.total_pulls_max,
            "Дней в расчёте": result.days_calculated,
        }
