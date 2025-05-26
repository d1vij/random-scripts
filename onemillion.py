from num2words import num2words
import asyncio

async def count_letters_and_word_count(string: str) -> tuple[int, int]:
    s = string.replace('-', '').strip()
    return (len(s.replace(' ', '')), s.count(' ') + 1)

async def chunk(start: int, end: int) -> tuple[int, int]:
    total_letter_count = 0
    total_words = 0

    for num in range(start, end + 1):
        v = await count_letters_and_word_count(num2words(num))
        total_letter_count += v[0]
        total_words += v[1]

    return (total_letter_count, total_words)

async def calculate(MAX: int, CHUNKS: int) -> tuple[int, ...]:
    CHUNK_RANGE = MAX // CHUNKS
    _remainder = MAX % CHUNKS
    _tasks = []

    start = 1
    while start <= MAX - _remainder:
        end = start + CHUNK_RANGE - 1
        _tasks.append(chunk(start, end))
        start = end + 1

    if _remainder:
        _tasks.append(chunk(start, MAX))

    final = await asyncio.gather(*_tasks)

    return tuple(map(sum, zip(*final)))  # (total_letters, total_words)

async def main() -> None:
    lc, wc = await calculate(99, 10)
    print(f"Letter count {lc}")
    print(f"Word count {wc}")

asyncio.run(main())
# well asynchronity doesnt provide any performance benefit here :(