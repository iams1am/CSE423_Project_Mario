from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random
import math  # Don't forget to import the math module!

# Window dimensions
W_Width, W_Height = 500, 500

# Player properties
player_x, player_y = 250, 30  # Player starting on the grass
player_radius = 10
player_lives = 3
player_score = 0
gravity = -3  # Faster gravity effect
jump_strength = 28  # Stronger jump against gravity
player_velocity_y = 0  # Initial vertical velocity
is_paused = False  # Game paused state
player_speed = 50  # Adjust player movement speed

# Box properties
box_width, box_height = 80, 10  # Increase box width
boxes = [
    {"x": 50, "y": 150, "direction": 0},  # Box 1
    {"x": 200, "y": 150, "direction": 0},  # Box 2
    {"x": 350, "y": 150, "direction": 0}   # Box 3
]

# Mushroom properties
mushroom_size = 30  # Increase mushroom size
mushrooms = []

# Trap properties
trap_size = 10
traps = []
trap_speed = 2.0  # Double trap speed

# Grass properties
grass = []
grass_speed = 0.3  # Speed up grass movement

# Game state
game_over = False

class AABB:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

def hasCollided(box1, box2):
    return (box1.x - box1.width / 2) < (box2.x + box2.width / 2) and \
           (box1.x + box1.width / 2) > (box2.x - box2.width / 2) and \
           (box1.y - box1.height / 2) < (box2.y + box2.height / 2) and \
           (box1.y + box1.height / 2) > (box2.y - box2.height / 2)

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def draw_circle(x, y, radius):
    glBegin(GL_POLYGON)
    for i in range(360):
        angle = math.radians(i)
        glVertex2f(x + math.cos(angle) * radius, y + math.sin(angle) * radius)
    glEnd()

def draw_box(x, y, width, height):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_mushroom(x, y):
    # Draw mushroom cap
    glColor3f(1.0, 0.0, 0.0)  # Red color
    draw_box(x - mushroom_size // 2, y, mushroom_size, mushroom_size // 2)
    
    # Draw mushroom stem
    glColor3f(0.5, 0.5, 0.5)  # Grey color
    draw_box(x - mushroom_size // 4, y - mushroom_size // 2, mushroom_size // 2, mushroom_size // 2)
    
    # Draw circle point on the mushroom
    glColor3f(1.0, 1.0, 0.0)  # Yellow color
    draw_circle(x, y + mushroom_size // 4, mushroom_size // 6)

def draw_trap(x, y):
    glColor3f(0.5, 0.5, 0.5)  # Grey color
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + trap_size, y)
    glVertex2f(x + trap_size // 2, y + trap_size)
    glEnd()

def draw_grass(x, y):
    glColor3f(0.0, 1.0, 0.0)  # Green color
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + 10, y)
    glVertex2f(x + 10, y + 5)
    glVertex2f(x, y + 5)
    glEnd()

def iterate():
    glViewport(0, 0, W_Width, W_Height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0.0, W_Width, 0.0, W_Height, 0.0, 1.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    iterate()
    
    # Draw player
    glColor3f(1.0, 1.0, 0.0)  # Yellow color
    draw_circle(player_x, player_y, player_radius)

    # Draw boxes
    glColor3f(1.0, 0.0, 0.0)  # Red color
    for box in boxes:
        draw_box(box["x"], box["y"], box_width, box_height)

    # Draw mushrooms
    for mushroom in mushrooms:
        draw_mushroom(mushroom["x"], mushroom["y"])

    # Draw traps
    for trap in traps:
        draw_trap(trap["x"], trap["y"])

    # Draw grass
    for g in grass:
        draw_grass(g["x"], g["y"])

    # Draw buttons
    glColor3f(1.0, 1.0, 1.0)  # White color
    draw_text(10, W_Height - 20, "End (X)")
    draw_text(100, W_Height - 20, "Pause (P)")
    draw_text(200, W_Height - 20, "Restart (R)")
    draw_text(350, W_Height - 20, f"Lives: {player_lives}  Score: {player_score}")

    if game_over:
        glColor3f(1.0, 0.0, 0.0)  # Red color
        draw_text(W_Width // 2 - 50, W_Height // 2, f"GAME OVER\nScore: {player_score}")

    glutSwapBuffers()

def keyboard_listener(key, x, y):
    global player_x, player_y, player_lives, game_over, player_velocity_y, is_paused
    if key == b'w' and not game_over:
        player_velocity_y = jump_strength  # Jump against gravity
    elif key == b'a' and not game_over:
        player_x -= player_speed
    elif key == b'd' and not game_over:
        player_x += player_speed
    elif key == b'p':
        is_paused = not is_paused  # Toggle pause state
    elif key == b'x':
        exit(0)  # Exit the game
    elif key == b'r':
        reset_game()  # Restart the game

    # Collision detection and scoring logic
    handle_collisions()

    glutPostRedisplay()

def handle_collisions():
    global player_x, player_y, player_lives, player_score, mushrooms, traps, game_over

    player_aabb = AABB(player_x, player_y, player_radius * 2, player_radius * 2)

    # Check for collision with mushrooms
    for mushroom in mushrooms:
        mushroom_aabb = AABB(mushroom["x"], mushroom["y"], mushroom_size, mushroom_size)
        if hasCollided(player_aabb, mushroom_aabb):
            player_score += 1
            mushrooms.remove(mushroom)

    # Check for collision with traps
    for trap in traps:
        trap_aabb = AABB(trap["x"], trap["y"], trap_size, trap_size)
        if hasCollided(player_aabb, trap_aabb):
            player_lives -= 1
            traps.remove(trap)
            if player_lives == 0:
                game_over = True

    if player_y - player_radius < 0:
        player_y = player_radius
        player_velocity_y = 0

    if player_y + player_radius > W_Height:
        player_y = W_Height - player_radius
        player_velocity_y = 0

def spawn_grass():
    global grass
    for x in range(0, W_Width, 10):
        new_grass = {
            "x": x,
            "y": 0  # Align with the bottom of the screen
        }
        grass.append(new_grass)

def spawn_mushroom_or_trap():
    global mushrooms, traps

    # Remove previous mushrooms and traps if they exist
    mushrooms.clear()
    traps.clear()

    if random.random() < 0.5:  # 50% chance to spawn a mushroom or trap
        mushrooms.append({"x": W_Width, "y": 10})  # Lower the mushroom
    else:
        traps.append({"x": W_Width, "y": 10})  # Lower the trap

def respawn_player():
    global player_x, player_y
    player_x, player_y = 250, 30  # Player on the grass

def reset_game():
    global player_x, player_y, player_lives, player_score, game_over, mushrooms, traps, grass
    player_x, player_y = 250, 30  # Player on the grass
    player_lives = 3
    player_score = 0
    game_over = False
    mushrooms = []
    traps = []
    grass = []
    spawn_grass()

def animate():
    global player_y, player_velocity_y, is_paused, player_x

    if not is_paused and not game_over:
        # Update player position with gravity
        player_velocity_y += gravity
        player_y += player_velocity_y

        player_aabb = AABB(player_x, player_y, player_radius * 2, player_radius * 2)

        # Ensure player doesn't fall below the ground
        if player_y - player_radius < 0:
            player_y = player_radius
            player_velocity_y = 0

        # Ensure player doesn't jump out of the screen
        if player_y + player_radius > W_Height:
            player_y = W_Height - player_radius
            player_velocity_y = 0

        # Ensure player moves along with the box if on a box
        on_box = False
        for box in boxes:
            box_aabb = AABB(box["x"] + box_width / 2, box["y"] + box_height / 2, box_width, box_height)
            if hasCollided(player_aabb, box_aabb):
                player_y = box["y"] + box_height + player_radius
                player_velocity_y = 0
                on_box = True
                break

        # If not on any box, apply gravity
        if not on_box:
            player_velocity_y += gravity

        # Move grass, mushrooms, and traps from right to left
        for g in grass:
            g["x"] -= grass_speed
        for mushroom in mushrooms:
            mushroom["x"] -= trap_speed  # High speed for mushrooms
        for trap in traps:
            trap["x"] -= trap_speed  # High speed for traps

        # Remove off-screen elements and spawn new ones
        grass[:] = [g for g in grass if g["x"] > -10]
        mushrooms[:] = [m for m in mushrooms if m["x"] > -mushroom_size]
        traps[:] = [t for t in traps if t["x"] > -trap_size]

        # Loop the grass
        if len(grass) == 0 or grass[-1]["x"] < W_Width - 10:
            spawn_grass()

        # Randomly spawn new mushrooms and traps one at a time
        if len(mushrooms) == 0 and len(traps) == 0 and random.random() < 0.02:
            spawn_mushroom_or_trap()

    glutPostRedisplay()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0.0, W_Width, 0.0, W_Height)

glutInit()
glutInitDisplayMode(GLUT_RGBA)
glutInitWindowSize(W_Width, W_Height)
glutInitWindowPosition(0, 0)
wind = glutCreateWindow(b"OpenGL Game")
init()

glutDisplayFunc(showScreen)
glutIdleFunc(animate)
glutKeyboardFunc(keyboard_listener)

# Initial grass spawn
spawn_grass()

glutMainLoop()
