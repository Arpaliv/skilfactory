import sys
import time
from random import randint


class FieldException(Exception):
    pass


class GameException(Exception):
    pass


class Field:
    def __init__(self, n: int = 6, m: int = None):
        if not m:
            m = n
        self.line = n
        self.collum = m
        self.ships = []
        self.number_of_ships = 0
        self.dots = []
        for i in range(n):
            self.dots.append([])
            for j in range(m):
                self.dots[i].append(' ')

    def in_field(self, x: int, y: int):
        if x < 0 or x >= self.line or y < 0 or y >= self.collum:
            return False
        else:
            return True

    def __repr__(self):
        _a = '-' * self.line * 2 + '-\n'
        for i in range(self.line):
            for j in range(self.collum):
                _a = _a + '|' + self.dots[i][j]
            _a = _a + '|\n'
        _a = _a + '-' * self.line * 2 + '-'
        return _a

    def canit(self, x: int, y: int):
        if not self.in_field(x, y):
            return True
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if self.in_field(x + i, y + j):
                    if self.dots[x + i][y + j] != ' ':
                        return True
        return False

    def add_ship(self, ship):
        can = True
        for x in ship.dots:
            if self.canit(x[0], x[1]):
                raise FieldException
        if can:
            self.ships.append(ship)
            self.number_of_ships += 1
            for x in ship.dots:
                self.dots[x[0]][x[1]] = 'D'
            return True

    def shoot(self, x: int, y: int):
        resolt = 0
        if self.dots[x][y] == ' ':
            self.dots[x][y] = '.'
            resolt = 0
        if self.dots[x][y] == 'D':
            for boat in self.ships:
                if (x, y) in boat.dots:
                    boat.shoot()
                    if boat.health == 0:
                        self.number_of_ships -= 1
                        for dot in boat.dots:
                            for i in (-1, 0, 1):
                                for j in (-1, 0, 1):
                                    if self.in_field(dot[0] + i, dot[1] + j):
                                        if self.dots[dot[0] + i][dot[1] + j] == ' ':
                                            self.dots[dot[0] + i][dot[1] + j] = '.'
                        if self.number_of_ships == 0:
                            resolt += 1
                    resolt += 1
            self.dots[x][y] = '!'
            resolt += 1
        return resolt


class Ship:
    def __init__(self, lenth: int, start_x: int, start_y: int, is_vert: bool = 0):
        self.health = lenth
        self.lenth = lenth
        if is_vert:
            self.dots = [(start_x, start_y + a) for a in range(lenth)]
        else:
            self.dots = [(start_x + a, start_y) for a in range(lenth)]

    def shoot(self):
        self.health -= 1


class Player:
    def __init__(self, player_field, enemy_field):
        self.player_field: Field = player_field
        self.enemy_field: Field = enemy_field

    def ask(self):
        pass

    def move(self):
        try:
            answ = None
            while not answ:
                answ = self.ask()
            return self.enemy_field.shoot(answ[0], answ[1])
        except GameException:
            print('Произошла ошибка, программа была принудительно закрыта')
            sys.exit()


class User(Player):
    def ask(self):
        reqest = input('Введите координаты клетки через одинарный пробел.')
        Settings.filter(reqest)
        reqest = reqest.split(' ')
        for r in reqest:
            if not r.isdigit():
                print('Неверный формат ввода - водите только цифры.')
                return False
        if len(reqest) != 2:
            print('Неверный формат ввода - введите только две координаты.')
            return False
        reqest = [int(reqest[0]) - 1, int(reqest[1]) - 1]
        if not self.enemy_field.in_field(reqest[0], reqest[1]):
            print('Неверный формат ввода - введите коодинаты, входящие в плоскость поля.')
            return False
        x = int(reqest[0])
        y = int(reqest[1])
        if self.enemy_field.dots[x][y] == 'x' or self.enemy_field.dots[x][y] == '!':
            print('Неверный ввод - введите координаты пустой клетки.')
            return False
        return reqest


class Ai(Player):
    def ask(self):
        var = []
        b_var = []
# Осматриваем поле на предмет подранков. Особенно смотрим две подряд.
        if Settings.difficulties >= 2:
            for i in range(Settings.size):
                for j in range(Settings.size):
                    if self.enemy_field.dots[i][j] == ' ' or self.enemy_field.dots[i][j] == 'D':
                        for n in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            try:
                                if self.enemy_field.dots[i + n[0]][j + n[1]] == '!':
                                    var.append((i, j))
                                    if self.enemy_field.dots[i + n[0]][j + n[1]] == '1':
                                        b_var.append((i, j))
                            except IndexError:
                                pass
            if b_var:
                return b_var[randint(0, len(b_var) - 1)]
            if var:
                return var[randint(0, len(var) - 1)]
# Оцениваем точки на предмет расположения крупных кораблей.
# Алгоритм прост - берем поочередно точки на поле и смотрим, можно ли туда поставить корабль
# вправо или вниз. Если можно - добавляем всем клеткам веса. В конце ищем клетку с наибольшим весом
# и стреляем по ней.
        if Settings.difficulties >= 3:
            value = [0] * Settings.size ** 2
            lon = 1
            for x in self.enemy_field.ships:
                if x.health > 0 and x.lenth > lon:
                    lon = x.lenth
            for i in range(Settings.size):
                for j in range(Settings.size):
                    count = 0
                    for n in range(lon):
                        if self.enemy_field.in_field(i + n, j):
                            if self.enemy_field.dots[i + n][j] == ' ' or self.enemy_field.dots[i + n][j] == 'D':
                                count += 1
                    if count == lon:
                        for n in range(lon):
                            value[(i + n) * Settings.size + j] += 1
                    count = 0
                    for n in range(lon):
                        if self.enemy_field.in_field(i, j + n):
                            if self.enemy_field.dots[i][j + n] == ' ' or self.enemy_field.dots[i][j + n] == 'D':
                                count += 1
                    if count == lon:
                        for n in range(lon):
                            value[i * Settings.size + j + n] += 1
            mx = max(value)
            fin = []
            for i in range(value.count(mx)):
                fin.append(value.index(mx) + i)
                value.pop(value.index(mx))
            fin2 = []
            for i in fin:
                fin2.append([i // Settings.size, i % Settings.size])
            x = randint(0, len(fin2) - 1)
            return fin2[x]
# Просто бьет куда попало.
        reqest = ''
        while reqest == '' or reqest == '.' or reqest == '!':
            x = randint(0, self.enemy_field.line - 1)
            y = randint(0, self.enemy_field.collum - 1)
            reqest = self.enemy_field.dots[x][y]
        reqest = [x, y]
        return reqest

# Класс отвечающий за визуальное оформление.
# Чтобы было проще ориентироваться в написаном, псевдографика
# была переведена в пременные d (от Design) и индексом, в зависимости
# от расположения цифры нв нампаде с добавлением 5, если есть переход
# на вертикаль или горизонталь.
#
# И да, я в курсе, что PEP8 плохо относится к объявлению переменных
# на одной строке через ";", но в данном случае это позволяет улучшить читаемость кода.


class Design:
    d7 = '\u2554'; d8 = '\u2550'; d85 = '\u2566'; d9 = '\u2557'
    d4 = '\u2551'; d45 = '\u2560'; d5 = '\u256c'; d6 = d4; d65 = '\u2563'
    d1 = '\u255a'; d2 = d8; d25 = '\u2569'; d3 = '\u255d'

    def outline(self, message: str, weight: int = 126):
        text = message.split('\n')
        length = max(map(len, text)) + 4
        indent = round((weight - length) / 2)
        if indent <= 0:
            indent = None
        else:
            indent = ' ' * indent
        report = indent + self.d7 + self.d8 * (length - 2) + self.d9 + '\n'
        for line in text:
            report += indent + self.d4 + ' ' * round((length - len(line) - 2) / 2) + line + ' ' * round(
                (length - len(line) - 2) / 2) + self.d6 + '\n'
        report += indent + self.d1 + self.d2 * (length - 2) + self.d3
        return report

# Функция - заплатка, принимает значения от программы и
# переформатирует их пользователю. И да, заодно прикрывает корабли противника.

    def cell_value(self, cell: str, isuser: bool = 1):
        if cell == 'D':
            if isuser:
                return Settings.badge['si']
            else:
                return Settings.badge['bs']
        elif cell == ' ':
            return Settings.badge['bs']
        elif cell == '.':
            return Settings.badge['ms']
        elif cell == '!':
            return Settings.badge['sh']
        else:
            return '?'

# Что бы отобразить обе доски на одной горизонтали, я
# не придумал ничего лучшего, чем собирать строки по кусуам.
# Общая логика - отступ, доска игрока, два отступа, доска противника.

    def out_field_2(self, field_user: Field, field_enemy: Field):
        print(' ' * 24 + self.d7 + self.d8 * 14 + self.d9 + ' ' * 47 + self.d7 + self.d8 * 15 + self.d9)
        print(' ' * 24 + self.d4 + ' Доска игрока ' + self.d4 + ' ' * 47 + self.d4 + 'Вражеская доска' + self.d6)
        print(' ' * 24 + self.d1 + self.d8 * 14 + self.d3 + ' ' * 47 + self.d1 + self.d8 * 15 + self.d3)
        indent = round((63 - (field_user.line * 4 + 3)) / 2)
        if indent <= 0:
            indent = 1
            indent_10 = 0
        else:
            indent_10 = ' ' * (indent - 1)
            indent = ' ' * indent
        line: str = indent + ' ' * 4
        for i in range(field_user.collum):
            _a = str(i + 1)
            line += _a + str(' ' * (4 - len(_a)))
        line += indent * 2 + '   '
        for i in range(field_user.collum):
            _a = str(i + 1)
            line += _a + str(' ' * (4 - len(_a)))
        _a = self.d7 + self.d8 * 3 + (self.d85 + self.d8 * 3) * (field_user.collum - 1) + self.d9
        line += '\n' + indent + '  ' + _a + indent * 2 + '  ' + _a
        for i in range(field_user.line):
            _a = str(i + 1)
            if i < 9:
                line += '\n' + indent + _a + ' '
            else:
                line += '\n' + indent_10 + _a + ' '
            for j in range(field_user.collum):
                _a = self.cell_value(field_user.dots[i][j], 1)
                line += self.d4 + ' ' + _a + ' '
            if i < 9:
                line += self.d4 + indent * 2 + str(i + 1) + ' '
            else:
                line += self.d4 + indent + indent_10 + str(i + 1) + ' '
            for j in range(field_enemy.collum):
                _a = self.cell_value(field_enemy.dots[i][j], 0)
                line += self.d4 + ' ' + _a + ' '
            line += self.d4 + '\n' + indent + '  '
            if i < (field_user.line - 1):
                _a = self.d45 + self.d8 * 3 + (self.d5 + self.d8 * 3) * (field_user.collum - 1) + self.d65
                line += _a + indent * 2 + '  ' + _a
        _a = self.d1 + self.d2 * 3 + (self.d25 + self.d2 * 3) * (field_user.collum - 1) + self.d3
        line += _a + indent * 2 + '  ' + _a
        print(line)

# Настройки. Более-менее работают. Оформление на фоне игры - так себе.
# Сильно удручает метод преждевременного начала новой игры - я так и не
# сумел это сделать нормально через прерывание Game.loop. Как итог - такой вот костыль


class Settings:
    size = 6                                    # max = 14
    ship_lens = [3, 2, 2, 1, 1, 1, 1]
    difficulties = 3
    slp = 0.5
    badge: dict = {'si': '\u2589',
                   'sh': 'X',
                   'ms': 'T',
                   'bs': 'O'}

    @staticmethod
    def filter(text):
        if text == 's' or text == 'S' or text == 'ы' or text == 'Ы':
            Settings.setting_menu()
        if text == 'q' or text == 'Q' or text == 'й' or text == 'Й':
            sys.exit()
        if text == 'n' or text == 'N' or text == 'т' or text == 'Т':
            Game.start()

    @staticmethod
    def setting_menu():
        while True:
            print('\n\n\n\n\nВведите в консоль номер пункта меню\n1 Размер поля и количество кораблей'
                  '\n2 Вид значков на поле  \n3 Задержка времени после хода \n4 Сложность')
            i = input()
            if i == '1':
                print('\n\n\n\n\nВведите 1 для поля 6х6 и 2 для поля 10х10')
                i = input()
                if i == '1':
                    Settings.size = 6
                    Settings.ship_lens = [3, 2, 2, 1, 1, 1, 1]
                if i == '2':
                    Settings.size = 10
                    Settings.ship_lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
            elif i == '2':
                print('\n\n\n\n\nВведите номер строки с выбраным оформлением\n')
                print('1   \u2589XOT')
                print("2   \u2589X' '.")
                i = input()
                if i == '1':
                    Settings.badge['si'] = '\u2589'
                    Settings.badge['sh'] = 'X'
                    Settings.badge['ms'] = 'T'
                    Settings.badge['bs'] = 'O'
                if i == '2':
                    Settings.badge['si'] = '\u2589'
                    Settings.badge['sh'] = 'X'
                    Settings.badge['ms'] = '.'
                    Settings.badge['bs'] = ' '
            elif i == '3':
                print('\n\n\n\n\nВведите 1 Число от 0 до десяти сколько десятков милисекунд должна длится задержка.\n')
                i = input()
                if i.isdigit():
                    if 0 <= int(i) <= 10:
                        try:
                            Settings.slp = int(i) / 10
                        except ValueError:
                            pass
            elif i == '4':
                print('\n\n\n\n\nВведите номер уровня сложности\n1 Простейший\n2 Простой\n3 Средний\n')
                i = input()
                if i.isdigit():
                    if 0 < int(i) < 4:
                        Settings.difficulties = int(i)
            else:
                Game.start()


class Game:
    ng = False
    set = Settings()
    disign = Design()

    @staticmethod
    def greet():
        print(Game.disign.outline('Приветствуем вас \nв игре \nморской бой! '))
        print(Game.disign.outline('формат ввода: х у\n х - номер строки\nу - номер столбца'))
        print(Game.disign.outline('Для начала игры нажмите Enter.\nДля входа в настройки введите s.\nДля '
                                  'завершения игры введите q.\nДля начала новой игры введите n.'))

    def new_game(self):
        user_board = self.new_field()
        enemy_board = self.new_field()
        player = User(user_board, enemy_board)
        ai = Ai(enemy_board, user_board)
        self.loop(player, ai)

    @staticmethod
    def start():
        Game.greet()
        inp = input()
        Settings.filter(inp)
        Game.new_game(self=g)

    def loop(self, player, ai):
        turn = 0
        while True:
            self.disign.out_field_2(player.player_field, player.enemy_field)
            if turn % 2 == 0:
                print(self.disign.outline('Ходит игрок.'))
                resolt = player.move()
                if resolt == 3:
                    print(self.disign.outline('Поздравляю, вы победили! \nЧтобы начать новую игру\nнажмите Enter. '))
                    i = input()
                    Settings.filter(i)
                    break
                elif resolt == 1:
                    print(self.disign.outline('Попадание, корабль ранен.'))
                    turn -= 1
                elif resolt == 2:
                    print(self.disign.outline('Попадание, корабль уничтожен.'))
                    turn -= 1
            else:
                print(self.disign.outline('Ходит компьютер.'))
                resolt = ai.move()
                if resolt == 3:
                    print(self.disign.outline('К сожалению вы проиграли.\nЧтобы начать новую игру\nнажмите Enter. '))
                    input()
                    i = input()
                    Settings.filter(i)
                    break
                elif resolt == 1:
                    print(self.disign.outline('Попадание, ваш корабль ранен.'))
                    turn -= 1
                elif resolt == 2:
                    print(self.disign.outline('Попадание, ваш корабль уничтожен.'))
                    turn -= 1
            turn += 1
            time.sleep(Settings.slp)

    def rand_field(self):
        new_field = Field(Settings.size)
        attempt = 0
        for sl in Settings.ship_lens:
            while True:
                attempt += 1
                if attempt > 1000:
                    return None
                boat = Ship(sl, randint(0, new_field.line-1), randint(0, new_field.collum-1), randint(0, 1))
                try:
                    new_field.add_ship(boat)
                    break
                except FieldException:
                    pass
        return new_field

    def new_field(self):
        while True:
            field = self.rand_field()
            if field is not None:
                return field


g = Game()
g.start()
while True:
    g.new_game()
