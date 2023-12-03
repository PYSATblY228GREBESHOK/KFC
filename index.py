import sqlite3
import time

class User:
    def __init__(self, user_id, login, password, role):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.role = role

class KFCOrderSystem:
    def __init__(self):
        self.conn = sqlite3.connect('KFC_Orders.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.last_order_id = None

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                subcategory TEXT,
                item INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cancelled_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                user_id INTEGER,
                category TEXT,
                subcategory TEXT,
                item INTEGER DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )
        ''')

        self.conn.commit()

    def register_user(self, login, password, role='user'):
        try:
            self.cursor.execute("INSERT INTO users (login, password, role) VALUES (?, ?, ?)", (login, password, role))
            self.conn.commit()
            print('Регистрация прошла успешно!')
            time.sleep(1.5)
            print("Добро пожаловать в систему заказов KFC")
            return True
        except sqlite3.IntegrityError:
            print('Пользователь с таким логином уже существует')
            return False

    def authenticate_user(self, login, password):
        self.cursor.execute("SELECT id, login, password, role FROM users WHERE login = ? AND password = ?", (login, password))
        user_data = self.cursor.fetchone()
        return User(*user_data) if user_data else None

    def display_menu(self):
        while True:
            time.sleep(2)

            choice = int(input('''
                Вы можете выбрать что-то из этой категории:
                    1. Бургеры
                    2. Роллы
                    3. Сочная курица
                    4. Холодные напитки
                :'''))

            if 1 <= choice <= 4:
                category_map = {1: 'Бургеры', 2: 'Роллы', 3: 'Сочная курица', 4: 'Холодные напитки'}
                category = category_map[choice]

                print(f"Вы выбрали категорию '{category}' ")

                subcategory_map = {
                    1: 'Маэстро Бургер Чиз', 2: 'Биг Маэстро Бургер', 3: 'Шефбургер Де Люкс',
                    4: 'Мега Ролл', 5: 'Ростмастер', 6: 'Шефролл',
                    7: 'Терияки', 8: 'Острые крылышки', 9: 'Стрипсы',
                    10: 'Фанта', 11: 'Лимонад', 12: 'Вода'
                }

                choice2 = int(input(f"Выберите {category[:-1]}:\n"
                                    f"    1. {subcategory_map[choice * 3 - 2]}\n"
                                    f"    2. {subcategory_map[choice * 3 - 1]}\n"
                                    f"    3. {subcategory_map[choice * 3]}\n"
                                    f": "))

                self.process_order(category, subcategory_map[choice2])

            else:
                print("Введите цифру от 1 до 4")

            more = input("Что-то еще? (да/нет/отменить): ")

            if more.lower() == 'отменить':
                if self.last_order_id:
                    self.cancel_order(self.last_order_id)
                    self.last_order_id = None
                else:
                    print("Нет активных заказов для отмены.")
            elif more.lower() != 'да':
                break
            else:
                print("Окей... перенаправляю вас в меню заказов")
                time.sleep(3)

    def process_order(self, category, subcategory):
        try:
            self.cursor.execute("INSERT INTO orders (user_id, category, subcategory, item) VALUES (?, ?, ?, 1)",
                                (1, category, subcategory))
            self.conn.commit()
            self.last_order_id = self.cursor.lastrowid
            print(f"Спасибо за заказ. {subcategory} добавлен в корзину.")
        except Exception as e:
            print(f"Произошла ошибка при обработке заказа: {e}")

    def cancel_order(self, order_id):
        try:
            self.cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            order_data = self.cursor.fetchone()

            if order_data:
                self.cursor.execute("""
                    INSERT INTO cancelled_orders (order_id, user_id, category, subcategory, item)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_data[0], order_data[1], order_data[2], order_data[3], order_data[4]))

                self.cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
                self.conn.commit()
                print(f"Заказ {order_id} успешно отменен.")
            else:
                print(f"Заказ с ID {order_id} не найден.")

        except Exception as e:
            print(f"Произошла ошибка при отмене заказа: {e}")

    def close_connection(self):
        self.conn.close()

def user():
    if __name__ == "__main__":
        order_system = KFCOrderSystem()

        while True:
            print('''
                Выберите пункт меню:
                1. Вход
                2. Регистрация
                3. Выход
                ''')

            user_input = input()

            if user_input == '1':
                print('Введите логин: ')
                login = input()

                print('Введите пароль: ')
                password = input()

                print('Вы вошли в систему заказов KFC')
                time.sleep(1)
                order_system.display_menu()

            elif user_input == '2':
                print('Введите логин: ')
                login = input()

                print('Введите пароль: ')
                password = input()

                print('Повторите пароль: ')
                password_repeat = input()

                if password != password_repeat:
                    print('Пароли не совпадают!')
                else:
                    role = input('Введите роль (user/admin): ')
                    order_system.register_user(login, password, role)

            elif user_input == '3':
                print('До свидания, Спасибо за работу')
                order_system.close_connection()
                break

user()
