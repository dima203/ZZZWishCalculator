#!/usr/bin/env python3
"""CLI-интерфейс для ZZZ Wish Calculator."""


def get_positive_integer(prompt: str) -> int:
    """
    Запросить у пользователя целое положительное число.

    Args:
        prompt: Сообщение для вывода пользователю.

    Returns:
        Целое положительное число.

    Raises:
        ValueError: Если пользователь ввел некорректные данные.
    """
    while True:
        user_input = input(prompt).strip()
        try:
            value = int(user_input)
            if value <= 0:
                print("❌ Пожалуйста, введите число больше 0.")
                continue
            return value
        except ValueError:
            print(f"❌ '{user_input}' — некорректный ввод. Введите целое число.")


def get_yes_no(prompt: str) -> bool:
    """
    Запросить у пользователя ответ 'да' или 'нет'.

    Args:
        prompt: Сообщение для вывода пользователю.

    Returns:
        True если пользователь ввёл 'да', False иначе.
    """
    valid_answers = {'да', 'yes', 'y'}
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in valid_answers:
            return True
        elif user_input not in {'нет', 'no', 'n'}:
            print(f"❌ '{user_input}' — некорректный ввод. Введите 'да' или 'нет'.")


def main():
    """Основная функция CLI-интерфейса."""

    # Заголовок
    print("--- ZZZ Wish Calculator ---\n")

    # Запрос данных у пользователя
    num_pulls = get_positive_integer("Введите количество круток для симуляции: ")
    current_pity = get_positive_integer("Введите текущий pity: ")
    last_was_standard_input = input("Был ли последний легендарный персонаж стандартным? (да/нет): ").strip().lower()

    # Преобразуем ответ пользователя в bool
    if last_was_standard_input in {'да', 'yes', 'y'}:
        last_was_standard = True
    else:
        last_was_standard = False

    print()  # Пустая строка для разделения ввода и вывода

    # Импортируем WishCalculator из core.wish
    from core.wish import WishCalculator

    # Создаем калькулятор с введенными данными
    calculator = WishCalculator(
        current_pity=current_pity,
        last_was_standard=last_was_standard
    )

    # Выполняем симуляцию
    probability = calculator.simulate_pulls(num_pulls=num_pulls)

    # Получаем текущее состояние
    summary = calculator.get_summary()

    # Выводим результат
    print("Результат:")
    print(f"Вероятность получения ивентового персонажа за {num_pulls} круток: "
          f"{probability:.4f} ({probability * 100:.2f}%)")
    print(f"Текущее состояние: pity={summary['pity']}, is_guaranteed_event={summary['is_guaranteed_event']}")


if __name__ == "__main__":
    main()
