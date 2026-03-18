from math import factorial
from collections import Counter


def calc_factorial():
    n = int(input("Enter a number: "))
    if n < 0:
        print("Factorial does not exist for negative numbers")
    else:
        print(factorial(n))


def calc_combination():
    n = int(input("Enter n: "))
    k = int(input("Enter k: "))
    if n < 0 or k < 0 or k > n:
        print("Invalid input. Please enter non-negative integers with k <= n.")
    else:
        print(factorial(n) // (factorial(k) * factorial(n - k)))


def calc_permutations():
    word = input("Enter a word: ").lower()
    if not word.isalpha():
        print("Please enter letters only.")
        return
    total = factorial(len(word))
    for count in Counter(word).values():
        total //= factorial(count)
    print(total)


ACTIONS = {
    "1": calc_factorial,
    "2": calc_combination,
    "3": calc_permutations,
}

MENU = """\
1. Factorial
2. Combination C(n, k)
3. Unique permutations of a word
4. Quit
"""

while True:
    print(MENU, end="")
    choice = input("Choose an option: ").strip()
    if choice == "4":
        break
    action = ACTIONS.get(choice)
    if action:
        try:
            action()
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    else:
        print("Invalid option.")
    print()
