import time
import random
import threading

class NPC:
    next_id = 1

    def __init__(self, name, gender, age=0, parent1=None, parent2=None):
        self.id = NPC.next_id
        NPC.next_id += 1
        self.name = name
        self.gender = gender
        self.age = age
        self.hunger = 50
        self.energy = 100
        self.memory = []
        self.skills = {"farming": 0, "hunting": 0, "building": 0, "exploring": 0, "leadership": 0}
        self.traits = {
            "curious": random.choice([True, False]),
            "social": random.choice([True, False]),
            "brave": random.choice([True, False]),
        }
        self.parents = (parent1, parent2)
        self.alive = True
        self.relationships = {}
        self.money = 0
        self.job = random.choice(["farmer", "hunter", "builder", "explorer", None])
        self.partner = None

    def eat(self):
        self.hunger -= 30
        self.hunger = max(0, self.hunger)
        self.store_memory(f"{self.name} ate food.")

    def sleep(self):
        self.energy += 50
        self.energy = min(100, self.energy)
        self.store_memory(f"{self.name} had a good sleep.")

    def work(self):
        if self.job:
            skill = self.job
        else:
            skill = random.choice(list(self.skills.keys()))
        self.skills[skill] += 1
        self.store_memory(f"{self.name} improved {skill}.")
        self.money += 10  # Earn money for working

    def explore(self):
        if self.traits["curious"] and random.random() < 0.5 and self.job == "explorer":
            event = f"{self.name} discovered new land!"
            self.store_memory(event)
            return event
        return None

    def reproduce(self, partner):
        if self.age > 18 and partner.age > 18 and random.random() < 0.3 and self.gender != partner.gender:
            child_name = f"Child_{self.id}_{random.randint(100,999)}"
            child_gender = random.choice(["male", "female"])
            child = NPC(child_name, child_gender, 0, self, partner)
            return child
        return None

    def store_memory(self, event):
        if "discovered" in event:
            self.memory.append(event)
        elif len(self.memory) > 10:
            self.memory.pop(0)
        self.memory.append(event)

    def pass_time(self):
        self.age += 1
        self.hunger += 10
        self.energy -= 10

        if self.hunger > 70:
            self.eat()
        elif self.energy < 30:
            self.sleep()
        else:
            self.work()

        if self.age > 80 and random.random() < 0.1:
            self.alive = False
            return f"{self.name} has passed away."

    def status(self):
        return {
            "ID": self.id,
            "Name": self.name,
            "Gender": self.gender,
            "Age": self.age,
            "Hunger": self.hunger,
            "Energy": self.energy,
            "Skills": self.skills,
            "Traits": self.traits,
            "Memory": self.memory[-3:],
            "Relationships": self.relationships,
            "Money": self.money,
            "Job": self.job,
            "Partner": self.partner.name if self.partner else "None"
        }

class Village:
    def __init__(self, name):
        self.name = name
        self.size = 10  # Initial size of the village
        self.resources = 100  # Initial resources
        self.chief = None
        self.residents = []
        self.migration = 0
        self.laws = []

    def expand(self):
        self.size += 5
        self.resources -= 20

    def upgrade_chief(self):
        if self.chief:
            self.chief.skills["leadership"] = self.chief.skills.get("leadership", 0) + 1

    def add_resident(self, npc):
        self.residents.append(npc)
        if not self.chief or (self.chief and self.chief.age > 60):
            self.chief = npc

    def remove_resident(self, npc):
        self.residents.remove(npc)
        if self.chief == npc:
            self.chief = None

    def create_law(self):
        if self.chief:
            law = f"Law_{random.randint(100,999)}"
            self.laws.append(law)
            self.chief.store_memory(f"{self.chief.name} created law: {law}")

    def status(self):
        job_counts = {"farmer": 0, "hunter": 0, "builder": 0, "explorer": 0, "None": 0}
        for resident in self.residents:
            job_counts[resident.job] += 1

        return {
            "Name": self.name,
            "Size": self.size,
            "Resources": self.resources,
            "Chief": self.chief.name if self.chief else "None",
            "Residents": len(self.residents),
            "Job Distribution": job_counts,
            "Migration": self.migration,
            "Laws": self.laws
        }

    def list_residents(self):
        return [(resident.id, resident.name) for resident in self.residents]

# 🌍 World Management
class Simulation:
    def __init__(self):
        self.villages = [Village("Village_1")]
        self.villages[0].add_resident(NPC("Adam", "male", 25))
        self.villages[0].add_resident(NPC("Eve", "female", 23))
        self.world_age = 0
        self.speed = 1  # Normal speed (1 min = 1 min)

    def run(self):
        while True:
            self.world_age += 1
            for village in self.villages:
                new_npcs = []
                deaths = []

                for npc in village.residents:
                    if npc.alive:
                        npc.pass_time()
                        if random.random() < 0.2 and npc.job == "explorer":  # 20% chance to explore
                            event = npc.explore()
                            if event:
                                print(event)

                        # Reproduction
                        if npc.partner and npc.partner.alive:
                            child = npc.reproduce(npc.partner)
                            if child:
                                new_npcs.append(child)

                    if not npc.alive:
                        deaths.append(npc)

                # Add newborns, remove deceased
                for new_npc in new_npcs:
                    village.add_resident(new_npc)
                for d in deaths:
                    village.remove_resident(d)

                # Expand village if resources allow
                if len(village.residents) > village.size and village.resources > 20:
                    village.expand()

                # Upgrade chief
                village.upgrade_chief()

                # Create laws
                if random.random() < 0.1:
                    village.create_law()

                # Migration
                if len(village.residents) > village.size * 2:
                    new_village = Village(f"Village_{len(self.villages) + 1}")
                    migrants = random.sample(village.residents, village.size // 2)
                    for migrant in migrants:
                        village.remove_resident(migrant)
                        new_village.add_resident(migrant)
                    self.villages.append(new_village)
                    village.migration += 1

            time.sleep(60 / self.speed)  # Adjust speed dynamically

    def check_status(self):
        return {village.name: village.status() for village in self.villages}

    def individual_status(self, npc_id):
        for village in self.villages:
            for npc in village.residents:
                if npc.id == npc_id:
                    return npc.status()
        return "NPC not found."

    def list_residents(self, village_name):
        for village in self.villages:
            if village.name == village_name:
                return village.list_residents()
        return "Village not found."

    def change_speed(self, new_speed):
        self.speed = new_speed

# 🎮 Run Simulation in Background
sim = Simulation()
thread = threading.Thread(target=sim.run, daemon=True)
thread.start()

# 🌍 Player Interaction Loop
while True:
    print("\n📌 Commands: [s] View Village Status, [i ID] View Individual Status, [l VILLAGE_NAME] List Residents, [sp X] Change speed (X=1,10,100), [e] Exit")
    command = input("Enter command: ").strip().lower()

    if command == "s":
        statuses = sim.check_status()
        for village_name, details in statuses.items():
            print(f"\n{village_name} Status: {details}")

    elif command.startswith("i "):
        try:
            npc_id = int(command.split()[1])
            status = sim.individual_status(npc_id)
            print(f"\nNPC {npc_id} Status: {status}")
        except ValueError:
            print("Invalid ID input.")

    elif command.startswith("l "):
        village_name = command.split()[1]
        residents = sim.list_residents(village_name)
        if residents == "Village not found.":
            print(residents)
        else:
            print(f"\nResidents of {village_name}:")
            for resident in residents:
                print(f"ID: {resident[0]}, Name: {resident[1]}")

    elif command.startswith("sp "):
        try:
            new_speed = int(command.split()[1])
            sim.change_speed(new_speed)
            print(f"⏩ Speed changed to {new_speed}x")
        except ValueError:
            print("Invalid speed input.")

    elif command == "e":
        print("Shutting down simulation...")
        break

    else:
        print("Invalid command. Please try again.")
