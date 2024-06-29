import random
import requests
import time
from telebot import TeleBot, types
from config import token

bot = TeleBot(token)
admin_ids = [1845730851]  

trainers = {}

START = 0
FIGHT_MENU = 1
COOLDOWN_TIME = 1800
FIGHT_DATA = {}
current_turn = None


class Trainer:
    def __init__(self, username):
        self.username = username
        self.pokemons = []
        self.current_pokemon_index = 0
        self.experience = 0

    def add_pokemon(self, pokemon):
        self.pokemons.append(pokemon)

    def get_current_pokemon(self):
        if self.pokemons:
            return self.pokemons[self.current_pokemon_index]
        else:
            return None

    def switch_pokemon(self, index):
        if 0 <= index < len(self.pokemons):
            self.current_pokemon_index = index
            return True
        else:
            return False

    def gain_experience(self, amount):
        self.experience += amount
        for pokemon in self.pokemons:
            if self.experience >= pokemon.evolution_experience:
                pokemon.evolve()
                self.experience -= pokemon.evolution_experience
                bot.send_message(self.username, f"{pokemon.name} эволюционировал!")
                break


class Pokemon:
    def __init__(self, trainer, pokemon_type):
        self.trainer = trainer
        self.name = ""
        self.img = ""
        self.abilities = []
        self.level = 1
        self.height = 0
        self.health = 0
        self.max_health = 0
        self.slot = 0
        self.power = 0
        self.pokemon_type = pokemon_type
        self.shield = 0
        self.shield_cooldown = 5
        self.shield_used = 0
        self.last_heal_time = 0
        self.max_level = 5
        self.magic_ball_charge = 0
        self.crit_chance = 0
        self.stunned = False
        self.evolution_experience = 500
        self.name, self.img, self.abilities, self.level, self.height, self.health, self.max_health, self.slot, self.power, self.pokemon_type = self.get_pokemon_data()

    def get_pokemon_data(self):
        while True:
            pokemon_id = random.randint(1, 898)
            url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_id}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                name = data['forms'][0]['name']
                img = data['sprites']['front_default']
                abilities = [ability['ability']['name'] for ability in data['abilities']]
                level = data['base_experience']
                height = data["height"]
                slot = max([ability["slot"] for ability in data['abilities']])
                if self.pokemon_type == "Визерд":
                    health = random.randint(150, 800)
                    power = random.randint(20, 30)
                    abilities.append("Магический Щит")
                    self.shield = 200
                elif self.pokemon_type == "Боец":
                    health = random.randint(50, 500)
                    power = random.randint(30, 60)
                    abilities.append("Супер Удар")
                else:
                    health = random.randint(100, 700)
                    power = random.randint(5, 20)
                return name, img, abilities, level, height, health, health, slot, power, self.pokemon_type
            else:
                continue

    def info(self):
        return f"Имя: {self.name}, Тип: {self.pokemon_type}, Уровень: {self.level}, Здоровье: {self.health}/{self.max_health}, Сила: {self.power}, Способности: {', '.join(self.abilities)}, Опыт: {self.trainer.experience}/{self.evolution_experience}"

    def show_img(self):
        return self.img

    def attack(self, opponent):
        if "Супер Удар" in self.abilities and random.random() < 0.2:
            damage = max(1, self.power * 2 - opponent.power // 2)
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} получил супер удар! -{damage} ХП")
        elif "Магический Шар" in self.abilities and self.magic_ball_charge >= 2:
            damage = max(1, (self.power * 3) - opponent.power)
            self.magic_ball_charge = 0
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} получил Магический Шар! -{damage} ХП")
        else:
            damage = max(1, self.power - opponent.power // 2)
        if "Магический Щит" in self.abilities and self.shield_used < self.shield_cooldown:
            damage -= self.shield
            self.shield_used += 1
            bot.send_message(opponent.trainer.username, f"Твой {opponent.name} защищен Магическим Щитом! -{self.shield} урона")
        if random.random() < self.crit_chance:
            damage *= 2
            bot.send_message(opponent.trainer.username, f"Критический удар! +{damage} урона")
        opponent.health -= damage
        if opponent.health <= 0:
            opponent.stunned = True
            bot.send_message(opponent.trainer.username, f"{opponent.name} оглушен!")
        return damage

    def heal(self):
        cooldown_time = 1800
        if time.time() - self.last_heal_time >= cooldown_time:
            self.health = self.max_health
            self.last_heal_time = time.time()
            return True
        return False

    def evolve(self):
        if self.level < self.max_level:
            if self.pokemon_type == "Визерд":
                self.name = "магистр"
                self.img = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/133.png"
                self.abilities.append("Магический Шар")
                self.max_health = 1000
                self.power = 50
                self.evolution_experience = 2000
                self.max_level = 10
                self.shield = 300
                self.shield_cooldown = 5
            elif self.pokemon_type == "Боец":
                self.name = "гладиатор"
                self.img = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/150.png"
                self.abilities.append("Мощный Удар")
                self.max_health = 700
                self.power = 80
                self.evolution_experience = 2000
                self.max_level = 10
                self.crit_chance = 0.1
                self.health = self.max_health
                self.level = self.max_level
            return True
        return False

    def increase_stats(self):
        if self.level < self.max_level:
            self.max_health += 50
            self.power += 10
            self.health = self.max_health
            self.shield += 50
            self.shield_cooldown -= 1
            self.crit_chance += 0.05
            self.magic_ball_charge += 1
            self.level += 1

    def use_magic_ball(self):
        self.magic_ball_charge += 1
        if self.magic_ball_charge >= 2:
            bot.send_message(self.trainer.username, f"{self.name} готов к Магическому Шару! (Заряд: {self.magic_ball_charge}/2)")

    def stun_reset(self):
        self.stunned = False



class Wizerd(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Визерд")


class Boez(Pokemon):
    def __init__(self, trainer):
        super().__init__(trainer, "Боец")



def init_fight_data(username, opponent_username):
    trainer = trainers[username]
    opponent_trainer = trainers[opponent_username]
    my_pokemon = trainer.get_current_pokemon()
    opponent_pokemon = opponent_trainer.get_current_pokemon()
    FIGHT_DATA[username] = {
        'opponent_username': opponent_username,
        'my_pokemon': my_pokemon,
        'opponent_pokemon': opponent_pokemon,
        'round': 1
    }
    FIGHT_DATA[opponent_username] = {
        'opponent_username': username,
        'my_pokemon': opponent_pokemon,
        'opponent_pokemon': my_pokemon,
        'round': 1
    }
    global current_turn
    current_turn = username


@bot.message_handler(commands=['heal'])
def heal_pokemon(message):
    username = message.from_user.username
    trainer = trainers[username]
    if time.time() - trainer.get_current_pokemon().last_heal_time < COOLDOWN_TIME:
        remaining_time = COOLDOWN_TIME - (time.time() - trainer.get_current_pokemon().last_heal_time)
        minutes, seconds = divmod(int(remaining_time), 60)
        bot.send_message(message.chat.id, f"Подожди {minutes} минут {seconds} секунд, чтобы излечить покемона снова.")
        return
    if trainer.pokemons:
        for pokemon in trainer.pokemons:
            if pokemon.heal():
                bot.send_message(message.chat.id, f"{pokemon.name} излечен!")
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет покемонов.")


@bot.message_handler(commands=['show'])
def show_pokemons(message):
    username = message.from_user.username
    trainer = trainers[username]
    if trainer.pokemons:
        pokemon_list = "\n".join(f"{i+1}. {pokemon.name} - {pokemon.info()}" for i, pokemon in enumerate(trainer.pokemons))
        bot.send_message(message.chat.id, f"Твои покемоны:\n{pokemon_list}")
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет покемонов.")


@bot.message_handler(commands=['switch'])
def switch_pokemon(message):
    username = message.from_user.username
    trainer = trainers[username]
    if len(trainer.pokemons) > 1:
        try:
            index = int(message.text.split()[1]) - 1
            if trainer.switch_pokemon(index):
                bot.send_message(message.chat.id, f"Теперь твой атакующий покемон: {trainer.get_current_pokemon().name}")
            else:
                bot.send_message(message.chat.id, "Некорректный номер покемона.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Необходимо указать номер покемона.")
    else:
        bot.send_message(message.chat.id, "У тебя только один покемон.")

@bot.message_handler(commands=['go'])
def go(message):
    username = message.from_user.username
    if username in trainers:
        trainer = trainers[username]
        if len(trainer.pokemons) < 4:
            pokemon_type = random.randint(0, 1)
            if pokemon_type == 0:
                pokemon = Wizerd(trainer)
            else:
                pokemon = Boez(trainer)
            trainer.add_pokemon(pokemon)
            bot.send_message(message.chat.id, pokemon.info())
            bot.send_photo(message.chat.id, pokemon.show_img())
            bot.reply_to(message, f"Поздравляю, ты поймал {pokemon.name}!")
        else:
            bot.reply_to(message, "У тебя уже 4 покемона. Сначала поменяй их или выйди из игры.")
    else:
        bot.reply_to(message, "Сначала начни игру, используя /start")


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    if username in trainers:
        bot.send_message(message.chat.id, f"Привет, {username}! Ты уже в игре!")
    else:
        trainers[username] = Trainer(username)
        bot.send_message(message.chat.id, f"Привет, {username}! Добро пожаловать в мир покемонов!")
        bot.send_message(message.chat.id, "Начни игру, используя /go")


@bot.message_handler(commands=['evolve'])
def evolve_command(message):
    if message.from_user.id in admin_ids:
        try:
            username, pokemon_index = message.text.split()[1:]
            pokemon_index = int(pokemon_index) - 1
            if username in trainers and 0 <= pokemon_index < len(trainers[username].pokemons):
                pokemon = trainers[username].pokemons[pokemon_index]
                if pokemon.evolve():
                    bot.send_message(message.chat.id, f"{pokemon.name} эволюционировал!")
                else:
                    bot.send_message(message.chat.id, f"{pokemon.name} уже эволюционировал!")
                return
            else:
                bot.send_message(message.chat.id, "Пользователь или покемон не найдены.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте /evolve @username [номер покемона]")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на эту команду.")

@bot.message_handler(commands=['forcefight'])
def force_fight(message):
    if message.from_user.id in admin_ids:
        try:
            
            usernames = message.text.split()[1:]
            username = usernames[0]
            opponent_username = usernames[1] if len(usernames) > 1 else username

            if username in trainers and opponent_username in trainers:
                if len(trainers[opponent_username].pokemons) == 0:
                    bot.send_message(message.chat.id, f"У {opponent_username} нет покемонов.")
                    return
                init_fight_data(username, opponent_username)
                current_turn = username
                start_fight_round(username)

            else:
                bot.send_message(message.chat.id, "Один или оба пользователя не найдены.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Неверный формат команды. Используйте /forcefight @username [@opponent_username].")
    else:
        bot.send_message(message.chat.id, "У вас нет прав на эту команду.")

@bot.message_handler(func=lambda message: message.text.startswith('/fight'))
def fight(message):
    if message.from_user.username in trainers:
        my_trainer = trainers[message.from_user.username]
        if '@' in message.text:
            opponent_username = message.text.split('@')[1].strip()  
            if opponent_username in trainers:
                opponent_trainer = trainers[opponent_username]
                
              
                if message.from_user.username in FIGHT_DATA and FIGHT_DATA[message.from_user.username]['opponent_username'] == opponent_username:
                    bot.send_message(message.chat.id, "Бой уже в процессе!")
                    return
                
                if opponent_username in FIGHT_DATA and FIGHT_DATA[opponent_username]['opponent_username'] == message.from_user.username:
                    bot.send_message(message.chat.id, "Бой уже в процессе!")
                    return

               
                if len(trainers[opponent_username].pokemons) == 0:
                    bot.send_message(message.chat.id, f"У {opponent_username} нет покемонов.")
                    return
                init_fight_data(message.from_user.username, opponent_username)
                current_turn = message.from_user.username
                start_fight_round(message.from_user.username)

            else:
                bot.reply_to(message, "У этого пользователя нет покемона.")
        else:
            bot.reply_to(message, "Неверный формат команды. Используйте /fight @[username].")
    else:
        bot.reply_to(message, "Сначала создай покемона!")



def start_fight_round(username):
    global current_turn

    
    if username in FIGHT_DATA and FIGHT_DATA[username]['opponent_pokemon'].stunned:
        FIGHT_DATA[username]['opponent_pokemon'].stun_reset()

    
    if FIGHT_DATA[username]['my_pokemon'].stunned:
        bot.send_message(username, f"{FIGHT_DATA[username]['my_pokemon'].name} оглушен! Пропустите ход.")
        current_turn = FIGHT_DATA[username]['opponent_username']
        start_fight_round(current_turn)
        return

    bot.send_message(username, f"Раунд {FIGHT_DATA[username]['round']}")
    bot.send_message(username, f"Твой покемон: {FIGHT_DATA[username]['my_pokemon'].name}\nЗдоровье: {FIGHT_DATA[username]['my_pokemon'].health}/{FIGHT_DATA[username]['my_pokemon'].max_health}")
    bot.send_photo(username, FIGHT_DATA[username]['my_pokemon'].img)
    
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Атаковать"), types.KeyboardButton("Сменить"))
    
    msg = bot.send_message(username, "Выберите действие:", reply_markup=keyboard)
    bot.register_next_step_handler(msg, handle_fight_action, username)


def handle_fight_action(message, username):
    global current_turn

    if message.text == "Атаковать":
        my_pokemon = FIGHT_DATA[username]['my_pokemon']
        opponent_pokemon = FIGHT_DATA[username]['opponent_pokemon']
        my_damage = my_pokemon.attack(opponent_pokemon)

        if my_pokemon.heal():
            bot.send_message(username, f"{my_pokemon.name} вылечился до максимального здоровья!")

        bot.send_message(username, f"{my_pokemon.name} атаковал {opponent_pokemon.name} и нанес {my_damage} урона. У {opponent_pokemon.name} осталось {opponent_pokemon.health} ХП.")

        if opponent_pokemon.health <= 0:
            bot.send_message(username, f"{opponent_pokemon.name} был побежден!")
            bot.send_message(FIGHT_DATA[username]['opponent_username'], f"Твой {opponent_pokemon.name} был побежден!")
            winner_username = username
            end_fight(winner_username)
            return
            
        current_turn = FIGHT_DATA[username]['opponent_username']
        start_fight_round(current_turn)

    elif message.text == "Сменить":
        
        username = message.from_user.username
        trainer = trainers[username]
        if len(trainer.pokemons) > 1:
            bot.send_message(username, "У тебя есть следующие покемоны:\n" + "\n".join(f"{i+1}. {pokemon.name}" for i, pokemon in enumerate(trainer.pokemons)))
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            for i in range(len(trainer.pokemons)):
                keyboard.add(types.KeyboardButton(str(i+1)))
            msg = bot.send_message(username, "Выберите покемона для смены:", reply_markup=keyboard)
            bot.register_next_step_handler(msg, handle_switch_pokemon, username)
        else:
            bot.send_message(username, "У тебя только один покемон.")
            start_fight_round(username)


def handle_switch_pokemon(message, username):
    global current_turn
    try:
        index = int(message.text) - 1
        if 0 <= index < len(trainers[username].pokemons):
            trainers[username].switch_pokemon(index)
            bot.send_message(username, f"Теперь твой атакующий покемон: {trainers[username].get_current_pokemon().name}")

           
            FIGHT_DATA[username]['my_pokemon'] = trainers[username].get_current_pokemon()
            FIGHT_DATA[FIGHT_DATA[username]['opponent_username']]['opponent_pokemon'] = trainers[username].get_current_pokemon()

            start_fight_round(username)
        else:
            bot.send_message(username, "Некорректный номер покемона.")
            start_fight_round(username)
    except ValueError:
        bot.send_message(username, "Неверный формат команды. Введите номер покемона.")
        start_fight_round(username)



def end_fight(winner_username):
    global current_turn
    current_turn = None
    winner_trainer = trainers[winner_username]
    loser_username = FIGHT_DATA[winner_username]['opponent_username']
    loser_trainer = trainers[loser_username]

    winner_pokemon = FIGHT_DATA[winner_username]['my_pokemon']
    loser_pokemon = FIGHT_DATA[winner_username]['opponent_pokemon']

    
    experience_gain = 100 + winner_pokemon.level * 20
    winner_trainer.gain_experience(experience_gain)
    bot.send_message(winner_username, f"Ты получил {experience_gain} опыта!")

   
    del FIGHT_DATA[winner_username]
    del FIGHT_DATA[loser_username]

    bot.send_message(winner_username, f"Ты победил!")
    bot.send_message(loser_username, f"Ты проиграл!")


if __name__ == '__main__':
    bot.infinity_polling()

