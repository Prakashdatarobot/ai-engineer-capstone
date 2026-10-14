"""Day 1 exercises: triangle, rectangle, and 99 bottles of beer."""


def triangle(text, n):
    """Draw a triangle of height n using copies of text."""
    for i in range(n):
        print(text * (i + 1))


def rectangle(text, width, height):
    """Draw a rectangle of the given width and height using copies of text."""
    for _ in range(height):
        print(text * width)


def bottles(n):
    """Return the correct wording for n bottles."""
    if n == 0:
        return 'No more bottles'
    if n == 1:
        return '1 bottle'
    return f'{n} bottles'


def bottle_verse(n):
    """Print one verse of the bottles song."""
    print(f'{bottles(n)} of beer on the wall')
    print(f'{bottles(n)} of beer')
    print('Take one down, pass it around')
    print(f'{bottles(n - 1)} of beer on the wall')


if __name__ == '__main__':
    print('--- Triangle ---')
    triangle('L', 5)
    print()

    print('--- Rectangle ---')
    rectangle('H', 5, 4)
    print()

    print('--- 99 Bottles ---')
    for n in range(99, 0, -1):
        bottle_verse(n)
        print()
