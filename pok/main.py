from random import randint

import telebot
from config import token
from logic import Pokemon , Wizerd , Boez
bot = telebot.TeleBot(token)



bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.username in trainers:
        trainer = trainers[message.from_user.username]
        pokemon_type = randint(0, 1)
        if pokemon_type == 0:
            pokemon = Wizerd(message.from_user.username)
        else:
            pokemon = Boez(message.from_user.username)
        trainer.add_pokemon(pokemon)
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
        bot.reply_to(message, f"Поздравляю, ты поймал {pokemon.name}!")
    else:
        bot.reply_to(message, "Сначала начни игру, используя /start")

@bot.message_handler(commands=['fight'])
def fight(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        my_pokemon = Pokemon.pokemons[message.from_user.username]
        opponent_username = message.text.split('@')[1].strip()
        if opponent_username in Pokemon.pokemons.keys():
            opponent_pokemon = Pokemon.pokemons[opponent_username]
            my_damage = my_pokemon.attack(opponent_pokemon)

            if my_pokemon.heal():
                bot.reply_to(message, f"{my_pokemon.name} вылечился до максимального здоровья!")

            bot.reply_to(message, f"{my_pokemon.name} атаковал {opponent_pokemon.name} и нанес {my_damage} урона.")
            if opponent_pokemon.health <= 0:
                bot.reply_to(message, f"{opponent_pokemon.name} был побежден!")
        else:
            bot.reply_to(message, "У этого пользователя нет покемона.")
    else:
        bot.reply_to(message, "Сначала создай покемона!")

@bot.message_handler(commands=['heal'])
def heal(message):
    if message.from_user.username in Pokemon.pokemons.keys():
        my_pokemon = Pokemon.pokemons[message.from_user.username]
        if my_pokemon.heal():
            bot.reply_to(message, f"{my_pokemon.name} вылечился до максимального здоровья!")
        else:
            bot.reply_to(message, f"{my_pokemon.name} не может лечиться так часто.")
    else:
        bot.reply_to(message, "Сначала создай покемона!")

class Trainer:
    def __init__(self, username):
        self.username = username
        self.pokemons = []
        self.current_pokemon = None

    def add_pokemon(self, pokemon):
        self.pokemons.append(pokemon)
        if self.current_pokemon is None:
            self.current_pokemon = pokemon

    def switch_pokemon(self, index):
        if 0 <= index < len(self.pokemons):
            self.current_pokemon = self.pokemons[index]
            return True
        return False

    def get_current_pokemon(self):
        return self.current_pokemon

trainers = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.username not in trainers:
        trainers[message.from_user.username] = Trainer(message.from_user.username)
        bot.reply_to(message, "Добро пожаловать в мир покемонов! Используй /go чтобы создать своего первого покемона.")
    else:
        bot.reply_to(message, "Ты уже в игре!")

@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.username in trainers:
        trainer = trainers[message.from_user.username]
        if len(trainer.pokemons) < 4:
            pokemon_type = randint(0, 1)
            if pokemon_type == 0:
                pokemon = Wizerd(message.from_user.username)
            else:
                pokemon = Boez(message.from_user.username)
            trainer.add_pokemon(pokemon)
            bot.send_message(message.chat.id, pokemon.info())
            bot.send_photo(message.chat.id, pokemon.show_img())
            bot.reply_to(message, f"Поздравляю, ты поймал {pokemon.name}!")
        else:
            bot.reply_to(message, "У тебя уже 4 покемона. Сначала поменяй их или выйди из игры.")
    else:
        bot.reply_to(message, "Сначала начни игру, используя /start")

@bot.message_handler(commands=['switch'])
def switch(message):
    if message.from_user.username in trainers:
        trainer = trainers[message.from_user.username]
        if len(trainer.pokemons) > 1:
            try:
                index = int(message.text.split()[1]) - 1
                if trainer.switch_pokemon(index):
                    bot.reply_to(message, f"Теперь твой активный покемон: {trainer.get_current_pokemon().name}")
                else:
                    bot.reply_to(message, "Некорректный номер покемона.")
            except (IndexError, ValueError):
                bot.reply_to(message, "Необходимо указать номер покемона.")
        else:
            bot.reply_to(message, "У тебя только один покемон.")
    else:
        bot.reply_to(message, "Сначала начни игру, используя /start")

@bot.message_handler(commands=['fight'])
def fight(message):
    if message.from_user.username in trainers:
        my_trainer = trainers[message.from_user.username]
        if '@' in message.text:
            opponent_username = message.text.split('@')[1].strip()  
            if opponent_username in trainers:
                opponent_trainer = trainers[opponent_username]
                my_pokemon = my_trainer.get_current_pokemon()
                opponent_pokemon = opponent_trainer.get_current_pokemon()
                my_damage = my_pokemon.attack(opponent_pokemon)

                if my_pokemon.heal():
                    bot.reply_to(message, f"{my_pokemon.name} вылечился до максимального здоровья!")

                bot.reply_to(message, f"{my_pokemon.name} атаковал {opponent_pokemon.name} и нанес {my_damage} урона.")
                if opponent_pokemon.health <= 0:
                    bot.reply_to(message, f"{opponent_pokemon.name} был побежден!")
            else:
                bot.reply_to(message, "У этого пользователя нет покемона.")
        else:
            bot.reply_to(message, "Неверный формат команды. Используйте /fight @[username].")
    else:
        bot.reply_to(message, "Сначала создай покемона!")

bot.polling()