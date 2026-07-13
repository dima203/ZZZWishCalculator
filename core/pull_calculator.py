from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass
class Currency:
    """Текущие ресурсы игрока."""
    pulls: int = 0           # Крутки
    polychromes: int = 0     # Полихромы
    monochromes: int = 0     # Монохромы
    subscription_days: int = 0  # Остаток дней подписки


@dataclass
class PullCalculationResult:
    """Результат расчёта количества круток за период."""
    total_pulls: int
    from_current_pulls: int
    from_current_polychromes: int
    from_current_monochromes: int
    from_daily_tasks: int
    from_subscription: int
    from_monthly_shop: int
    from_weekly_missions: int
    from_zero_hollow: int
    from_subscription_polychromes: int
    total_polychromes_earned: int
    total_monochromes_used: int
    days_calculated: int


class ZZZPullCalculator:
    """
    Калькулятор количества круток, которые можно получить за указанное время.
    
    Источники дохода:
    1. Ежедневные задания — 60 полихромов в день
    2. Подписка — 90 полихромов в день (учитывается оставшиеся дни подписки)
    3. Ежемесячный магазин — 5 круток 1 числа каждого месяца (бесконечная валюта)
    4. Еженедельные задания — 420 полихромов в неделю
    5. Нулевая каверна — 160 полихромов в неделю
    
    Конвертация:
    - 1 крутка = 160 полихромов
    - 1 монохром = 1 полихром (1:1)
    """

    POLYCHROMES_PER_PULL = 160
    DAILY_TASK_POLYCHROMES = 60
    SUBSCRIPTION_POLYCHROMES_PER_DAY = 90
    MONTHLY_SHOP_PULLS = 5
    WEEKLY_MISSION_POLYCHROMES = 420
    ZERO_HOLLOW_POLYCHROMES = 160

    def __init__(self, 
                 current_pulls: int = 0,
                 current_polychromes: int = 0,
                 current_monochromes: int = 0,
                 subscription_days: int = 0,
                 days: int = 30,
                 start_date: Optional[date] = None):
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
        
        self.currency = Currency(
            pulls=current_pulls,
            polychromes=current_polychromes,
            monochromes=current_monochromes,
            subscription_days=subscription_days
        )
        self.start_date = start_date or date.today()
        self.days = days
        self.end_date = self.start_date + timedelta(days=days)

    def calculate(self) -> PullCalculationResult:
        """Рассчитывает общее количество круток за указанный период."""
        # Крутки из текущих ресурсов
        from_current_pulls = self.currency.pulls
        from_current_polychromes = self.currency.polychromes // self.POLYCHROMES_PER_PULL
        from_current_monochromes = self.currency.monochromes // self.POLYCHROMES_PER_PULL

        # Полихромы от ежедневных заданий
        daily_task_polychromes = self.DAILY_TASK_POLYCHROMES * self.days

        # Полихромы от подписки (учитываем только оставшиеся дни подписки)
        subscription_days = min(self.currency.subscription_days, self.days)
        subscription_polychromes = self.SUBSCRIPTION_POLYCHROMES_PER_DAY * subscription_days

        # Полихромы от еженедельных заданий
        weeks = self._count_weeks()
        weekly_mission_polychromes = self.WEEKLY_MISSION_POLYCHROMES * weeks

        # Полихромы от нулевой каверны
        zero_hollow_polychromes = self.ZERO_HOLLOW_POLYCHROMES * weeks

        # Крутки из ежемесячного магазина (1 числа каждого месяца)
        monthly_shop_pulls = self._count_monthly_shop_pulls()

        # Общее количество полихромов, полученных за период
        total_polychromes_earned = (
            daily_task_polychromes +
            subscription_polychromes +
            weekly_mission_polychromes +
            zero_hollow_polychromes
        )

        # Все доступные полихромы (текущие + монохромы 1:1 + заработанные)
        total_polychromes_available = (
            self.currency.polychromes +
            self.currency.monochromes +
            total_polychromes_earned
        )

        # Общее количество круток из всех полихромов
        total_pulls_from_polychromes = total_polychromes_available // self.POLYCHROMES_PER_PULL

        # Итого круток
        total_pulls = (
            from_current_pulls +
            total_pulls_from_polychromes +
            monthly_shop_pulls
        )

        return PullCalculationResult(
            total_pulls=total_pulls,
            from_current_pulls=from_current_pulls,
            from_current_polychromes=from_current_polychromes,
            from_current_monochromes=from_current_monochromes,
            from_daily_tasks=daily_task_polychromes // self.POLYCHROMES_PER_PULL,
            from_subscription=subscription_polychromes // self.POLYCHROMES_PER_PULL,
            from_monthly_shop=monthly_shop_pulls,
            from_weekly_missions=weekly_mission_polychromes // self.POLYCHROMES_PER_PULL,
            from_zero_hollow=zero_hollow_polychromes // self.POLYCHROMES_PER_PULL,
            from_subscription_polychromes=subscription_polychromes,
            total_polychromes_earned=total_polychromes_earned,
            total_monochromes_used=min(self.currency.monochromes, total_polychromes_earned + self.currency.polychromes),
            days_calculated=self.days
        )

    def _count_weeks(self) -> int:
        """Подсчитывает количество полных недель в периоде."""
        return self.days // 7

    def _count_monthly_shop_pulls(self) -> int:
        """Подсчитывает количество круток из ежемесячного магазина (1 число каждого месяца)."""
        pulls = 0
        current = self.start_date
        
        # Проверяем каждое 1-е число месяца в периоде
        while current <= self.end_date:
            if current.day == 1:
                pulls += self.MONTHLY_SHOP_PULLS
            current += timedelta(days=1)
        
        return pulls

    def get_detailed_breakdown(self) -> dict:
        """Возвращает подробную разбивку по источникам."""
        result = self.calculate()
        return {
            "Текущие крутки": result.from_current_pulls,
            "Из текущих полихромов": result.from_current_polychromes,
            "Из текущих монохромов": result.from_current_monochromes,
            "Ежедневные задания": result.from_daily_tasks,
            "Подписка": result.from_subscription,
            "Ежемесячный магазин": result.from_monthly_shop,
            "Еженедельные задания": result.from_weekly_missions,
            "Нулевая каверна": result.from_zero_hollow,
            "Итого полихромов заработано": result.total_polychromes_earned,
            "Итого круток": result.total_pulls,
            "Дней в расчёте": result.days_calculated,
        }