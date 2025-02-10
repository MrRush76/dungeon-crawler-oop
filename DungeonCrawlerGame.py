import sys
import time
import random

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
room_2: Room = Room("Hall of Echoes", "A hall where every sound is amplified")
room_3: Room = Room("Chamber of Whispers", "A chamber filled with eerie whispers")
room_4: Room = Room("Hall of Shadows", "A hall where shadows seem to move on their own")
room_5: Room = Room("Guard Room", "A room where guards once stood watch")
room_6: Room = Room("Armory", "A room filled with old weapons and armor")
room_7: Room = Room("Torture Chamber", "A room with old torture devices")
room_8: Room = Room("Storage Room", "A cluttered room filled with old supplies")
room_9: Room = Room("Alchemy Lab", "A room with various potions and alchemical equipment")
room_10: Room = Room("Control Room", "A room with old control panels and monitors")
room_11: Room = Room("Dungeon Cell 1", "A dark cell with iron bars")
room_12: Room = Room("Dungeon Cell 2", "A cell with broken chains and shackles")
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






item_gem: Loot = Loot("Gem", "A sparkling gem", 200)
item_potion: Loot = Loot("Potion", "A healing potion", 75)
item_scroll: Loot = Loot("Scroll", "A scroll with ancient writings", 150)
room_8.add_existing_item(item_gem)
room_8.add_existing_item(item_potion)
room_8.add_existing_item(item_scroll)
room_8.add_existing_item(Loot("Golden Crown", "A crown adorned with precious gems", 500))
room_8.add_existing_item(Loot("Ancient Coin", "A rare coin from a lost civilization", 300))
room_8.add_existing_item(Loot("Jeweled Dagger", "A dagger with a jeweled hilt", 250))


sword_1 = Weapon("Excalibur", "A legendary sword with immense power", 500, 50)
sword_2 = Weapon("Shadow Blade", "A dark sword that drains the life of its enemies", 300, 35)
sword_3 = Weapon("Flame Sword", "A sword engulfed in flames", 400, 45)
bow = Weapon("Elven Bow", "A finely crafted bow with great accuracy", 250, 30)
staff = Weapon("Wizard's Staff", "A staff imbued with magical energy", 350, 40)
axe = Weapon("Battle Axe", "A heavy axe with a sharp blade", 200, 25)
dagger = Weapon("Poison Dagger", "A small dagger coated with poison", 150, 20)
mace = Weapon("War Mace", "A spiked mace for crushing armor", 300, 40)


npc_1: NPC = NPC("Gorath the Keeper", "A mysterious figure with a hooded cloak and piercing eyes")
npc_1.add_loot(Loot("Gold Ring", "A shiny gold ring", 100))
npc_1.add_loot(Loot("Dungeon Key of Wisdom", "A key with ancient runes", 50))
room_2.add_npc(npc_1)

npc_2: NPC = NPC("Tharok the Mighty", "A towering warrior with bulging muscles and a fierce expression")
npc_2.add_loot(Loot("Silver Necklace", "A delicate silver necklace", 75))
npc_2.add_loot(Loot("Dungeon Key of Strength", "A key with a lion emblem", 50))
npc_2.add_loot(axe)
room_4.add_npc(npc_2)

npc_3: NPC = NPC("Lyra the Shadow", "A nimble rogue with quick reflexes and a mischievous grin")
npc_3.add_loot(Loot("Bronze Coin", "An old bronze coin", 50))
npc_3.add_loot(Loot("Dungeon Key of Agility", "A key with a winged design", 50))
npc_3.add_loot(dagger)
room_6.add_npc(npc_3)

npc_4: NPC = NPC("Arin the Sage", "A wise scholar with a book in hand and a thoughtful demeanor")
npc_4.add_loot(Loot("Platinum Bracelet", "A shiny platinum bracelet", 150))
npc_4.add_loot(Loot("Dungeon Key of Intelligence", "A key with a book symbol", 50))
npc_4.add_loot(mace)
room_8.add_npc(npc_4)

loot_1: Loot = Loot("Silver Ring", "A shiny silver ring", 50)
room_spawn.add_existing_item(loot_1)
player_1.collect_item(loot_1)

wooden_sword = Weapon("Wooden Sword", "A basic wooden sword", 10, 5)
player_1.collect_item(wooden_sword, True)
player_1.weapon = wooden_sword


room_3.add_existing_item(sword_1)
room_5.add_existing_item(sword_2)
room_7.add_existing_item(sword_3)
room_9.add_existing_item(bow)
room_11.add_existing_item(staff)

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
        print_slow("Your ultimate goal is to reach Dungeon Cell 2, where you can merge the keys to unlock the final room and complete the game.")
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
            if self.player.current_room != room_spawn:
                print_slow(f"You are in {self.player.current_room.name} you have {self.player.hp} health remaining")
            print_slow("\nWhat would you like to do?")
            print_slow("1. Move to another room")
            print_slow("2. Check inventory")
            print_slow("3. Collect item in room")
            print_slow("4. Show NPCs")
            print_slow("5. Quit game")
            if self.player.current_room.check_npc():
                print_slow("6. Talk to NPC\n")
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
                    if self.player.current_room.check_npc():
                        print_slow("6. Talk to NPC\n")
                        places = ["by the door", "in the corner", "in the middle", "leaning against the wall"]
                        random_place = random.choice(places)
                        print_slow(f"You see a figure {random_place} in the room")

            if self.player.current_room == room_12:
                print_slow("7. Merge keys")
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
            elif choice == "6":
                if self.player.current_room.check_npc():
                    self.talk_to_npc()
            elif choice == "7":
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
        direction = input("Enter your choice: ")
        if direction in self.player.current_room.connected_rooms:
            self.player.set_current_room(self.player.current_room.connected_rooms[direction])
        else:
            print_slow("Invalid direction")


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
            item_name = input("Enter the name of the item to collect: ")
            for item in self.player.current_room.items:
                if item.name.lower() == item_name.lower():
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
            choice = input("Enter the name of the item you would like to buy: ")
            for loot in npc.loot:
                if loot.name.lower() == choice.lower():
                    loot_bought = True
                    npc.buy_loot(loot, self.player)

            if not loot_bought:
                print_slow("Item not found")
        elif choice == "2":
            loot_sold = False
            print_slow("You have the following items to sell:")
            for item in self.player.inventory:
                if isinstance(item, Loot):
                    item.slow_print()
            choice = input("Enter the name of the item you would like to sell: ")
            for item in self.player.inventory:
                if item.name.lower() == choice.lower() and isinstance(item, Loot):
                    self.player.remove_item(item)
                    self.player.add_money(item.value)
                    npc.add_loot(item)
                    loot_sold = True
                    print_slow(f"{self.player.name} sold {item.name} for {item.value} coins")
            if not loot_sold:
                print_slow("Item not found")
        else:
            print_slow("Invalid choice")
        print_slow(f"{npc.name}: Anything else?")
        choice = input("Enter your choice: ")
        if choice == "yes":
            self.talk_to_npc()
        else:
            print_slow("Goodbye")
            return


game = Game(player_1)
start_game = game.menu()