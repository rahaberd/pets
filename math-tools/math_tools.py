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


def calc_combination_product():
    print("Enter combinations C(n, k) one per line (leave n blank to finish):")
    product = 1
    count = 0
    while True:
        n_input = input(f"  C{count + 1} - n (or blank to finish): ").strip()
        if not n_input:
            break
        k_input = input(f"  C{count + 1} - k: ").strip()
        try:
            n, k = int(n_input), int(k_input)
        except ValueError:
            print("Invalid input. Please enter integers.")
            continue
        if n < 0 or k < 0 or k > n:
            print("Invalid input. Please enter non-negative integers with k <= n.")
            continue
        product *= factorial(n) // (factorial(k) * factorial(n - k))
        count += 1
    if count == 0:
        print("No combinations entered.")
    else:
        print(product)


ACTIONS = {
    "1": calc_factorial,
    "2": calc_combination,
    "3": calc_permutations,
    "4": calc_combination_product,
}

MENU = """\
1. Factorial
2. Combination C(n, k)
3. Unique permutations of a word
4. Product of several combinations
5. Quit
"""

while True:
    print(MENU, end="")
    choice = input("Choose an option: ").strip()
    if choice == "5":
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
