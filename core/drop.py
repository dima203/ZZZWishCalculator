import random


class Drop:
    pass


class Weapon(Drop):
    pass


class Character(Drop):
    pass


STANDARD = "STANDARD"
EVENT = "EVENT"


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
