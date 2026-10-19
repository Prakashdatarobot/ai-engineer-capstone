"""
CS50P Problem Set 2 - Loops
All five programs combined into one file.

Run:  python pset2_all.py
Then pick a program from the menu.

Note: for check50 / submit50, each program still needs to be in its own
file (camel.py, coke.py, twttr.py, plates.py, nutrition.py).
"""


# ---------------------------------------------------------------
# 1. camel.py - convert camelCase to snake_case
# ---------------------------------------------------------------
def camel():
    name = input("camelCase: ")
    print("snake_case: ", end="")
    for c in name:
        if c.isupper():
            print("_" + c.lower(), end="")
        else:
            print(c, end="")
    print()


# ---------------------------------------------------------------
# 2. coke.py - coin machine, 50 cents per bottle
# ---------------------------------------------------------------
def coke():
    amount_due = 50
    while amount_due > 0:
        print(f"Amount Due: {amount_due}")
        coin = int(input("Insert Coin: "))
        if coin in (25, 10, 5):
            amount_due -= coin
    print(f"Change Owed: {-amount_due}")


# ---------------------------------------------------------------
# 3. twttr.py - remove vowels
# ---------------------------------------------------------------
def shorten(word):
    result = ""
    for c in word:
        if c.lower() not in "aeiou":
            result += c
    return result


def twttr():
    text = input("Input: ")
    print("Output:", shorten(text))


# ---------------------------------------------------------------
# 4. plates.py - vanity plate validator
# ---------------------------------------------------------------
def is_valid(s):
    # 2 to 6 characters
    if len(s) < 2 or len(s) > 6:
        return False

    # must start with at least two letters
    if not s[:2].isalpha():
        return False

    # no periods, spaces, or punctuation
    if not s.isalnum():
        return False

    # numbers only at the end, and the first number can't be 0
    for i, char in enumerate(s):
        if char.isdigit():
            return char != "0" and s[i:].isdigit()

    return True


def plates():
    plate = input("Plate: ")
    if is_valid(plate):
        print("Valid")
    else:
        print("Invalid")


# ---------------------------------------------------------------
# 5. nutrition.py - calories in fruit (FDA poster)
# ---------------------------------------------------------------
FRUITS = {
    "apple": 130,
    "avocado": 50,
    "banana": 110,
    "cantaloupe": 50,
    "grapefruit": 60,
    "grapes": 90,
    "honeydew melon": 50,
    "kiwifruit": 90,
    "lemon": 15,
    "lime": 20,
    "nectarine": 60,
    "orange": 80,
    "peach": 60,
    "pear": 100,
    "pineapple": 50,
    "plums": 70,
    "strawberries": 50,
    "sweet cherries": 100,
    "tangerine": 50,
    "watermelon": 80,
}


def nutrition():
    item = input("Item: ").strip().lower()
    if item in FRUITS:
        print("Calories:", FRUITS[item])


# ---------------------------------------------------------------
# Menu
# ---------------------------------------------------------------
PROGRAMS = {
    "1": ("camel     - camelCase to snake_case", camel),
    "2": ("coke      - coin machine", coke),
    "3": ("twttr     - remove vowels", twttr),
    "4": ("plates    - vanity plate validator", plates),
    "5": ("nutrition - calories in fruit", nutrition),
}


def main():
    while True:
        print("\nCS50P Problem Set 2 - Loops")
        for key, (label, _) in PROGRAMS.items():
            print(f"  {key}. {label}")
        print("  q. quit")

        choice = input("Choose a program: ").strip().lower()
        if choice == "q":
            break
        if choice in PROGRAMS:
            PROGRAMS[choice][1]()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
