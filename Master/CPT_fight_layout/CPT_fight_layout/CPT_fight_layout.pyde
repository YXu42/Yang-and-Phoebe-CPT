import random
import time

user_option_selection_counter = 0
option_selection = 0
slide = 0
player_pos = [320, 308]
offset = 0
keys_pressed = [False for key_code in range(256)]
enemy_dialogue = []
movement = True
text_list_index = 0 # Maybe fix
ENEMY_ATTACK_BOUNDARIES = [425, 375, 200, 229]
WORLD_BOUNDARIES = [0, 150, -891, -72]
map_offset = [-10, 0]
counter = 0

enemy_attack = None
user_color = "#FF0000"
USER_HEALTH = [20, 20]
items = ["Burger", "Ice Cream", "Noodles", "Cake"]
item_values = [12, 6, 2, 8]
ENEMY_DAMAGE = 4
attack_counter = 0
MAX_ATTACK_COUNT = 5
ratio = random.random()


def setup():
    global user, enemy, landscape, PLAYER_POS_WORLD, user_items, heart, player, keys_pressed, enemy_image
    size(640, 480)
    rectMode(CORNERS)
    frameRate(100)

    player = loadImage("player.png")
    heart = loadImage("heart.png")
    landscape = loadImage("map.png")
    

    PLAYER_POS_WORLD = [width/2, height/2]

    enemy = Enemy()
    user_items = Item(items, item_values)
    user = User(USER_HEALTH)
    tests = Tests()

    tests.test_user_attack_damage_calc()
    tests.test_user_movement()
    tests.test_movement_boundaries()
    tests.test_enemy_patch()
    tests.test_enemy_act()
    tests.test_enemy_collision_detection()
    tests.test_immunity()
    tests.test_reset()
    tests.test_use_item()
    
    enemy.patch()  # Defined at beginning just to get program running
    
    keys_pressed = [False for key_code in range(256)]  # Reseting because tests change variables


def draw():
    global slide, user_option_selection_counter, option_selection, user, enemy
    global offset, player_pos, movement, map_offset
    global counter, keys_pressed, enemy_attack, user_health, user_items
    global attack_counter, MAX_ATTACK_COUNT, text_list_index
    background(0)
    
    if slide == 3 or slide == 4 or slide == 5 or slide == 6:
        battle_screen_display(user.user_health, enemy.enemy_attributes[1:3])
        enemy_image.resize(0, 140)
        image(enemy_image, width/2 - 45, height/2 - 170)

    if slide == 0:
        title_screen()
    
    elif slide == 1:
        tutorial_screen()

    elif slide == 2:
        landscape.resize(0, 800)
        image(landscape, map_offset[0], map_offset[1])
        draw_world_user(PLAYER_POS_WORLD[0], PLAYER_POS_WORLD[1], 13)
        if movement:
            map_offset = user_movement(-1.5, map_offset, [38, 40, 37, 39], keys_pressed)
            map_offset = movement_boundaries(map_offset, WORLD_BOUNDARIES, 10)

        if map_offset[0] <= enemy.enemy_attributes[4]:
            movement = False
            draw_textbox([11, 324], [629, 468])
            if text_list_index <= 0:
                fill(255)
                textSize(15)
                text(enemy_dialogue[text_list_index], 25, 405)
            else:
                slide += 1

    elif slide == 3:
        draw_textbox([width/2 - 308, height/2 - 4], [width/2 + 308, height/2 + 139])        

        user_choice_pos = [37 + (157 * user_option_selection_counter), 442]
        draw_user(user_choice_pos[0], user_choice_pos[1])
        fill(255)
        textSize(20)
        text(enemy_dialogue[1], 60, 320)

    elif slide == 4:
        draw_textbox([width/2 - 308, height/2 - 4], [width/2 + 308, height/2 + 139])
        fill(255)
        if user_option_selection_counter == 0:
            fight()
            if offset >= 490:
                offset = 0
                time.sleep(0.15)
                slide += 1
        elif user_option_selection_counter == 1:
            print_options(0, 4, enemy.act_choices)
            user_choice_pos = [56 + (151 * option_selection), 320] #problem
            draw_user(user_choice_pos[0], user_choice_pos[1])
        elif user_option_selection_counter == 2:
            print_options(0, 4, user_items.items)
            
            if option_selection > len(user_items.items) - 1:
                option_selection = len(user_items.items) - 1
                
            user_choice_pos = [56 + (151 * option_selection), 320]
            draw_user(user_choice_pos[0], user_choice_pos[1])
        else:   
            if enemy.enemy_attributes[3]:
                time.sleep(0.15)
                slide = 8
            else:
                text("You tried to spare the enemy but it won't budge.", 60, 320)

    elif slide == 5:
        draw_textbox([width/2 - 308, height/2 - 4], [width/2 + 308, height/2 + 139])

        if user_option_selection_counter == 0:
            if enemy.enemy_attributes[1] - user_attack_damage_calc(24.5, 245, offset) < 0:
                enemy.enemy_attributes[1] = 0
            else:
                enemy.enemy_attributes[1] -= user_attack_damage_calc(24.5, 245, offset)
            if enemy.enemy_attributes[1] <= 0:
                time.sleep(1)
                slide = 8
            else:
                offset = 0
                slide += 1
        elif user_option_selection_counter == 1:
            text_index = enemy.act(option_selection)
            
            if text_index == len(enemy_dialogue) - 1:
                text("{}".format(enemy_dialogue[text_index]), 60, 320)
                enemy.enemy_attributes[3] = True
            else:
                text(enemy_dialogue[text_index + 2], 60, 320)

        elif user_option_selection_counter == 2:
            if len(user.items) > 0:
                user.use_item(option_selection, user_items.items, user_items.item_values)
            slide += 1
        else:
            slide += 1

    elif slide == 6:
        draw_fight_box([width/2 - 110, height/2 - 4], [width/2 + 110, height/2 + 139])    
        enemy_attack()
        if user.user_health[0] <= 0:
            time.sleep(0.15)
            slide = 7
        player_pos = user_movement(1.5, player_pos, [38, 40, 37, 39], keys_pressed)
        player_pos = movement_boundaries(player_pos, ENEMY_ATTACK_BOUNDARIES, 13)
        draw_user(player_pos[0], player_pos[1])
        if enemy.collision_immune == True:
            tint(165, 35, 35)
        else:
            noTint()
        
        if enemy.collision_detection(player_pos, 3):
            enemy.collision_immune = True
            enemy.immune_time_start = frameCount
            user.user_health[0] -= ENEMY_DAMAGE
        
        enemy.immunity()


    elif slide == 7:
        lose_screen()

    elif slide == 8:
        if counter == 4:
            final_win_screen()
        else:
            movement = True
            win_screen()

    elif slide == 9:
        counter += 1
        text_list_index = 0
        
        if counter == 1:
            enemy.rosalind()
        elif counter == 2:
            enemy.quack()
        elif counter == 3:
            enemy.desdemona()
        elif counter == 4:
            enemy.gallo()
        else :
            enemy.patch()
        

        offset = 0
        keys_pressed = [False for key_code in range(256)]
        user.user_health[0] = user.user_health[1]
        slide = 2


def title_screen():
    fill(255)
    textSize(80)
    text("Blundertale", width/2 - 205, height/2 + 40)
    textSize(20)
    text("Press 'z' to start", width/2 - 70, height/2 + 70)

def tutorial_screen():
    fill(255)
    textSize(15)
    text("""Welcome to Blundertale! 
1. Use the Arrow Keys to explore the map.
2. Use the Arrow Keys to navigate between options and "z" to select the desired 
option. Use "x" to go back.
3. If you choose "Act", you have 4 options. If you choose the options in the 
correct sequence, you can talk the enemy into calming down, then use the "Mercy" 
option to avoid a fight.
**"Mercy" is useless without first completing "Act".**
4. If you choose to use an item, you can eat food to regain HP. Use wisely, once 
you use one, it's gone!
5. Your HP is displayed above the options, along with the opponent's HP. If you 
choose to fight, it's a battle to the death. Your HP resets before every battle. 
If you choose to fight, you can deal damage and be dealt damage.
a. To deal damage, press "z" and the line will start moving across the screen. 
Press "z" again and it'll stop. The closer you get to the middle line, the more 
damage is dealt! 
b. To dodge enemy attacks, use the arrow keys to maneuver around the obstacles. 
HP is lost for every obstacle you hit.""", width/2 - 298, height/2 - 205)


def battle_screen_display(user_health, enemy_health):
    # Selection boxes
    stroke("#FF8503")
    fill(0)
    rect(width/2 - 308, height/2 + 177, width/2 - 163, height/2 + 227)
    rect(width/2 - 151, height/2 + 177, width/2 - 6, height/2 + 227)
    rect(width/2 + 6, height/2 + 177, width/2 + 151, height/2 + 227)
    rect(width/2 + 163, height/2 + 177, width/2 + 308, height/2 + 227)

    # Selection text
    fill("#FF8503")
    textSize(30)
    text("Fight", width/2 - 260, height/2 + 190, width/2 - 163, height/2 + 235)
    text("Act", width/2 - 103, height/2 + 190, width/2 - 6, height/2 + 235)
    text("Items", width/2 + 54, height/2 + 190, width/2 + 151, height/2 + 235)
    text("Spare", width/2 + 211, height/2 + 190, width/2 + 308, height/2 + 235)

    # Health fractions
    fill(255)
    textSize(16)
    
    try:
        text("Player Health {}/{}".format(user_health[0], user_health[1]), width/2 - 308, height/2 + 165)
    except:
        raise Exception("User's health should contain 2 integers in a list. The list contained '{}'".format(user_health))
    
    try:
        text("Enemy Health {}/{}".format(enemy_health[0], enemy_health[1]), width/2 - 120, height/2 + 165)
    except:
         raise Exception("Enemy's health should contain 2 integers in a list. The list contained '{}'".format(enemy_health))


def draw_fight_box(corner1, corner2):
    fill(0)
    stroke(255)
    strokeWeight(5)
    try:
        rect(corner1[0], corner1[1], corner2[0], corner2[1])
    except: 
        raise Exception("corner1 and corner2 should be lsits, each containing a set of coordinates (ints or floats). corner1 contained '{}'. corner2 contained '{}'.".format(corner1, corner2))


def draw_textbox(corner1, corner2):
    fill(0)
    stroke(255)
    strokeWeight(5)
    rect(corner1[0], corner1[1], corner2[0], corner2[1])


def win_screen():
    fill(255)
    textSize(80)
    text("You Win!", width/2 - 175, height/2 + 40)
    textSize(10)
    text("...we'll get you next time", width/2 + 50, height/2 + 75)


def final_win_screen():
    dialogue = ["You won.", "You've finally escaped.", "The Gallo has been defeated."]
    draw_textbox([11, 324], [629, 468])
    if text_list_index <= 2:
        fill(255)
        text(dialogue[text_list_index], 25, 405)
    else:
        exit()


def lose_screen():
    fill(255)
    textSize(80)
    text("You Lose.", width/2 - 175, height/2 + 40)
    textSize(10)
    text("how unfortunate :)", width/2+85, height/2+75)


def fight(): 
    global offset, slide

    # Box
    fill(0)
    stroke(255)
    strokeWeight(5)
    rect(width/2 - 250, height/2 + 15, width/2 + 250, height/2 + 120)

    # Red line
    stroke(255, 59, 59)
    rect(width/2, height/2 + 15, width/2, height/2 + 120)

    # Moving white bar
    stroke(255)
    strokeWeight(10)
    rect((width/2 - 246) + offset, height/2 + 15, (width/2 - 245) + offset, height/2 + 120)
    
    offset += 2


def user_attack_damage_calc(start, end, hit_location):
    try:
        damage = int(abs(start - (abs(end - hit_location) / 10)))
    except:
        raise Exception("All three arguments should be ints or floats and the start argument can't be 0")

    return damage


def user_movement(speed, position, keys_used, keys_pressed):
    try:
        keys_pressed[keys_used[0]: keys_used[3]]
    except:
        raise Exception("keys_pressed should contain a value for every key code. keys_used should contain 4 key codes (ints).")

    try:
        position[1] - speed
    except:
        raise Exception("position should be a list containing 2 ints/floats. speed should be an int or float value.")

    if keys_pressed[keys_used[0]]:
        position[1] -= speed
    if keys_pressed[keys_used[1]]:
        position[1] += speed
    if keys_pressed[keys_used[2]]:
        position[0] -= speed
    if keys_pressed[keys_used[3]]:
        position[0] += speed

    return position


def movement_boundaries(position, boundary_values, radius):
    try:
        position[1] >= (boundary_values[3] + radius)
    except:
        raise Exception("position should be a list containing 2 ints/floats. boundary_values should be a list containing 3 ints/floats. radius should be an int or float value.")
    
    if not(position[0] >= (boundary_values[2] + radius)):
        position[0] = (boundary_values[2] + radius)
    if not(position[0] <= (boundary_values[0] - radius)):
        position[0] = (boundary_values[0] - radius)
    if not(position[1] >= (boundary_values[3] + radius)):
        position[1] = (boundary_values[3] + radius)
    if not(position[1] <= (boundary_values[1] - radius)):
        position[1] = (boundary_values[1] - radius)
    
    return position


def draw_user(x_pos, y_pos):
    heart.resize(0, 13)
    try:
        image(heart, x_pos, y_pos)
    except:
        raise Exception("x_pos and y_pos should be ints or floats. Respectively, they were '{}' and '{}'.".format(x_pos, y_pos))
    

def draw_world_user(x_pos, y_pos,length):
    global player
    player.resize(0, 55)
    image(player, x_pos, y_pos)


def print_options(min_range, max_range, options_list):
    try:
        slice_list = options_list[min_range: max_range]
    except:
        raise Exception("min_range, max_range should be ints within the length of options_list (needs to be a list).")

    for option in range(0, len(slice_list)):
        text(slice_list[option], 60 + (option * 151), 320)


def keyPressed():
    global keys_pressed
    if slide == 6 or slide == 2:
        keys_pressed[keyCode] = True


def keyReleased():
    global user_option_selection_counter, slide, option_selection, keys_pressed, text_list_index
    if key == "z":
        if slide in [2, 8] and movement is False:
            text_list_index += 1            
        elif slide in [0, 1, 3, 4, 5, 8]:
            time.sleep(0.15)
            slide += 1
    elif key == "x" and slide in [4] and user_option_selection_counter not in [0, 3]:
        slide -= 1

    if slide == 3:
        # Changes option selection counter
        if keyCode == RIGHT and user_option_selection_counter < 3:
            user_option_selection_counter += 1
        elif keyCode == LEFT and user_option_selection_counter > 0:
            user_option_selection_counter -= 1

    elif slide == 4:
        # Changes option selection counter
        if keyCode == RIGHT:
            if user_option_selection_counter == 2 and option_selection < len(user_items.items) - 1:
                option_selection += 1
            elif user_option_selection_counter == 1 and option_selection < 3:
                option_selection += 1
        elif keyCode == LEFT and option_selection > 0:
            option_selection -= 1

    if slide == 6 or slide == 2:
        keys_pressed[keyCode] = False


def mousePressed():
    print(str(mouseX) + ", " + str(mouseY))


class Enemy:
    enemy_attributes = []
    act_choices = []
    act_solution = []
    obstacle_pos = []
    collision_immune = False
    immune_time_start = 0
    IMMUNE_TIME = 70  # Frames

    boxsize = 0
    speed = 0
    ratio_factors = []
    vector_offsets = []
    moving_direction = []

    def patch(self):
        global enemy_dialogue, enemy_attack, enemy_image
        enemy_dialogue = ["Patch blocks the way!", "You will be judged for your every action...", "Patch is annoyed", "Patch is taken aback, surprised.", "Patch smiles at you", "Patch laughs and his arrogant vibe dissolves into a friendly aura."]
        self.enemy_attributes = ["Patch", 1, 50, False, -88]
        self.act_choices = ["Taunt", "Compliment", "Critcize", "Encourage"]
        self.act_solution = ["131", ""]
        enemy_attack = enemy.attack
        enemy_image = loadImage("Patch.png")
        self.boxsize = 67
        self.speed = 1
        self.ratio_factors = [0, 8.3]
        self.vector_offsets = [- 110, 0, - 50, 50] 
        self.moving_direction = [1, 0]

    def rosalind(self):
        global enemy_dialogue, attack_functions, enemy_image
        enemy_dialogue = ["Rosalind stumbles in the way.", "Rosalind apologizes.", "Rosalind cries pitifully", "Rosalind cries out, still frightened", "Rosalind sniffs and wipes away her tears.", "Rosaline finally cracks a smile, she no longer wants to fight."]
        self.enemy_attributes = ["Rosalind", 1, 40, False, -360]  # Still need to change stats and location
        self.act_choices = ["Threaten", "Play", "Smile", "Hug"]
        self.act_solution = ["231", ""]
        enemy_attack = enemy.attack
        enemy_image = loadImage("rosalind.png")
        self.boxsize = 130
        self.speed = 1
        self.ratio_factors = [15.4, 0]
        self.vector_offsets = [- 110, 0, - 50, 50]        
        self.moving_direction = [0, 1]        

    def quack(self):
        global enemy_dialogue, attack_functions, enemy_image
        enemy_dialogue = ["Quack blocks the way!", "Quack gives you an evil grin", "Quack growls at you", "Quack laughs at your defiant attitude", "Quack finds you very amusing", "Quack no longer wants to fight."]
        self.enemy_attributes = ["Quack", 1, 40, False, -582]
        self.act_choices = ["Taunt", "Ignore", "Joke", "Pet"]
        self.act_solution = ["1323", ""]
        enemy_attack = enemy.attack
        enemy_image = loadImage("quack.png")
        self.boxsize = 33
        self.speed = 2
        self.ratio_factors = [0, 10.85]
        self.vector_offsets = [- 110, 0, - 80, 30]        
        self.moving_direction = [1, 0]               

    def desdemona(self):
        global enemy_dialogue, attack_functions, enemy_image
        enemy_dialogue = ["Desdemona blocks the way!", "Desmonda files her nails", "You are ignored", "She glares at you, the insult hits a sore spot", "Desdemona's confidence goes down", "Desdemona is getting scared", "Desdemona cowers in fright."]
        self.enemy_attributes = ["Desdemona", 1, 40, False, -759]
        self.act_choices = ["Threaten", "Cheer", "Insult", "Scare"]
        self.act_solution = ["2023", ""]
        enemy_attack = enemy.attack
        enemy_image = loadImage("desdemona.png")
        self.boxsize = 63
        self.speed = 2
        self.ratio_factors = [0, 8.3]
        self.vector_offsets = [- 110, 0, - 50, 50]        
        self.moving_direction = [1, 0]        

    def gallo(self):
        global enemy_dialogue, attack_functions, enemy_image
        enemy_dialogue = ["Gallo blocks the way!", "Gallo takes your phone", "Gallo transcends this realm of mortals. Your actions are meaningless."]
        self.enemy_attributes = ["Gallo", 1, 300, False, -881]
        self.act_choices = ["Plead", "Reason", "Talk", "Compliment"]
        self.act_solution = ["0", ""]
        enemy_attack = enemy.attack
        enemy_image = loadImage("gallo.png")
        self.boxsize = 164
        self.speed = 2
        self.ratio_factors = [19, 0]
        self.vector_offsets = [- 110, 0, - 80, 80]        
        self.moving_direction = [0, 1]        

    def attack(self):
        global offset, obstacle_pos, ratio, attack_counter, MAX_ATTACK_COUNT, reset, slide
        if attack_counter >= MAX_ATTACK_COUNT:
            enemy.reset()
            slide = 3
            
        if offset < 220:
            offset += self.speed

        fill(255)
        stroke(255)
        strokeWeight(5)
        try:
            self.obstacle_pos = [(width/2) + self.ratio_factors[0] * ratio + self.vector_offsets[0] + self.moving_direction[0] * offset, 
            (height/2) + self.ratio_factors[1] * ratio + self.vector_offsets[1] + self.moving_direction[1] * offset, 
            (width/2) + self.ratio_factors[0] * ratio + self.vector_offsets[2] + self.moving_direction[0] * offset, 
            (height/2) + self.ratio_factors[1] * ratio + self.vector_offsets[3] + self.moving_direction[1] * offset]
        except:
            raise Exception("offset and ratio need to be ints or floats.")
        try:
            rect(self.obstacle_pos[0], self.obstacle_pos[1], self.obstacle_pos[2], self.obstacle_pos[3])
        except:
            raise Exception("obstacle_pos needs to be a list containing ints or floats of at least 2 corners of an obstacle.")
        
        if offset >= 220 - self.boxsize:
            offset = 0
            ratio = random.randint(0, 10) 
            attack_counter += 1         
               
    def act(self, act_index):
        index = 0
        number_correct_choices = 0

        try:
            self.act_solution[1]
        except:
            raise Exception("act_solution should contain 2 strings in a list.")
        else:
            if self.act_solution[1] == "":
                self.act_solution[1] = str(act_index)
            else:
                self.act_solution[1] += str(act_index)

        fill(255)
        for action in range(0, len(self.act_solution[0])):
            if self.act_solution[1][index + 1:].count(self.act_solution[0][action]) > 0:
                index = self.act_solution[1][index:].find(self.act_solution[0][action])
                number_correct_choices += 1
            else:
                return number_correct_choices
        else:
            return len(enemy_dialogue) - 1

    def collision_detection(self, player_pos, radius):
        for coordinate in range(0, len(self.obstacle_pos), 4):
            try:
                player_pos[0] >= self.obstacle_pos[coordinate] and player_pos[0] <= self.obstacle_pos[coordinate + 2] \
                and player_pos[1] >= self.obstacle_pos[coordinate + 1] and player_pos[1] <= self.obstacle_pos[coordinate + 3] \
                    and self.collision_immune is False
            except:
                raise Exception("player_pos should contain the x and y pos (ints) of player in a list as separate elements. obstacle_pos should contain the location (x1, y1, x2, y2) of every obstacle as separate elements in a list.")
            else:
                if player_pos[0] - radius >= self.obstacle_pos[coordinate] and player_pos[0] + radius <= self.obstacle_pos[coordinate + 2] \
                    and player_pos[1] - radius >= self.obstacle_pos[coordinate + 1] and player_pos[1] + radius <= self.obstacle_pos[coordinate + 3] \
                        and self.collision_immune is False:
                    return True
        else:
            return False

    def immunity(self):
        if self.collision_immune:
            try:
                frameCount - self.immune_time_start >= self.IMMUNE_TIME
            except:
                raise Exception("immune_time_start and IMMUNE_TIME should be ints or floats.")
            else:
                if frameCount - self.immune_time_start >= self.IMMUNE_TIME:
                    self.collision_immune = False
                    self.immune_time_start = 0
            
    def reset(self):
        global offset, user, keys_pressed, player_pos, slide, user_color, attack_counter

        self.obstacle_pos = []
        offset = 0
        keys_pressed = [False for key_code in range(256)]
        player_pos = [320, 308]
        user_color = "#FF0000"
        time.sleep(0.25)
        noTint()
        self.collision_immune = False
        attack_counter = 0


class User:
    user_health = []
    
    def __init__(self, health):
        self.user_health = health

    def use_item(self, item_index, list_items, list_item_values):
        try:
            value = list_item_values[item_index]
        except:
            raise Exception("item_index needs to be an int smaller than the length of list_item_values (needs to be list)")
        (list_item_values).pop(item_index)

        try:
            (list_items).pop(item_index)
        except:
            raise Exception("item_index needs to be an int smaller than the length of list_items (needs to be list)")

        try:
            self.user_health[0] += value
        except:
            raise Exception("user_health needs to be a list that contains only ints or floats.")

        try:
            self.user_health[0] > self.user_health[1]
        except:
            raise Exception("user_health needs 2 int or float elements.")
        else:
            if self.user_health[0] > self.user_health[1]:
                self.user_health[0] = self.user_health[1]


class Item:
    items = []
    item_values = []

    def __init__(self, item_list, health_values):
        self.items = item_list
        self.item_values = health_values


class Tests():
    def test_user_attack_damage_calc(self):
        assert user_attack_damage_calc(1, 10, 5) == 1,  "Should return 1"
        assert user_attack_damage_calc(3, 56, 5) == 2,  "Should return 2"
        assert user_attack_damage_calc(34, 200, 123) == 27,  "Should return 27"

    def test_user_movement(self):
        test_keys_pressed = keys_pressed
        assert user_movement(1, [230, 480], [38, 40, 37, 39], test_keys_pressed) == [230, 480], "There should be no change"
        test_keys_pressed[38] = True
        assert user_movement(1, [230, 480], [38, 40, 37, 39], test_keys_pressed) == [230, 479], "y position should decrease by 1"
        test_keys_pressed[38] = False
        test_keys_pressed[40] = True
        assert user_movement(3, [230, 480], [38, 40, 37, 39], test_keys_pressed) == [230, 483], "y position should increase by 3"
        test_keys_pressed[40] = False
        test_keys_pressed[37] = True
        assert user_movement(2, [230, 480], [38, 40, 37, 39], test_keys_pressed) == [228, 480], "x position should decrease by 2"
        test_keys_pressed[37] = False
        test_keys_pressed[39] = True
        assert user_movement(10, [230, 480], [38, 40, 37, 39], test_keys_pressed) == [240, 480], "x position should increase by 1"

    def test_movement_boundaries(self):
        assert movement_boundaries([230, 480], [430, 379, 210, 236], 10) == [230, 369], "y position should change to 369"
        assert movement_boundaries([230, 200], [430, 379, 210, 236], 10) == [230, 246], "y position should change to 24"
        assert movement_boundaries([500, 480], [430, 379, 210, 236], 10) == [420, 369], "x position should change to 420"
        assert movement_boundaries([100, 480], [430, 379, 210, 236], 10) == [220, 369], "x position should change to 220"

    def test_enemy_patch(self):
        test_enemy_class = Enemy()
        test_enemy_class.patch()
        assert enemy_dialogue == ["Patch blocks the way!", "You will be judged for your every action...", "Patch is annoyed", "Patch is taken aback, surprised.", "Patch smiles at you", "Patch laughs and his arrogant vibe dissolves into a friendly aura."], "Should be given Patch's dialogue"
        assert test_enemy_class.enemy_attributes == ["Patch", 1, 50, False, -88], "Should be given Patch stats and location"
        assert test_enemy_class.act_choices == ["Taunt", "Compliment", "Critcize", "Encourage"], "Should be given actions user can do against Patch and solution to problem"
      
    def test_enemy_rosalind(self):
        test_enemy_class = Enemy()
        test_enemy_class.rosalind()
        assert enemy_dialogue == ["Rosalind stumbles in the way.", "Rosalind apologizes.", "Rosalind cries pitifully", "Rosalind cries out, still frightened", "Rosalind sniffs and wipes away her tears.", "Rosaline finally cracks a smile, she no longer wants to fight."], "Should be given Rosalind's dialogue"
        assert test_enemy_class.enemy_attributes == ["Rosalind", 1, 40, False, -360], "Should be given Rosalind stats and location"
        assert test_enemy_class.act_choices == ["Threaten", "Play", "Smile", "Hug"], "Should be given actions user can do against Rosalind and solution to problem"
        
    def test_enemy_quack(self):
        test_enemy_class = Enemy()
        test_enemy_class.patch()
        assert enemy_dialogue == ["Quack blocks the way!", "Quack gives you an evil grin", "Quack growls at you", "Quack laughs at your defiant attitude", "Quack finds you very amusing", "Quack no longer wants to fight."], "Should be given Quack's dialogue"
        assert test_enemy_class.enemy_attributes == ["Quack", 1, 40, False, -582], "Should be given Quack stats and location"
        assert test_enemy_class.act_choices == ["Taunt", "Ignore", "Joke", "Pet"], "Should be given actions user can do against Quack and solution to problem"
      
    def test_enemy_desdemona(self):
        test_enemy_class = Enemy()
        test_enemy_class.patch()
        assert enemy_dialogue == ["Desdemona blocks the way!", "Desmonda files her nails", "You are ignored", "She glares at you, the insult hits a sore spot", "Desdemona's confidence goes down", "Desdemona is getting scared", "Desdemona cowers in fright."], "Should be given Desdemona's dialogue"
        assert test_enemy_class.enemy_attributes == ["Desdemona", 1, 40, False, -759], "Should be given Desdemona stats and location"
        assert test_enemy_class.act_choices == ["Threaten", "Cheer", "Insult", "Scare"], "Should be given actions user can do against Desdemona and solution to problem"
      
    def test_enemy_gallo(self):
        test_enemy_class = Enemy()
        test_enemy_class.patch()
        assert enemy_dialogue == ["Gallo blocks the way!", "Gallo takes your phone", "Gallo transcends this realm of mortals. Your actions are meaningless."], "Should be given Gallo's dialogue"
        assert test_enemy_class.enemy_attributes == ["Gallo", 1, 300, False, -881], "Should be given Gallo stats and location"
        assert test_enemy_class.act_choices == ["Plead", "Reason", "Talk", "Compliment"], "Should be given actions user can do against Gallo and solution to problem"
      
    def test_enemy_act(self):
        test_enemy_class = Enemy()
        test_enemy_class.patch()
        assert test_enemy_class.act(3) == 0, "Should return a text index"
        assert test_enemy_class.act(4) == 0, "Should return a text index"
        test_enemy_class.act_solution[1] = "13"
        assert test_enemy_class.act(1) == 5, "Should return the number of correct choices"
    
    def test_enemy_collision_detection(self):
        test_enemy_class = Enemy()
        test_enemy_class.obstacle_pos = [100, 200, 300, 400]
        assert test_enemy_class.collision_detection([0, 300], 4) == False, "Should return False"
        assert test_enemy_class.collision_detection([150, 300], 2) == True, "Should return True"
        assert test_enemy_class.collision_detection([300, 0], 3) == False, "Should return False"
        assert test_enemy_class.collision_detection([200, 300], 0) == True, "Should return False"
        
    def test_immunity(self):
        test_enemy_class = Enemy()
        test_enemy_class.collision_immune = True
        test_enemy_class.immunity()
        assert test_enemy_class.collision_immune == True, "Should return True"
        
    def test_reset(self):
        test_enemy_class = Enemy()
        test_enemy_class.reset()
        assert test_enemy_class.obstacle_pos == [], "Should be set to an empty list"
        assert offset == 0, "Should be set to 0"
        assert keys_pressed == [False for key_code in range(256)], "Should be set to a list that contains 256 False elements"
        assert player_pos == [320, 308], "Should be set to [320, 308]"
        assert user_color == "#FF0000", "Should be set to #FF0000"
        assert test_enemy_class.collision_immune == False, "Should be set to False"
        assert attack_counter == 0, "Should be set to 0"
        
    def test_use_item(self):
        test_user_class = User([1, 20])
        list_items = [0, 1, 2, 3]
        list_item_values = [0, 1, 2, 3]
        test_user_class.use_item(2, list_items, list_item_values)
        assert test_user_class.user_health == [3, 20], "Should be changed to [3, 20]"
        assert list_items == [0, 1, 3], "Should remove 2 from list"
        assert list_item_values == [0, 1, 3], "Should remove 2 from list"
