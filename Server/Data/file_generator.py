import os

PATH = r'Files'

allowed = {'B': 'bytes', 'KB': 'kilobyte', 'MB': 'megabyte', 'GB': 'gigabyte'}
values = {'bytes': 1, 'kilobyte': 1000}


def file_in_size(units, size):
    with open(os.path.join(PATH, str(size) + units + ".txt"), 'wb') as f:
        f.write(value_in_bytes(units, size) * b'0')


def value_in_bytes(unit, size):
    if unit in allowed:
        unit = allowed[unit]
    elif unit not in allowed.values():
        raise TypeError("Invalid unit")
    if unit in values:
        return values[unit] * size
    else:
        if 'giga' in unit:
            return 1000 * value_in_bytes(unit.replace('giga', 'mega'), size)
        elif 'mega' in unit:
            return 1000 * value_in_bytes(unit.replace('mega', 'kilo'), size)
        elif 'kilo' in unit:
            return 1000 * value_in_bytes(unit.replace('kilo', 'byte'), size)


def make_all(sizes: list, exclude=('GB',)):
    for size in sizes:
        for unit in allowed:
            if unit not in exclude:
                file_in_size(unit, size)


def single():
    print("Units:",  allowed)
    units = input("Enter units:")
    if units in allowed:
        units = allowed[units]
    elif units.lower() not in allowed.values():
        print("Unknown unit try again")
        return
    try:
        size = int(input("How many " + units + " you want the file to be? "))
    except ValueError:
        print("Size must be int")
        return
    print(size, ' ', units, ' is ', value_in_bytes(units, size), ' bytes')
    file_in_size(units, size)


def auto_all():
    try:
        sizes = [int(x) for x in input("Enter values to create files: ").split(' ')]
    except ValueError:
        print("Error converting string to int")
        return
    make_all(sizes)


if __name__ == '__main__':
    #single()
    auto_all()
