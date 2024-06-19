from random import randint
import requests
import telebot
from config import token

bot = telebot.TeleBot(token)

class Pokemon:
    pokemons = {}

    def __init__(self, pokemon_trainer):
        self.pokemon_trainer = pokemon_trainer
        self.pokemon_number = randint(1, 1000)
        self.name, self.img, self.abilities, self.level, self.height, self.health , self.slot = self.get_pokemon_data()
        Pokemon.pokemons[pokemon_trainer] = self

    def get_pokemon_data(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            name = data['forms'][0]['name']
            img = data['sprites']['front_default']
            abilities = [ability['ability']['name'] for ability in data['abilities']]
            level = data['base_experience']
            height = data["height"]
            slot = max([ability["slot"] for ability in data['abilities']])
            health = randint(50, 100)
            return name, img, abilities, level, height, health , slot
        else:
            return "Pikachu", "https://via.placeholder.com/150", [], 1, 0, 100

    def info(self):
        return f"Имя твоего покемона: {self.name}, Слот : {self.slot}  ,  Здоровье: {self.health} , базовый опыт: {self.level}, высота: {self.height}, Способности: {', '.join(self.abilities) }"

    def show_img(self):
        return self.img


@bot.message_handler(commands=['go'])
def go(message):
    if message.from_user.username not in Pokemon.pokemons.keys():
        pokemon = Pokemon(message.from_user.username)
        bot.send_message(message.chat.id, pokemon.info())
        bot.send_photo(message.chat.id, pokemon.show_img())
    else:
        bot.reply_to(message, "Ты уже создал себе покемона")

bot.infinity_polling(none_stop=True)


