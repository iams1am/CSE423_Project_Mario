from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random
import math  # Don't forget to import the math module!

# Window dimensions
W_Width, W_Height = 500, 500

# Player properties
player_x, player_y = 250, 150
player_radius = 10
player_lives = 3
player_score = 0
gravity = -0.01  # 5x slower gravity effect
player_velocity_y = 0  # Initial vertical velocity
is_paused = False  # Game paused state

# Box properties
box_width, box_height = 60, 10
box_speed = 0.05  # Slow down the boxes even more
boxes = [
    {"x": 200, "y": 200, "direction": 1},
    {"x": 270, "y": 200, "direction": -1},
    {"x": 340, "y": 200, "direction": 1}
]

# Mushroom properties
mushroom_size = 30  # Increase mushroom size
mushrooms = []

# Trap properties
trap_size = 10
traps = []

# Game state
game_over = False

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
    glColor3f(0.0, 1.0, 0.0)  # Green color
    glBegin(GL_TRIANGLES)
    glVertex2f(x, y)
    glVertex2f(x + trap_size, y)
    glVertex2f(x + trap_size // 2, y + trap_size)
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

    # Draw buttons
    glColor3f(1.0, 1.0, 1.0)  # White color
    draw_text(10, W_Height - 20, "End (X)")
    draw_text(100, W_Height - 20, "Pause (||)")
    draw_text(200, W_Height - 20, "Restart (R)")
    draw_text(350, W_Height - 20, f"Lives: {player_lives}  Score: {player_score}")

    if game_over:
        glColor3f(1.0, 0.0, 0.0)  # Red color
        draw_text(W_Width // 2 - 50, W_Height // 2, "GAME OVER")

    glutSwapBuffers()

def keyboard_listener(key, x, y):
    global player_x, player_y, player_lives, game_over, player_velocity_y, is_paused
    if key == b'w' and not game_over:
        player_velocity_y = 1  # Jump up
    elif key == b'a' and not game_over:
        player_x -= 20
    elif key == b'd' and not game_over:
        player_x += 20
    elif key == b' ':
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

    # Check for collision with mushrooms
    for mushroom in mushrooms:
        if (player_x > mushroom["x"] - mushroom_size // 2 and player_x < mushroom["x"] + mushroom_size // 2) and \
           (player_y > mushroom["y"] - mushroom_size // 2 and player_y < mushroom["y"] + mushroom_size // 2):
            player_score += 1
            mushrooms.remove(mushroom)
            spawn_mushroom()

    # Check for collision with traps
    for trap in traps:
        if (player_x > trap["x"] - trap_size // 2 and player_x < trap["x"] + trap_size // 2) and \
           (player_y > trap["y"] - trap_size // 2 and player_y < trap["y"] + trap_size // 2):
            player_lives -= 1
            player_lives = max(player_lives, 0)
            if player_lives == 0:
                game_over = True
            else:
                respawn_player()

def spawn_mushroom():
    global mushrooms
    while len(mushrooms) < 4:  # Limit to 3-4 mushrooms
        new_mushroom = {
            "x": random.randint(0, W_Width),
            "y": 10 + mushroom_size // 2  # Ground level
        }
        mushrooms.append(new_mushroom)

def spawn_traps():
    global traps
    for x in range(0, W_Width, trap_size):
        new_trap = {
            "x": x,
            "y": 10  # Ground level
        }
        traps.append(new_trap)

def respawn_player():
    global player_x, player_y
    player_x, player_y = W_Width // 2, 200

def reset_game():
    global player_x, player_y, player_lives, player_score, game_over, mushrooms, traps
    player_x, player_y = 250, 150
    player_lives = 3
    player_score = 0
    game_over = False
    mushrooms = []
    traps = []
    spawn_mushroom()
    spawn_traps()

def animate():
    global boxes, player_y, player_velocity_y, is_paused, player_x

    if not is_paused and not game_over:
        # Update player position with gravity
        player_velocity_y += gravity
        player_y += player_velocity_y

        # Ensure player doesn't fall below the ground
        if player_y - player_radius < 0:
            player_y = player_radius
            player_velocity_y = 0

        # Ensure player moves along with the box if on a box
        on_box = False
        for box in boxes:
            if player_x > box["x"] and player_x < box["x"] + box_width and \
               player_y - player_radius <= box["y"] + box_height and \
               player_y - player_radius >= box["y"]:
                player_y = box["y"] + box_height + player_radius
                player_velocity_y = 0
                on_box = True
                break

        # If not on any box, apply gravity
        if not on_box:
            player_velocity_y += gravity

        # Update boxes positions
        for box in boxes:
            box["y"] += box["direction"] * box_speed
            if box["y"] > 300 or box["y"] < 100:
                box["direction"] *= -1

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

# Initial mushroom and trap spawn
spawn_mushroom()
spawn_traps()

glutMainLoop()
