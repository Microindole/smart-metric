"""module docstring"""


def add(a, b):
    return a + b


def compute(values):
    total = 0
    for value in values:
        if value > 0:
            total = add(total, value)
        else:
            total = total - 1
    return total


class Demo:
    def run(self):
        items = [1, 2, 3, -1]
        # run with sample list
        print(compute(items))
