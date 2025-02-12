import sys
import random
import json
directions_map: dict[str:str] = {
    "up": "down",
    "down": "up",
    "left": "right",
    "right": "left"
}

def print_slow(text: str):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
    print()

class Item:
    def __init__(self, given_name: str, given_desc: str):
        self.name: str = given_name
        self.description: str = given_desc

    def __str__(self):
        return f"This is a '{self.name}' and it is '{self.description}'"

    def slow_print(self) -> None:
        print_slow(f"This is a '{self.name}' and it is '{self.description}'")

class Loot(Item):
    def __init__(self, given_name: str, given_desc: str, given_value: int):
        super().__init__(given_name, given_desc)
        self.value: int = given_value

    def __str__(self):
        return f"This is a '{self.name}' and it is '{self.description}' and it is worth '{self.value}'"

    def slow_print(self) -> None:
        print_slow(f"This is a '{self.name}' and it is '{self.description}' and it is worth '{self.value}'")

class Weapon(Loot):
    def __init__(self, given_name: str, given_desc: str, given_value: int, given_damage: int):
        super().__init__(given_name, given_desc, given_value)
        self.damage: int = given_damage

    def __str__(self):
        return f"This is a '{self.name}' and it is '{self.description}' and it is worth '{self.value}' and it does '{self.damage}' damage"

    def slow_print(self) -> None:
        print_slow(f"This is a '{self.name}' and it is '{self.description}' and it is worth '{self.value}' and it does '{self.damage}' damage")

# class Potion(Loot):
#     def __init__(self, given_name: str, given_desc: str, given_value: int, given_effect: int):
#         super().__init__(given_name, given_desc, given_value)
#         self.effect: str = given_effect
#

class NPC:
    def __init__(self, given_name: str, given_desc: str):
        self.name: str = given_name
        self.description: str = given_desc
        self.loot: list[Loot] = []

    def __str__(self):
        return f"This is '{self.name}' and they are '{self.description}'"

    def slow_print(self) -> None:
        print_slow(f"This is a '{self.name}' and they are '{self.description}'")

    def add_loot(self, loot: Loot) -> None:
        self.loot.append(loot)

    def remove_loot(self, loot: Loot) -> None:
        self.loot.remove(loot)

    def buy_loot(self, loot: Loot, player: "Player") -> None:
        if player.money >= loot.value:
            player.remove_money(loot.value)
            player.collect_item(loot, True)
            self.remove_loot(loot)
            print_slow(f"{player.name} bought {loot.name} for {loot.value} coins")
        else:
            print_slow(f"{player.name} does not have enough money to buy {loot.name}")

    def show_loot(self) -> None:
        if len(self.loot) == 0:
            print_slow(f"{self.name} has no loot")
            return
        print_slow(f"{self.name} has the following loot:")
        for loot in self.loot:
            print_slow("-> " + loot.name + " worth " + str(loot.value) + " coins")
            print_slow(loot.description)

class Enemy(NPC):
    def __init__(self, given_name: str, given_desc: str, given_hp: int, given_damage: int):
        super().__init__(given_name, given_desc)
        self.hp: int = given_hp
        self.damage: int = given_damage

    def attack(self, player: "Player") -> None:
        player.hp -= self.damage
        print_slow(f"{self.name} attacked {player.name} for {self.damage} damage")
        print_slow(f"{player.name} has {player.hp} health remaining")

    def take_damage(self, damage: int) -> None:
        self.hp -= damage
        print_slow(f"{self.name} took {damage} damage")
        if self.hp <= 0:
            self.kill()
        else:
            print_slow(f"{self.name} has {self.hp} health remaining")

    def kill(self) -> None:
        print_slow(f"{self.name} has been defeated")

class Room:
    def __init__(self, given_name: str, given_desc: str, locked: bool = False, unlock_item: Item = None):
        self.name: str = given_name
        self.description: str = given_desc
        self.items: list[Item] = list()
        self.connected_rooms: dict[str, Room] = dict()
        self.locked: bool = locked
        self.unlock_item: Item = unlock_item
        self.npcs: list[NPC] = list()

    def __str__(self):
        return f"This is a '{self.name}' and it is '{self.description}'"

    def add_existing_item(self, existing_item: Item) -> None:
        self.items.append(existing_item)

    def connect_room(self, existing_room: "Room", direction: str, two_way: bool = True) -> None:
        self.connected_rooms[direction] = existing_room
        if two_way:
            existing_room.connect_room(self, directions_map[direction], False)

    def remove_item(self, existing_item: Item) -> None:
        if existing_item in self.items:
            self.items.remove(existing_item)

    def items_in_room(self) -> bool:
        return len(self.items) > 0

    def show_items(self) -> None:
        if len(self.items) == 0:
            print_slow("No items in this room")
            return
        print_slow(f"Items in {self.name}:")
        for item in self.items:
            item.slow_print()

    def add_npc(self, npc: NPC) -> None:
        self.npcs.append(npc)

    def check_npc(self) -> bool:
        return len(self.npcs) > 0

    def show_npc(self) -> None:
        if len(self.npcs) == 0:
            print_slow("No NPC's in this room")
            return
        print_slow(f"NPC in {self.name} is {self.npcs[0].name}")

    def show_connected_rooms(self) -> None:
        for direction, room in self.connected_rooms.items():
            print_slow(f"{direction.capitalize()} : {room.name}")

class Player:
    current_room: "Room"

    def __init__(self, given_name: str, starting_room: Room):
        self.name: str = given_name
        if starting_room.name == "Spawn":
            self.set_current_room(starting_room, True)
        else:
            self.set_current_room(starting_room)
        self.inventory: list[Item] = list()
        self.money: int = 100
        self.hp: int = 100
        self.weapon: Weapon = None

    def __str__(self):
        return f"This is '{self.name}' and they are in '{self.current_room.name}' items in inventory: '{self.inventory}'"

    def set_current_room(self, new_room: Room, spawn: bool = False) -> None:
        if spawn:
            self.current_room = new_room
            return
        if not new_room.locked and new_room in self.current_room.connected_rooms.values():
            self.current_room = new_room
        elif new_room.locked and self.check_inventory(new_room.unlock_item):
            self.current_room = new_room
            self.inventory.remove(new_room.unlock_item)
        else:
            print_slow("Room is locked")

    def items_in_room(self) -> None:
        self.current_room.show_items()

    def remove_money(self, amount: int) -> None:
        self.money -= amount

    def add_money(self, amount: int) -> None:
        self.money += amount

    def collect_item(self, existing_item: Item, npc_bought=False) -> None:
        self.inventory.append(existing_item)
        if not npc_bought:
            self.current_room.remove_item(existing_item)

    def remove_item(self, existing_item: Item) -> None:
        self.inventory.remove(existing_item)

    def check_inventory(self, existing_item: Item) -> bool:
        return existing_item in self.inventory

final_key: Item = Item("Final Key", "A key that unlocks the final room")
room_spawn: Room = Room("Spawn", "The starting room")
player_1: Player = Player("Player 1", room_spawn)
with open('generate.json', 'r') as file:
    data = json.load(file)

rooms_data = data['rooms']
random_rooms = random.sample(rooms_data, 13)
room_2: Room = Room(random_rooms[0]['name'], random_rooms[0]['description'])
room_3: Room = Room(random_rooms[1]['name'], random_rooms[1]['description'])
room_4: Room = Room(random_rooms[2]['name'], random_rooms[2]['description'])
room_5: Room = Room(random_rooms[3]['name'], random_rooms[3]['description'])
room_6: Room = Room(random_rooms[4]['name'], random_rooms[4]['description'])
room_7: Room = Room(random_rooms[5]['name'], random_rooms[5]['description'])
room_8: Room = Room(random_rooms[6]['name'], random_rooms[6]['description'])
room_9: Room = Room(random_rooms[7]['name'], random_rooms[7]['description'])
room_10: Room = Room(random_rooms[8]['name'], random_rooms[8]['description'])
room_11: Room = Room(random_rooms[9]['name'], random_rooms[9]['description'])
room_12: Room = Room(random_rooms[10]['name'], random_rooms[10]['description'])
room_13: Room = Room("Final Room", "A room with flickering torches", True, final_key)

room_spawn.connect_room(room_2, "right")
room_2.connect_room(room_3, "right")
room_2.connect_room(room_4, "left")
room_2.connect_room(room_5, "up")
room_3.connect_room(room_6, "right")
room_3.connect_room(room_7, "left")
room_4.connect_room(room_8, "down")
room_4.connect_room(room_9, "left")
room_5.connect_room(room_10, "up")
room_2.connect_room(room_3, "right")
room_6.connect_room(room_11, "down")
room_6.connect_room(room_2, "left")
room_6.connect_room(room_11, "down")
room_11.connect_room(room_6, "up")
room_11.connect_room(room_3, "left")
room_7.connect_room(room_12, "down")
room_12.connect_room(room_7, "up")
room_12.connect_room(room_3, "right")





random_loot = random.sample(data['items'], 6)
for loot in random_loot:
    item = Loot(loot['name'], loot['description'], loot['value'])
    random.choice([room_2, room_3, room_4, room_5, room_6, room_7, room_8, room_9, room_10, room_11, room_12]).add_existing_item(item)

random_weapons = random.sample(data['weapons'], 6)
for weapon in random_weapons:
    item = Weapon(weapon['name'], weapon['description'], weapon['value'], weapon['damage'])
    random.choice([room_2, room_3, room_4, room_5, room_6, room_7, room_8, room_9, room_10, room_11, room_12]).add_existing_item(item)

random_npcs = random.sample(data['npcs'], 4)
keys = ["Dungeon Key of Wisdom", "Dungeon Key of Strength", "Dungeon Key of Agility", "Dungeon Key of Intelligence"]
for npc_data, key in zip(random_npcs, keys):
    npc = NPC(npc_data['name'], npc_data['description'])
    key_item = Loot(key, f"A key that represents {key.split()[-1].lower()}", 50)
    npc.add_loot(key_item)
    random_room = random.choice([room_2, room_3, room_4, room_5, room_6, room_7, room_8, room_9, room_10, room_11, room_12])
    while random_room.check_npc():
        random_room = random.choice([room_2, room_3, room_4, room_5, room_6, room_7, room_8, room_9, room_10, room_11, room_12])
    random_room.add_npc(npc)


loot_1: Loot = Loot("Silver Ring", "A shiny silver ring", 50)
room_spawn.add_existing_item(loot_1)
player_1.collect_item(loot_1)

wooden_sword = Weapon("Wooden Sword", "A basic wooden sword", 10, 5)
player_1.collect_item(wooden_sword, True)
player_1.weapon = wooden_sword



class Game:
    def __init__(self, player: Player = None):
        self.player = player
        self.game_over = False
        self.win = False

    def menu(self):
        print_slow("Welcome to the Dungeon Crawler Game!")
        print_slow("In this game, you will explore various rooms, collect items, and interact with NPCs.")
        print_slow("Make sure to look for weapons in the rooms to help you in battles.")
        print_slow("Keep an eye out for keys, as they are essential to progress through the game.")
        print_slow(f"Your ultimate goal is to reach {room_12.name}, where you can merge the keys to unlock the final room and complete the game.")
        print_slow("Good luck!")
        print_slow("1. Start Game")
        print_slow("2. Exit Game")
        choice = input("Enter your choice: \n")
        if choice == "1":
            print_slow("What is your name?")
            name = input("Enter your name: ")
            self.player.name = name
            self.start_game()
        elif choice == "2":
            self.game_over = True
        else:
            print_slow("Invalid choice")
            self.menu()

    def start_game(self):
        print("\nYou are in the Spawn room")
        while not self.game_over:
            for i in range(len(self.player.inventory)):
                if isinstance(self.player.inventory[i], Weapon):
                    if self.player.inventory[i].damage > self.player.weapon.damage:
                        self.player.weapon = self.player.inventory[i]
            if self.player.current_room != room_spawn:
                print_slow(f"You are in {self.player.current_room.name} you have {self.player.hp} health remaining")
            print_slow("\nWhat would you like to do?")
            print_slow("1. Move to another room")
            print_slow("2. Check inventory")
            print_slow("3. Collect item in room")
            print_slow("4. Show NPCs")
            print_slow("5. Quit game")
            option_number = 6
            if self.player.current_room.check_npc():
                print_slow(f"{option_number}. Talk to NPC\n")
                option_number += 1
                places = ["by the door", "in the corner", "in the middle", "leaning against the wall"]
                random_place = random.choice(places)
                print_slow(f"You see a figure {random_place} in the room")
            if self.player.current_room != room_13 and self.player.current_room.name != "Spawn":
                random_number = random.randint(1, 5)
                random_number_2 = random.randint(1, 5)
                if random_number == random_number_2:
                    print_slow("An enemy has appeared")
                    enemy_names = ["Goblin", "Orc", "Troll", "Skeleton", "Zombie"]
                    enemy_name = random.choice(enemy_names)
                    enemy_hp = random.randint(1, 50)
                    enemy_damage = random.randint(1, 10)
                    enemy = Enemy(enemy_name, "A fearsome foe", enemy_hp, enemy_damage)
                    print_slow(f"{enemy.name} has {enemy.hp} health")
                    running = True
                    while enemy.hp > 0:
                        print_slow("1. Attack")
                        if running:
                            print_slow("2. Run")
                        choice = input("Enter your choice: ")
                        if choice == "1":
                            enemy.attack(self.player)
                            enemy.take_damage(self.player.weapon.damage)
                            if self.player.hp <= 0:
                                print_slow("You have been defeated")
                                self.game_over = True
                                break
                        elif choice == "2":
                            random_run = random.randint(1, 5)
                            if random_run == 3:
                                print_slow("You can no longer run")
                                running = False
                            else:
                                break
                            break
                        else:
                            print_slow("Invalid choice")
                    print_slow(f"You are in {self.player.current_room.name} you have {self.player.hp} health remaining and {self.player.money} coins")
                    print_slow("\nWhat would you like to do?")
                    print_slow("1. Move to another room")
                    print_slow("2. Check inventory")
                    print_slow("3. Collect item in room")
                    print_slow("4. Show NPCs")
                    print_slow("5. Quit game")
                    option_number = 6




            if self.player.current_room == room_12:
                print_slow(f"{option_number}. Merge keys")
            choice = input("\nEnter your choice: ")
            if choice == "1":
                self.move()
            elif choice == "2":
                self.check_inventory()
            elif choice == "3":
                self.check_and_collect_item()
            elif choice == "4":
                self.player.current_room.show_npc()
            elif choice == "5":
                self.game_over = True
            elif choice == str(option_number - 1):
                if self.player.current_room.check_npc():
                    self.talk_to_npc()
            elif choice == str(option_number):
                if self.player.current_room == room_12:
                    keys = ["Dungeon Key of Wisdom", "Dungeon Key of Strength", "Dungeon Key of Agility", "Dungeon Key of Intelligence"]
                    missing_keys = [key for key in keys if key not in [item.name for item in self.player.inventory]]
                    if missing_keys:
                        for key in missing_keys:
                            print_slow(f"You do not have the {key}")
                        print_slow("They are sold by the NPC's in the rooms")
                    else:
                        print_slow("The Keys are rising into the air and merging into one")
                        print_slow("The Keys have merged into the Final Key")
                        self.player.collect_item(final_key, True)
                        print_slow("You collect the Final Key")
                        print_slow("Would you like to unlock the final room?")
                        choice = input("Enter your choice: ")
                        if choice.lower() == "yes":
                            self.player.set_current_room(room_13)
                            print_slow("You have unlocked the final room")
                            print_slow("You see a figure in the corner of the room")
                            print_slow("You approach the figure and see a shadowy figure")
                            print_slow("The figure hands you a small box")
                            print_slow("You open the box and see a bright light")
                            print_slow("You wake up in your bed")
                            print_slow("Congratulations you have completed the game")
                            self.win = True
                            self.game_over = True
                        else:
                            print_slow("You have chosen not to unlock the final room")
                            print_slow("Game Over")
                            self.game_over = True
                else:
                    print_slow("Invalid choice")
            else:
                print_slow("Invalid choice")


    def move(self):
        print_slow("Which direction would you like to move?")
        self.player.current_room.show_connected_rooms()
        directions = list(self.player.current_room.connected_rooms.keys())
        for i, direction in enumerate(directions, start=1):
            print_slow(f"{i}. {direction.capitalize()}")
        choice = input("Enter the number of your choice: ")
        if choice.isdigit() and 1 <= int(choice) <= len(directions):
            direction = directions[int(choice) - 1]
            self.player.set_current_room(self.player.current_room.connected_rooms[direction])
        else:
            print_slow("Invalid choice")


    def check_inventory(self):
        if len(self.player.inventory) == 0:
            print_slow("No items in inventory")
        else:
            print_slow("Items in inventory:")
            for item in self.player.inventory:
                item.slow_print()
            print_slow(f"Money: {self.player.money}")


    def check_and_collect_item(self):
        self.player.current_room.show_items()
        if self.player.current_room.items_in_room():
            print_slow("Enter the number of the item to collect:")
            for index, item in enumerate(self.player.current_room.items, start=1):
                print_slow(f"{index}. {item.name}")
            choice = input("Enter the number of the item to collect: ")
            for index, item in enumerate(self.player.current_room.items, start=1):
                if str(index) == choice:
                    self.player.collect_item(item)
                    print_slow(f"Collected {item.name}")
                    return
            print_slow("Item not found")


    def talk_to_npc(self):
        npc = self.player.current_room.npcs[0]
        print_slow(f"You approach {npc.name} with your bag of {self.player.money} coins")
        print_slow(f"{npc.name} says: Hello {self.player.name}")
        npc.show_loot()
        print_slow("Would you like to buy or sell something?")
        print_slow("1. Buy")
        print_slow("2. Sell")
        choice = input("Enter your choice: ")
        if choice == "1":
            loot_bought = False
            print_slow("Enter the number of the item you would like to buy:")
            for index, loot in enumerate(npc.loot, start=1):
                print_slow(f"{index}. {loot.name} worth {loot.value} coins")
            choice = input("Enter the number of the item you would like to buy: ")
            for index, loot in enumerate(npc.loot, start=1):
                if str(index) == choice:
                    loot_bought = True
                    npc.buy_loot(loot, self.player)
                    break
            if not loot_bought:
                print_slow("Item not found")
        elif choice == "2":
            loot_sold = False
            print_slow("You have the following items to sell:")
            for index, item in enumerate(self.player.inventory, start=1):
                if isinstance(item, Loot):
                    print_slow(f"{index}. {item.name} worth {item.value} coins")
            choice = input("Enter the number of the item you would like to sell: ")
            for index, item in enumerate(self.player.inventory, start=1):
                if str(index) == choice and isinstance(item, Loot):
                    self.player.remove_item(item)
                    self.player.add_money(item.value)
                    npc.add_loot(item)
                    loot_sold = True
                    print_slow(f"{self.player.name} sold {item.name} for {item.value} coins")
                    break
            if not loot_sold:
                print_slow("Item not found")
        else:
            print_slow("Invalid choice")
        print_slow(f"{npc.name}: Anything else? (1 - Yes, 2 - No)")
        choice = input("Enter your choice: ")
        if choice == "1":
            self.talk_to_npc()
        else:
            print_slow("Goodbye")
            return


game = Game(player_1)
start_game = game.menu()
