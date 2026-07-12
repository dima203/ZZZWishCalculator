from dataclasses import dataclass
import random

from .drop import Drop, EVENT, STANDARD


@dataclass
class Wish:
    drop: Drop


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


class DropManager:
    """Менеджер для определения типа выпадающего персонажа."""

    def __init__(self, is_guaranteed_event: bool = False) -> None:
        self.is_guaranteed_event = is_guaranteed_event

    def get_character_type(self, is_guaranteed: bool) -> tuple[str, bool]:
        """
        Определяет тип персонажа и обновляет статус флага гарантии.

        Args:
            is_guaranteed: Текущее значение флага is_guaranteed_event.

        Returns:
            Кортеж (тип персонажа, новый статус флага is_guaranteed_event).
        """
        if is_guaranteed:
            # Если флаг гарантирован — выпадает ивентовый персонаж
            self.is_guaranteed_event = False
            return EVENT, False
        else:
            # С вероятностью 50% стандартный или ивентовый персонаж
            if random.random() < 0.5:
                # Выпал стандартный — флаг становится True
                return STANDARD, True
            else:
                # Выпал ивентовый — флаг остается False
                return EVENT, False


class WishCalculator:
    """Калькулятор для симуляции гача ZZZ."""

    def __init__(self, current_pity: int = 0, last_was_standard: bool = True) -> None:
        """
        Инициализация калькулятора.

        Args:
            current_pity: Текущее количество круток подряд без легендарки.
            last_was_standard: Был ли последний легендарный персонаж стандартным.
        """
        self.current_pity = current_pity
        self.last_was_standard = last_was_standard
        self.drop_manager = DropManager(is_guaranteed_event=False)

    def simulate_pulls(self, num_pulls: int, iterations: int = 100000) -> float:
        """
        Провести симуляцию методом Монте-Карло.

        Args:
            num_pulls: Количество круток в одной симуляции.
            iterations: Количество итераций симуляции (по умолчанию 100000).

        Returns:
            Вероятность получения ивентового персонажа (доля успешных симуляций).
        """
        successful_simulations = 0

        for _ in range(iterations):
            # Сбрасываем состояние для каждой симуляции
            pity = self.current_pity
            is_guaranteed_event = False
            got_event_character = False

            for pull_num in range(1, num_pulls + 1):
                # Рассчитываем шанс выпадения легендарки на текущей крутке
                chance = BannerLogic().calculate_chance(pity)

                # Генерируем случайное число для проверки шанса
                roll = random.random()

                if roll < chance:
                    # Выпал легендарный персонаж
                    is_guaranteed = False

                    # Определяем тип выпавшего персонажа через DropManager
                    character_type, new_is_guaranteed_event = self.drop_manager.get_character_type(
                        is_guaranteed
                    )

                    if character_type == EVENT:
                        got_event_character = True
                    else:
                        # Выпал стандартный — сбрасываем pity и обновляем флаг гарантии
                        pity = 0
                        is_guaranteed_event = new_is_guaranteed_event
                else:
                    # Не выпала легендарка, увеличиваем счетчик pity
                    pity += 1

            if got_event_character:
                successful_simulations += 1

        return successful_simulations / iterations

    def get_summary(self) -> dict:
        """
        Возвращает текущее состояние калькулятора.

        Returns:
            Словарь с состоянием (pity, is_guaranteed_event).
        """
        return {
            "pity": self.current_pity,
            "is_guaranteed_event": self.drop_manager.is_guaranteed_event
        }


# Пример использования
if __name__ == "__main__":
    # Создаем калькулятор с начальным pity = 0 и последним стандартным персонажем
    calculator = WishCalculator(current_pity=0, last_was_standard=True)

    # Симулируем 10 круток на 100000 итерациях
    probability = calculator.simulate_pulls(num_pulls=10, iterations=100000)
    print(f"Вероятность получения ивентового персонажа за 10 круток: {probability:.4f} ({probability*100:.2f}%)")

    # Получаем текущее состояние
    summary = calculator.get_summary()
    print(f"Текущее состояние: pity={summary['pity']}, is_guaranteed_event={summary['is_guaranteed_event']}")
