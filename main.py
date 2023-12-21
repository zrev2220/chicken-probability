import itertools
from collections import Counter

from tqdm import tqdm


def brute_force():
    dice = [1, 2, 3, 4, 5, 6]
    MIN_DICE = 4
    N_DICE = 8
    T3_DICE = max(0, N_DICE - 8)
    UNSAFE_FOX_COUNT = 3
    possibilities = itertools.product(dice, repeat=N_DICE)
    total_possibilities = 6**N_DICE

    safe_by_dice_count = Counter()
    with tqdm(total=total_possibilities) as progress_bar:
        for i, possibility in enumerate(possibilities):
            # for dice 0-3: 5-6 considered foxes
            # for dice 4-11: 6 considered fox
            def is_fox(i, value):
                return i < T3_DICE and value in (5, 6) or i >= T3_DICE and value == 6

            for n_dice in range(MIN_DICE, N_DICE + 1):
                n_foxes = sum(
                    i >= N_DICE - n_dice and is_fox(i, value)
                    for i, value in enumerate(possibility)
                )
                if n_foxes < UNSAFE_FOX_COUNT:
                    safe_by_dice_count[n_dice] += 1
            progress_bar.update(1)

    # print results
    for n_dice, safe_count in safe_by_dice_count.items():
        # handle double-counting for n_dice < 12
        deduped_count = safe_count // (6 ** (N_DICE - n_dice))
        sample_space = 6**n_dice
        print(
            f"{n_dice:2} dice: {deduped_count:10} safe rolls out of {sample_space:10}, "
            f"{deduped_count/sample_space*100:4.2f}% chance"
        )


def formula():
    pass


if __name__ == "__main__":
    brute_force()
