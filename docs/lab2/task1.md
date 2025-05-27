# Ход работы

В каждом отдельном файле threads.py / processes.py / courutines.py примерно одна логика:
- считаем сумму от 1 до N числа через `sum(range(...))`
- диапазон внутри `range` делим на батчи и для каждого батча считаем все отдельно (в корутинах/потоках/процессах)
- в конце замеряем мета информацию о времени выполнении, количестве батчей и результате подсчета

## Потоки

```python
import threading
import time
import json


def range_sum(start: int, end: int, result: list[int], index: int) -> None:
    result[index] = sum(range(start, end))


def big_sum(start: int, end: int, batches: int, result: list[int]) -> None:
    threads: list[threading.Thread] = []
    steps_per_batch: int = (end - start) // batches

    for i, batch_start in enumerate(range(start, end, steps_per_batch)):
        batch_end: int = min(batch_start + steps_per_batch, end)
        thread: threading.Thread = threading.Thread(
            target=range_sum,
            args=(batch_start, batch_end, result, i)
        )
        threads.append(thread)
        thread.start()
        print(f"-- Batch {i} is started: summing from {batch_start} to {batch_end}")

    for i, thread in enumerate(threads):
        thread.join()
        print(f"-- Batch {i} is finished")


def test() -> None:
    test_batches: int = 5
    test_result_list: list[int] = [0] * (test_batches + 1)
    big_sum(1, 102, test_batches, test_result_list)

    total, expected = sum(test_result_list), sum(range(1, 102))
    assert total == expected, f"Expected {expected}, got {total}"


if __name__ == "__main__":
    test()

    start_sum, end_sum, batches = 1, 1_000_000_000, 100
    print(f"Starting sum from {start_sum} to {end_sum} in {batches} batches...")

    result_list: list[int] = [0] * batches
    start_time = time.time()
    big_sum(start_sum, end_sum + 1, batches, result_list)
    end_time = time.time()

    data: dict = {
        "batches": batches,
        "result": sum(result_list),
        "duration_seconds": end_time - start_time
    }

    with open("threads.json", "w") as f:
        json.dump(data, f, indent=2)
```

**Результат**

```json
{
  "batches": 100,
  "result": 500000000500000000,
  "duration_seconds": 7.881979942321777
}
```

## Процессы

```python
import multiprocessing
import time
import json
import os


def range_sum(args: tuple[int, int, int]) -> int:
    index, start, end = args
    print(f"-- Batch {index} started: summing from {start} to {end}")
    result = sum(range(start, end))
    print(f"-- Batch {index} finished")
    return result


def big_sum(start: int, end: int, batches: int) -> int:
    steps_per_batch = (end - start) // batches
    ranges = [
        (i // steps_per_batch, i, min(i + steps_per_batch, end))
        for i in range(start, end, steps_per_batch)
    ]

    with multiprocessing.Pool(processes=batches) as pool:
        results = pool.map(range_sum, ranges)

    return sum(results)


def test() -> None:
    test_batches = os.cpu_count()
    total, expected = big_sum(1, 102, test_batches), sum(range(1, 102))
    assert total == expected, f"Expected {expected}, got {total}"


if __name__ == "__main__":
    test()

    start_sum, end_sum = 1, 1_000_000_000
    batches = os.cpu_count()
    print(f"Starting sum from {start_sum} to {end_sum} in {batches} batches...")

    start_time = time.time()
    result: int = big_sum(start_sum, end_sum + 1, batches)
    end_time = time.time()

    data: dict = {
        "batches": batches,
        "result": result,
        "duration_seconds": end_time - start_time
    }

    with open("processes.json", "w") as f:
        json.dump(data, f, indent=2)
```

**Результат**

```json
{
  "batches": 8,
  "result": 500000000500000000,
  "duration_seconds": 1.4063470363616943
}
```

## Корутины

```python
import asyncio
import time
import json


async def range_sum(args: tuple[int, int, int]) -> int:
    index, start, end = args
    print(f"-- Batch {index} started: summing from {start} to {end}")
    result = sum(range(start, end))
    print(f"-- Batch {index} finished")
    return result


async def big_sum(start: int, end: int, batches: int) -> int:
    steps_per_batch = (end - start) // batches
    ranges = [
        (i // steps_per_batch, i, min(i + steps_per_batch, end))
        for i in range(start, end, steps_per_batch)
    ]

    results = await asyncio.gather(*(range_sum(args) for args in ranges))
    return sum(results)


def test() -> None:
    test_batches = 5
    total, expected = asyncio.run(big_sum(1, 102, test_batches)), sum(range(1, 102))
    assert total == expected, f"Expected {expected}, got {total}"


if __name__ == "__main__":
    test()

    start_sum, end_sum, batches = 1, 1_000_000_000, 20_000
    print(f"Starting threaded sum from {start_sum} to {end_sum} in {batches} batches...")

    start_time = time.time()
    result = asyncio.run(big_sum(start_sum, end_sum + 1, batches))
    end_time = time.time()

    data: dict = {
        "batches": batches,
        "result": result,
        "duration_seconds": end_time - start_time
    }

    with open("coroutines.json", "w") as f:
        json.dump(data, f, indent=2)
```

**Результат**

```json
{
  "batches": 20000,
  "result": 500000000500000000,
  "duration_seconds": 8.07617712020874
}
```

## Итого 

| Метод    | Батчи | Результат             | Время выполнения (с)       |
|----------|-------|-----------------------|-----------------------------|
| Корутины | 20000 | 500000000500000000    | 8.07617712020874            |
| Процессы | 8     | 500000000500000000    | 1.4063470363616943         |
| Потоки   | 100   | 500000000500000000    | 7.881979942321777           |

Использование процессов оказалось наиболее эффективным, обеспечивая результат за 1.41 секунды с минимальным количеством пакетов. Корутины показали наибольшее время выполнения 
при существенно большем количестве батчей => в первом случае мы делаем нагрузку на разные ядра системы, 
когда в случае с корутинами на одно ядро + выполняем нагрузку только в конкретный момент времени и в рамках
Python управления корутинами на уровне интерпретатора 