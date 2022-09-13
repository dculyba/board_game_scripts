import random
import csv


class Die:
    def __init__(self, vals=[1,2,3,4,5,6], is_special=False):
        self.vals = vals
        self.is_special = is_special
        self.current_val = None

    def roll(self):
        self.current_val = random.choice(self.vals)
        return self.current_val

class DiceSet:
    def __init__(self, name="", dice=[]):
        self.name = name
        self.dice = dice

    def roll(self, dice_to_hold=[]):
        result = []
        for die in self.dice:
            if die in dice_to_hold:
                result.append(die.current_val)
            else:
                result.append(die.roll())
        result.sort()
        return result

    def get_current_roll(self):
        result = []
        for die in self.dice:
            result.append(die.current_val)
        result.sort()
        return result

def has_pair(sorted_list):
    for i in range(len(sorted_list)-1):
        if sorted_list[i] == sorted_list[i+1]:
            return i
    return -1

class Recipe:
    def __init__(self, name="", pattern=[]):
        self.name = name
        self.pattern = pattern

    def check_roll(self, die_roll):
        unmatched = self.pattern.copy()
        for symbol in self.pattern:
            if symbol in die_roll:
                die_roll.remove(symbol)
                unmatched.remove(symbol)
        for symbol in unmatched:
            pair_index = has_pair(die_roll)
            if pair_index != -1:
                unmatched.remove(symbol)
                die_roll.pop(pair_index)
                die_roll.pop(pair_index)
        if len(unmatched) == 0:
            return True
        return False

    def reroll(self, dice_set):
        to_hold = []
        to_reroll = dice_set.dice.copy()
        for to_match in self.pattern:
            matching_dice = []
            die_to_hold = None
            for die in to_reroll:
                if die.current_val == to_match:
                    matching_dice.append(die)
            if len(matching_dice) == 1:
                die_to_hold = matching_dice[0]
            elif len(matching_dice) > 1:
                for die in matching_dice:
                    if die.is_special:
                        die_to_hold = die
                        break
                if die_to_hold is None:
                    die_to_hold = matching_dice[0]
            if die_to_hold != None:
                to_reroll.remove(die_to_hold)
                to_hold.append(die_to_hold)
        success = self.check_roll(dice_set.roll(to_hold))
        return success



class RollSimulator:
    PRIMARY_SUCCESS_KEY = "primary success count"
    PRIMARY_PROBABILITY_KEY = "primary probability"
    SECONDARY_SUCCESS_KEY = "secondary success count"
    SECONDARY_PROBABILITY_KEY = "secondary probability"
    TOTAL_KEY = "total"

    PATTERN_NAME_KEY = "Pattern Name"


    def __init__(self):
        self.recipes = []
        self.dice_sets = []
        self.results = []
        self.field_names = []

    def add_recipe(self, recipe):
        self.recipes.append(recipe)

    def add_dice_set(self, dice_set):
        self.dice_sets.append(dice_set)

    def simulate(self, cycles=100):
        self.results.clear()
        self.field_names.clear()
        for recipe in self.recipes:
            recipe_results = {RollSimulator.PATTERN_NAME_KEY:recipe.name}
            for dice_set in self.dice_sets:
                success1_count = 0
                success2_count = 0
                for i in range(cycles):
                    success1 = recipe.check_roll(dice_set.roll())
                    if success1:
                        success1_count += 1
                    else:
                        success2 = recipe.reroll(dice_set)
                        if success2:
                            success2_count += 1
                success1_probability = success1_count / cycles
                success2_probability = success2_count / cycles
                recipe_results[dice_set.name+": 1st"] = success1_probability
                recipe_results[dice_set.name + ": 2nd"] = success2_probability
                recipe_results[dice_set.name + ": Total"] = success1_probability + success2_probability
            self.results.append(recipe_results)
        self.field_names.append(RollSimulator.PATTERN_NAME_KEY)
        for dice_set in self.dice_sets:
            self.field_names.append(dice_set.name+": 1st")
            self.field_names.append(dice_set.name + ": 2nd")
            self.field_names.append(dice_set.name + ": Total")

    def print_results(self):
        for result in self.results:
            print(result[RollSimulator.PATTERN_NAME_KEY]+":")
            for dice_set in self.dice_sets:
                primary_probability = result[dice_set.name+": 1st"]
                print("  "+dice_set.name+": "+str(primary_probability))

    def write_results_csv(self, csv_file):
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.field_names)
            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

def main():
    uc_sim = RollSimulator()
    uc_sim.add_recipe(Recipe("Four Unique", [1,2,3,4]))
    uc_sim.add_recipe(Recipe("Three Unique", [1, 2, 3]))
    uc_sim.add_recipe(Recipe("Two Unique", [1, 2]))
    uc_sim.add_recipe(Recipe("One Unique", [1]))
    uc_sim.add_recipe(Recipe("Two Matching", [1, 1]))
    uc_sim.add_recipe(Recipe("Three Matching", [1, 1, 1]))
    uc_sim.add_recipe(Recipe("Four Matching", [1, 1, 1, 1]))
    uc_sim.add_recipe(Recipe("Two Matching Two Unique", [1, 1, 2, 3]))
    uc_sim.add_recipe(Recipe("Two Matching One Unique", [1, 1, 2]))
    uc_sim.add_recipe(Recipe("Two Matching Two Unique", [1, 1, 1, 2]))
    uc_sim.add_recipe(Recipe("Two Matching Two Matching", [1, 1, 2, 2]))
    uc_sim.add_recipe(Recipe("Five Unique", [1, 2, 3, 4, 5]))
    uc_sim.add_recipe(Recipe("Two Matching Three Unique", [1, 1, 2, 3, 4]))
    uc_sim.add_recipe(Recipe("Three Matching Two Unique", [1, 1, 1, 2, 3]))
    uc_sim.add_recipe(Recipe("Four Matching One Unique", [1, 1, 1, 1, 2]))
    uc_sim.add_recipe(Recipe("Two Matching Two Matching One Unique", [1, 1, 2, 2, 3]))
    uc_sim.add_recipe(Recipe("Three Matching Two Matching", [1, 1, 1, 2, 2]))

    base_dice_set = [Die([1,2,3,4,5,6]),Die([1,2,3,4,5,6]),Die([1,2,3,4,5,6]),Die([1,2,3,4,5,6])]
    specialty_die_1 = [Die([1, 1, 1, 1, 6, 6], is_special=True)]
    specialty_die_2 = [Die([2, 2, 2, 2, 6, 6], is_special=True)]
    specialty_die_3 = [Die([3, 3, 3, 3, 6, 6], is_special=True)]
    specialty_die_4 = [Die([4, 4, 4, 4, 6, 6], is_special=True)]
    specialty_die_5 = [Die([5, 5, 5, 5, 6, 6], is_special=True)]
    uc_sim.add_dice_set(DiceSet("No Specialty Dice", base_dice_set))

    uc_sim.add_dice_set(DiceSet("One Specialty Die", base_dice_set+specialty_die_1))
    uc_sim.add_dice_set(DiceSet("Two Specialty Die", base_dice_set + specialty_die_2))
    uc_sim.add_dice_set(DiceSet("Three Specialty Die", base_dice_set + specialty_die_3))
    uc_sim.add_dice_set(DiceSet("Four Specialty Die", base_dice_set + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("Five Specialty Die", base_dice_set + specialty_die_5))

    uc_sim.add_dice_set(DiceSet("One Two Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2))
    uc_sim.add_dice_set(DiceSet("One Three Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_3))
    uc_sim.add_dice_set(DiceSet("One Four Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("One Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Two Three Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_3))
    uc_sim.add_dice_set(DiceSet("Two Four Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("Two Five Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Three Four Specialty Dice", base_dice_set + specialty_die_3 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("Three Five Specialty Dice", base_dice_set + specialty_die_3 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Four Five Specialty Dice", base_dice_set + specialty_die_4 + specialty_die_5))

    uc_sim.add_dice_set(DiceSet("One Two Three Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_3))
    uc_sim.add_dice_set(DiceSet("One Two Four Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("One Two Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("One Three Four Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_3 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("One Three Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_3 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("One Four Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_4 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Two Three Four Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_3 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("Two Three Five Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_3 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Two Four Five Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_4 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Three Four Five Specialty Dice", base_dice_set + specialty_die_3 + specialty_die_4 + specialty_die_5))

    uc_sim.add_dice_set(DiceSet("One Two Three Four Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_3 + specialty_die_4))
    uc_sim.add_dice_set(DiceSet("One Two Three Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_3 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("One Two Four Five Specialty Dice", base_dice_set + specialty_die_1 + specialty_die_2 + specialty_die_4 + specialty_die_5))
    uc_sim.add_dice_set(DiceSet("Two Three Four Five Specialty Dice", base_dice_set + specialty_die_2 + specialty_die_3 + specialty_die_4 + specialty_die_5))

    uc_sim.simulate(10000)
    uc_sim.print_results()
    uc_sim.write_results_csv('results.csv')

if __name__ == "__main__":
    main()