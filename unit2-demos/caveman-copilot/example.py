def average(numbers):
    total = 0
    for n in numbers:
        total += n
    return total / len(numbers)


print(average([]))  # crashes: ask Copilot to explain and fix it
