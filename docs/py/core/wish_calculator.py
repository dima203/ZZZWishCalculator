from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class BannerSpec:
    """Параметры канала Signal Search."""

    key: str
    label: str
    hard_pity: int
    soft_pity_start: int
    featured_rate: float


BANNERS: Final[dict[str, BannerSpec]] = {
    "agent": BannerSpec(
        key="agent",
        label="Агент",
        hard_pity=90,
        soft_pity_start=74,
        featured_rate=0.5,
    ),
    "w_engine": BannerSpec(
        key="w_engine",
        label="W-Engine",
        hard_pity=80,
        soft_pity_start=65,
        featured_rate=0.75,
    ),
}


class ZZZGachaCalculator:
    """
    Калькулятор вероятностей для каналов агентов и W-Engine в ZZZ.
    Механика:
      - базовый шанс 0.6% до начала soft pity;
      - soft pity: +6 п.п. за крутку (оценка сообщества; точная кривая не раскрыта);
      - hard pity: 90 для агента, 80 для W-Engine;
      - featured rate: 50/50 для агента, 75/25 для W-Engine;
      - гарант на ивентовый включается после не-ивентового S-ранга.

    Официально HoYoverse публикует только базовую ставку и hard pity.
    """

    BASE_RATE: Final[float] = 0.006
    SOFT_PITY_STEP: Final[float] = 0.06

    prob_legendary: Final[list[float]]

    def __init__(self, current_pity: int = 0, guarantee: bool = False, banner: str = "agent") -> None:
        """
        :param current_pity: сколько круток уже сделано после последнего S-ранга
        :param guarantee: True, если следующий S-ранг гарантированно ивентовый
        :param banner: "agent" или "w_engine"
        """
        if banner not in BANNERS:
            raise ValueError(f"unknown banner: {banner}")

        self.spec: Final[BannerSpec] = BANNERS[banner]
        self.banner: Final[str] = banner
        self.hard_pity: Final[int] = self.spec.hard_pity
        self.soft_pity_start: Final[int] = self.spec.soft_pity_start
        self.featured_rate: Final[float] = self.spec.featured_rate

        if not (0 <= current_pity < self.hard_pity):
            raise ValueError(f"current_pity must be between 0 and {self.hard_pity - 1}")

        self.current_pity: int = current_pity
        self.guarantee: bool = guarantee

        self.prob_legendary = [0.0] * (self.hard_pity + 1)
        for i in range(1, self.soft_pity_start):
            self.prob_legendary[i] = self.BASE_RATE
        for i in range(self.soft_pity_start, self.hard_pity):
            self.prob_legendary[i] = self.BASE_RATE + (i - self.soft_pity_start + 1) * self.SOFT_PITY_STEP
        self.prob_legendary[self.hard_pity] = 1.0

    def _compute_distribution(self, pulls: int) -> list[float]:
        """
        Возвращает массив prob[k] — вероятность получить ровно k ивентовых
        за 'pulls' круток, начиная с текущего состояния.
        Длина массива = pulls + 1.
        """
        if pulls < 0:
            raise ValueError("pulls must be non-negative")

        # Состояние: (pity, guarantee) -> массив вероятностей по k (длина pulls+1)
        # pity — текущий счётчик до S-ранга (0..hard_pity-1)
        # guarantee — bool
        init_arr: list[float] = [0.0] * (pulls + 1)
        init_arr[0] = 1.0
        states: dict[tuple[int, bool], list[float]] = {(self.current_pity, self.guarantee): init_arr}

        for _ in range(pulls):
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
                        prob_event = p_leg * self.featured_rate
                        prob_non_event = p_leg * (1.0 - self.featured_rate)
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
        if prob <= 0.0:
            return
        if key not in states:
            states[key] = [0.0] * len(src_arr)
        dest = states[key]
        for k, val in enumerate(src_arr):
            if val <= 0.0:
                continue
            dest_k = k + shift
            if dest_k < len(dest):
                dest[dest_k] += val * prob

    def probability_at_least_one(self, pulls: int) -> float:
        """Вероятность получить хотя бы одного ивентового легендарного за pulls круток."""
        dist = self._compute_distribution(pulls)
        return 1.0 - dist[0]

    def probability_k(self, pulls: int, k: int) -> float:
        """Вероятность получить не менее k ивентовых легендарных за pulls круток."""
        if k < 0 or k > pulls:
            return 0.0
        dist = self._compute_distribution(pulls)
        return sum(dist[k:]) if k < len(dist) else 0.0

    def get_distribution(self, pulls: int) -> list[float]:
        """Получить полное распределение вероятностей для k=0..pulls."""
        return self._compute_distribution(pulls)
