import itertools
import signal
from collections import Counter
from multiprocessing import Pool, current_process
from time import sleep

from tqdm import tqdm

DICE = (1, 2, 3, 4, 5, 6)
# TODO add a CLI lib and parametrize min & max dice
MIN_DICE = 4
MAX_DICE = 12
T3_DICE = max(0, MAX_DICE - 8)
UNSAFE_FOX_COUNT = 3


def brute_force_worker(*, fixed_dice: list[int] | None = None):
    current_worker = current_process()
    try:
        worker_index = current_worker._identity[0] - 1
    except IndexError:
        # IndexError will throw when not using multiprocessing
        worker_index = 0

    fixed_dice = fixed_dice or ()
    possibilities = itertools.product(DICE, repeat=MAX_DICE - len(fixed_dice))
    total_possibilities = 6 ** (MAX_DICE - len(fixed_dice))

    safe_by_dice_count = Counter()
    # TODO progress bars are kinda messy with multiprocessing
    with tqdm(
        total=total_possibilities, position=worker_index, desc=str(fixed_dice)
    ) as progress_bar:
        for i, possibility in enumerate(possibilities):
            # for dice 0-3: 5-6 considered foxes
            # for dice 4-11: 6 considered fox
            def is_fox(i, value):
                return i < T3_DICE and value in (5, 6) or i >= T3_DICE and value == 6

            for n_dice in range(MIN_DICE, MAX_DICE + 1):
                full_possibility = fixed_dice + possibility
                n_foxes = sum(
                    i >= MAX_DICE - n_dice and is_fox(i, value)
                    for i, value in enumerate(full_possibility)
                )
                if n_foxes < UNSAFE_FOX_COUNT:
                    safe_by_dice_count[n_dice] += 1
            progress_bar.update(1)
    return safe_by_dice_count


def brute_force(*, parallel=True):
    result_counter = Counter()

    if parallel:
        with Pool(
            processes=12,
            initializer=signal.signal,
            initargs=(signal.SIGINT, signal.SIG_IGN),
        ) as pool:
            try:
                permutations = list(itertools.product(DICE, repeat=2))
                results = [
                    pool.apply_async(
                        brute_force_worker, kwds={"fixed_dice": fixed_dice}
                    )
                    for fixed_dice in permutations
                ]
                while not all(result.ready() for result in results):
                    sleep(1)

                # get and combine results
                print("\n" * 20)
                for result in results:
                    result_counter += result.get()
            except KeyboardInterrupt:
                print("\n" * 20)
                print("KeyboardInterrupt detected, terminating early")
    else:
        result_counter = brute_force_worker()

    for n_dice, safe_count in result_counter.items():
        # handle double-counting for n_dice < 12
        deduped_count = safe_count // (6 ** (MAX_DICE - n_dice))
        sample_space = 6**n_dice
        print(
            f"{n_dice:2} dice: {deduped_count:10} safe rolls "
            f"out of {sample_space:10}, "
            f"{deduped_count/sample_space*100:4.2f}% chance"
        )


def formula():
    # TODO
    pass


if __name__ == "__main__":
    brute_force()
