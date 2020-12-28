import random

import colorama


def print(txt):
    codes = vars(colorama.Fore)
    colors = [codes[color] for color in codes if color not in ['BLACK', 'WHITE', 'RESET']]
    color_txt = [random.choice(colors) + char for char in txt]
    print(''.join(color_txt))