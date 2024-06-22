from random import randint
import requests
import telebot
from config import token
import time

class Pokemon:
    pokemons = {}
    cooldown_time = 1800

    def __init__(self, pokemon_trainer, pokemon_type):
        self.pokemon_trainer = pokemon_trainer
        self.pokemon_number = randint(1, 1000)
        self.name, self.img, self.abilities, self.level, self.height, self.health, self.max_health, self.slot, self.power, self.pokemon_type = self.get_pokemon_data(pokemon_type)
        self.shield = 200
        self.shield_cooldown = 10
        self.shield_used = 0
        self.last_heal_time = time.time()

        Pokemon.pokemons[pokemon_trainer] = self

    def get_pokemon_data(self, pokemon_type):
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
            if pokemon_type == "визерд":
                health = randint(150, 800)
                power = randint(5, 20)
                abilities.append("Магический щит") 
            elif pokemon_type == "бойец":
                health = randint(50, 500)
                power = randint(10, 25)
                abilities.append("Супер удар")  
            else:
                health = randint(100, 700)
                power = randint(5, 20)
            return name, img, abilities, level, height, health, health, slot, power, pokemon_type
        else:
            return "Pikachu", "https://via.placeholder.com/150", [], 1, 0, 100, 100, 1, 10, "unknown"

    def info(self):
        return f"Имя твоего покемона: {self.name}, Тип: {self.pokemon_type}, Слот : {self.slot}, Здоровье: {self.health}/{self.max_health}, Сила: {self.power}, базовый опыт: {self.level}, высота: {self.height}, Способности: {', '.join(self.abilities)}"

    def show_img(self):
        return self.img

    def attack(self, opponent):
        if "super power" in self.abilities:
            damage = max(1, self.power * 2 - opponent.power // 2)
        else:
            damage = max(1, self.power - opponent.power // 2)

        if "mageck sheld" in self.abilities and self.shield_used < self.shield_cooldown: 
            damage -= self.shield
            self.shield_used += 1

        opponent.health -= damage
        return damage

    def heal(self):
        if time.time() - self.last_heal_time >= Pokemon.cooldown_time:
            self.health = self.max_health
            self.last_heal_time = time.time()
            return True
        return False

class Wizerd(Pokemon):
    def __init__(self, pokemon_trainer):
        super().__init__(pokemon_trainer, "визерд")

class Boez(Pokemon):
    def __init__(self, pokemon_trainer):
        super().__init__(pokemon_trainer, "бойец")
