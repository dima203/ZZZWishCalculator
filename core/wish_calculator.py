from typing import Final


class ZZZGachaCalculator:
    """
    Калькулятор вероятностей для баннера ивентового персонажа в ZZZ.
    Механика:
      - базовый шанс 0.6% до 74-й крутки;
      - с 75-й крутки шанс линейно растёт от 20% до 100% на 90-й;
      - при выпадении легендарного действует правило 50/50 (если нет гаранта);
      - гарант на ивентового включается после не-ивентового легендарного.
    """

    prob_legendary: Final[list[float]]

    def __init__(self, current_pity: int = 0, guarantee: bool = False) -> None:
        """
        :param current_pity: сколько круток уже сделано после последнего легендарного (0..89)
        :param guarantee: True, если следующий легендарный гарантированно будет ивентовым
        """
        if not (0 <= current_pity <= 89):
            raise ValueError("current_pity must be between 0 and 89")
        self.current_pity: int = current_pity
        self.guarantee: bool = guarantee

        self.prob_legendary = [0.0] * 91
        base: float = 0.006
        for i in range(1, 75):
            self.prob_legendary[i] = base
        for i in range(75, 90):
            self.prob_legendary[i] = 0.2 + (i - 75) * (0.8 / 15)
        self.prob_legendary[90] = 1.0

    def _compute_distribution(self, pulls: int) -> list[float]:
        """
        Возвращает массив prob[k] — вероятность получить ровно k ивентовых
        за 'pulls' круток, начиная с текущего состояния.
        Длина массива = pulls + 1.
        """
        if pulls < 0:
            raise ValueError("pulls must be non-negative")

        # Состояние: (pity, guarantee) -> массив вероятностей по k (длина pulls+1)
        # pity — текущий счётчик до легендарного (0..89)
        # guarantee — bool
        init_arr: list[float] = [0.0] * (pulls + 1)
        init_arr[0] = 1.0
        states: dict[tuple[int, bool], list[float]] = {(self.current_pity, self.guarantee): init_arr}

        for step in range(pulls):
            new_states: dict[tuple[int, bool], list[float]] = {}
            for (pity, guar), prob_arr in states.items():
                p_leg = self.prob_legendary[pity + 1]
                p_no = 1.0 - p_leg

                if p_no > 0:
                    new_pity = pity + 1
                    new_guar = guar
                    self._add_transition(new_states, (new_pity, new_guar), prob_arr, p_no, shift=0)

                if p_leg > 0:
                    if guar:
                        self._add_transition(new_states, (0, False), prob_arr, p_leg, shift=1)
                    else:
                        prob_event = p_leg * 0.5
                        prob_non_event = p_leg * 0.5
                        self._add_transition(new_states, (0, False), prob_arr, prob_event, shift=1)
                        self._add_transition(new_states, (0, True), prob_arr, prob_non_event, shift=0)

            states = new_states

        result: list[float] = [0.0] * (pulls + 1)
        for arr in states.values():
            for k, val in enumerate(arr):
                result[k] += val
        return result

    @staticmethod
    def _add_transition(
            states: dict[tuple[int, bool], list[float]],
            key: tuple[int, bool],
            src_arr: list[float],
            prob: float,
            shift: int,
    ) -> None:
        """
        Добавляет вклад в состояние key: src_arr * prob, со сдвигом индекса k на shift.
        """
        if prob == 0.0:
            return
        if key not in states:
            states[key] = [0.0] * len(src_arr)
        dest = states[key]
        for k, val in enumerate(src_arr):
            if val == 0.0:
                continue
            dest_k = k + shift
            if dest_k < len(dest):
                dest[dest_k] += val * prob

    def probability_at_least_one(self, pulls: int) -> float:
        """Вероятность получить хотя бы одного ивентового легендарного за pulls круток."""
        dist = self._compute_distribution(pulls)
        return 1.0 - dist[0]

    def probability_k(self, pulls: int, k: int) -> float:
        """Вероятность получить ровно k ивентовых легендарных за pulls круток."""
        if k < 0 or k > pulls:
            return 0.0
        dist = self._compute_distribution(pulls)
        return sum(dist[k:]) if k < len(dist) else 0.0

    def get_distribution(self, pulls: int) -> list[float]:
        """Получить полное распределение вероятностей для k=0..pulls."""
        return self._compute_distribution(pulls)
