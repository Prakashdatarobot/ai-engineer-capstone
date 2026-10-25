"""
CS50P Problem Set 0 - Functions and Variables
All five programs combined into one file.

Run:  python pset0_all.py
Then pick a program from the menu.

Note: for check50 / submit50, each program still needs to be in its own
file (indoor.py, playback.py, faces.py, einstein.py, tip.py).
"""


# ---------------------------------------------------------------
# 1. indoor.py - output the input in lowercase
# ---------------------------------------------------------------
def indoor():
    text = input("Enter your input: ").lower()
    print(text)


# ---------------------------------------------------------------
# 2. playback.py - replace each space with "..."
# ---------------------------------------------------------------
def playback():
    text = input("Enter your input: ").replace(" ", "...")
    print(text)


# ---------------------------------------------------------------
# 3. faces.py - convert :) and :( to emoji
# ---------------------------------------------------------------
def convert(text):
    return text.replace(":)", "🙂").replace(":(", "🙁")


def faces():
    text = input("Enter the string: ")
    print(convert(text))


# ---------------------------------------------------------------
# 4. einstein.py - E = mc^2
# ---------------------------------------------------------------
def einstein():
    m = int(input("Mass (kg): "))
    c = 300000000  # speed of light in m/s
    print(m * c ** 2)


# ---------------------------------------------------------------
# 5. tip.py - tip calculator
# ---------------------------------------------------------------
def dollars_to_float(d):
    return float(d.removeprefix("$"))


def percent_to_float(p):
    return float(p.removesuffix("%")) / 100


def tip():
    dollars = dollars_to_float(input("How much was the meal? "))
    percent = percent_to_float(input("What percentage would you like to tip? "))
    amount = dollars * percent
    print(f"Leave ${amount:.2f}")


# ---------------------------------------------------------------
# Menu
# ---------------------------------------------------------------
PROGRAMS = {
    "1": ("indoor   - lowercase the input", indoor),
    "2": ("playback - replace spaces with ...", playback),
    "3": ("faces    - convert :) and :( to emoji", faces),
    "4": ("einstein - mass to energy (E = mc^2)", einstein),
    "5": ("tip      - tip calculator", tip),
}


def main():
    while True:
        print("\nCS50P Problem Set 0")
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
