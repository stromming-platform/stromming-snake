def fix_odd(x, y) -> tuple((int, int)):
    if x % 2 == 1:
        x = x + 1
    if y % 2 == 1:
        y = y + 1
    return x, y