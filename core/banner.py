class BannerLogic:
    """Логика расчета шансов выпадения легендарного персонажа."""

    BASE_CHANCE = 0.006  # Базовый шанс 0.6%
    SOFT_PITY_START = 75  # Мягкий гарант начинается с 75-й крутки
    HARD_PITY = 90  # Жесткий гарант на 90-й крутке

    def calculate_chance(self, pity: int) -> float:
        """
        Рассчитать шанс выпадения легендарного персонажа.

        Args:
            pity: Количество круток подряд без получения легендарки.

        Returns:
            Шанс выпадения в процентах (от 0 до 1).
        """
        if pity < self.SOFT_PITY_START:
            # Базовый шанс для первых 74 круток
            return self.BASE_CHANCE
        elif pity == self.HARD_PITY:
            # Жесткий гарант на 90-й крутке - 100% шанс
            return 1.0
        else:
            # Мягкий гарант с 75 по 89 крутку
            # Формула: P = 0.2 + (pity - 75) * (1.0 - 0.2) / (90 - 75)
            soft_pity_chance = 0.2 + (pity - self.SOFT_PITY_START) * \
                               (1.0 - 0.2) / (self.HARD_PITY - self.SOFT_PITY_START)
            return soft_pity_chance
