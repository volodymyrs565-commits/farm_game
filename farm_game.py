import asyncio

plants = [
    {"id": 1, "name": "Wheat", "baseGrowTime": 5, "sellPrice": 12},
    {"id": 2, "name": "Carrot", "baseGrowTime": 3, "sellPrice": 8},
    {"id": 3, "name": "Corn", "baseGrowTime": 8, "sellPrice": 20},
]

fertilizers = {
    "basic": {"price": 10, "multiplier": 0.8},
    "strong": {"price": 25, "multiplier": 0.6},
}

class Plot:
    def __init__(self, plot_id):
        self.id = plot_id
        self.state = "empty"
        self.plant = None

    async def grow(self, grow_time):
        await asyncio.sleep(grow_time)
        self.state = "ready"
        print(f"Plot {self.id}: {self.plant['name']} is ready")

class Barn:
    def __init__(self):
        self.storage = {}

    def add(self, plant_name, amount=1):
        self.storage[plant_name] = self.storage.get(plant_name, 0) + amount
        print(f"Barn: {plant_name} +{amount}")

    def remove(self, plant_name, amount=1):
        if self.storage.get(plant_name, 0) >= amount:
            self.storage[plant_name] -= amount
            if self.storage[plant_name] == 0:
                del self.storage[plant_name]
            return True
        return False

class Player:
    def __init__(self):
        self.money = 50
        self.inventory = {}
        self.barn = Barn()

class Shop:
    def __init__(self, player):
        self.player = player

    def buy_fertilizer(self, name):
        fert = fertilizers[name]
        if self.player.money >= fert["price"]:
            self.player.money -= fert["price"]
            self.player.inventory[name] = self.player.inventory.get(name, 0) + 1
            print(f"Bought fertilizer: {name}")
        else:
            print("Not enough money")

    def sell_crop(self, plant_name):
        for p in plants:
            if p["name"] == plant_name:
                if self.player.barn.remove(plant_name):
                    self.player.money += p["sellPrice"]
                    print(f"Sold {plant_name} for {p['sellPrice']}")
                else:
                    print("Not in barn")

class Farm:
    def __init__(self, player, plots_count=3):
        self.player = player
        self.plots = [Plot(i + 1) for i in range(plots_count)]

    async def plant_crop(self, plot_id, plant_id, fertilizer=None):
        plot = self.plots[plot_id - 1]

        if plot.state != "empty":
            print("Plot is busy")
            return

        plant = next(p for p in plants if p["id"] == plant_id)
        grow_time = plant["baseGrowTime"]

        if fertilizer:
            if self.player.inventory.get(fertilizer, 0) <= 0:
                print("No fertilizer")
                return
            self.player.inventory[fertilizer] -= 1
            grow_time *= fertilizers[fertilizer]["multiplier"]

        plot.state = "growing"
        plot.plant = plant

        print(f"Planted {plant['name']} on plot {plot.id} ({grow_time:.1f}s)")
        asyncio.create_task(plot.grow(grow_time))

    def harvest(self, plot_id):
        plot = self.plots[plot_id - 1]

        if plot.state != "ready":
            print("Nothing to harvest")
            return

        self.player.barn.add(plot.plant["name"])
        plot.state = "empty"
        plot.plant = None

async def main():
    player = Player()
    shop = Shop(player)
    farm = Farm(player)

    print(f"Balance: {player.money}")

    shop.buy_fertilizer("basic")
    await farm.plant_crop(1, 1, "basic")

    await asyncio.sleep(6)

    farm.harvest(1)
    shop.sell_crop("Wheat")

    print(f"Balance: {player.money}")

asyncio.run(main())
