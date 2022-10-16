def start():
    global step
    global sign
    global current_field
    step = 0
    sign = 'X'
    current_field = make_field()
    view_field(current_field)
    master(request())


def make_field():
    field = []
    for i in range(3):
        field.append([' '] * 3)
    return field


def view_field(field):
    i = ' \u2551 '
    print('    0   1   2')
    print('  \u2554' + '\u2550' * 3 + '\u2566' + '\u2550' * 3 + '\u2566' + '\u2550' * 3 + '\u2557')
    print('0' + i + field[0][0] + i + field[0][1] + i + field[0][2] + i)
    print('  \u2560' + '\u2550' * 3 + '\u256c' + '\u2550' * 3 + '\u256c' + '\u2550' * 3 + '\u2563')
    print('1' + i + field[1][0] + i + field[1][1] + i + field[1][2] + i)
    print('  \u2560' + '\u2550' * 3 + '\u256c' + '\u2550' * 3 + '\u256c' + '\u2550' * 3 + '\u2563')
    print('2' + i + field[2][0] + i + field[2][1] + i + field[2][2] + i)
    print('  \u255a' + '\u2550' * 3 + '\u2569' + '\u2550' * 3 + '\u2569' + '\u2550' * 3 + '\u255d')


def request():
    coordinate = input('Введите координаты клетки или соответствующюю кнопку на num-паде.')
    coordinate = coordinate.split(' ')
    if coordinate[0].isdigit() == 0 or len(coordinate) == 2 and coordinate[1].isdigit() == 0:
        print('Неверный формат ввода, вводите только цифры.')
        return request()
    if len(coordinate) > 2:
        print('Неверный формат ввода, введите заново. Введено слишком много значений')
        return request()
    if len(coordinate[0]) > 1 or len(coordinate) == 2 and len(coordinate[1]) > 1:
        print('Неверный формат ввода, введите заново. Значения превышают допустимые или в неверном формате.')
        return request()
    if len(coordinate) == 2:
        x = int(coordinate[0])
        y = int(coordinate[1])
        if x in (0, 1, 2) and y in (0, 1, 2) and current_field[x][y] == ' ':
            print(x, y)
            return x, y
        else:
            print('Неверный формат ввода, введите заново.')
            return request()
    else:
        coordinate[0] = int(coordinate[0])
        x = 2-(coordinate[0]-1) // 3
        y = ((coordinate[0])-1) % 3
        if x in (0, 1, 2) and y in (0, 1, 2) and current_field[x][y] == ' ':
            print(x, y)
            return [x, y]
        else:
            print('Неверный формат ввода, введите заново. 4')
            return request()


def master(cor):
    global step
    x = cor[0]
    y = cor[1]
    step += 1
    if step % 2 == 0:
        sign = 'X'
    else:
        sign = 'O'
    current_field[x][y] = sign
    view_field(current_field)
    if (current_field[x][0] == current_field[x][1] == current_field[x][2] or
        current_field[0][y] == current_field[1][y] == current_field[2][y] or
        x == y and current_field[0][0] == current_field[1][1] == current_field[2][2] or
        x+y == 2 and current_field[2][0] == current_field[1][1] == current_field[0][2]):
        print(f'Победил {sign}! Нажмите Enter, что бы начать заново.')
        input()
        start()
    elif step == 9:
        print('Ничья, не осталось возможных ходов. Что бы начать заново, нажмите Enter.')
        input()
        start()
    else:
        master(request())


start()
