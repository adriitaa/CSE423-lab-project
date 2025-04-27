from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

window_width, window_height = 1000, 800
camera_angle_y = 0
camera_angle_x = 30

road_boundary = 800
line_height = 0.1
line_length = 50
gap_length = 30
road_segments = 50
road_segment_length = 100

car_scale = 0.4
camera_height = 15 * car_scale
camera_distance = 20 * car_scale

car_pos = [0, 0.6 * car_scale, 0]
car_speed = 0
car_rotation = 0
car_turn_speed = 2.0

clouds = []
num_clouds = 20
cloud_speed = 0.1
spheres_per_cloud = 5

first_person_mode = False
day_night_factor = 1.0
weather_mode = 'normal'
obstacles = []
game_over = False
score=0
collision_count=0


# Helper function
def render_bitmap_string(x, y, font, string):
    glRasterPos2f(x, y)
    for c in string:
        glutBitmapCharacter(font, ord(c))



def generate_obstacles():
    global obstacles, road_boundary, road_segments, road_segment_length, car_pos, car_scale

    obstacle_generation_distance = 500
    min_z = car_pos[2] + 50 * car_scale
    max_z = car_pos[2] + obstacle_generation_distance
    num_obstacles = random.randint(3, 7)
    for _ in range(num_obstacles):
        x = random.uniform(-road_boundary + 5 * car_scale, road_boundary - 5 * car_scale)
        z = random.uniform(min_z, max_z)
        size = random.uniform(1 * car_scale, 3 * car_scale)
        color = random.choice([(1.0, 1.0, 0.0), (0.0, 1.0, 0.0)])
        obstacles.append([x, 0.5 * size, z, size, color])



for i in range(num_clouds):
    x = random.uniform(-road_boundary * 3, road_boundary * 3)
    y = random.uniform(200, 500)
    z = random.uniform(-road_boundary * 3, road_boundary * 3)
    size = random.uniform(50, 150)
    cloud_parts = []
    for j in range(spheres_per_cloud):
        offset_x = random.uniform(-0.3 * size, 0.3 * size)
        offset_y = random.uniform(-0.2 * size, 0.2 * size)
        offset_z = random.uniform(-0.3 * size, 0.3 * size)
        radius = random.uniform(0.3 * size, 0.5 * size)
        cloud_parts.append((offset_x, offset_y, offset_z, radius))
    clouds.append([x, y, z, size, cloud_parts])


def draw_cloud(cloud_data):
    x, y, z, size, cloud_parts = cloud_data
    glColor4f(1.0, 1.0, 1.0, 0.8)
    glPushMatrix()
    glTranslatef(x, y, z)
    for part in cloud_parts:
        offset_x, offset_y, offset_z, radius = part
        glTranslatef(offset_x, offset_y, offset_z)
        glutSolidSphere(radius, 15, 15)
        glTranslatef(-offset_x, -offset_y, -offset_z)
    glPopMatrix()


def create_bullet():
    global bullets, car_pos, gun_angle
    bx = car_pos[0] + math.sin(math.radians(gun_angle)) * gun_length
    by = car_pos[1] + 0.5 * car_scale
    bz = car_pos[2] + math.cos(math.radians(gun_angle)) * gun_length
    bradius = 0.2 * car_scale
    bullets.append([bx, by, bz, bradius])

def move_bullets():
    global bullets
    for bullet in bullets:
        bullet[0] += 5 * math.sin(math.radians(gun_angle))
        bullet[2] -= 5 * math.cos(math.radians(gun_angle))



def draw_circle(radius_x, radius_y, center_x, center_y):
    glBegin(GL_POLYGON)
    glVertex3f(center_x, 0, center_y)
    for i in range(361):
        angle = i * 2 * math.pi / 360
        x = radius_x * math.cos(angle)
        y = radius_y * math.sin(angle)
        glVertex3f(center_x + x, 0, center_y + y)
    glEnd()


def draw_car():
    glPushMatrix()
    glTranslatef(car_pos[0], car_pos[1], car_pos[2])
    glRotatef(car_rotation, 0, 1, 0)
    glScalef(car_scale, car_scale, car_scale)

    # Base (Dark Red)
    glColor3f(0.6, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-1.5, 0.0, 2.0)
    glVertex3f(1.5, 0.0, 2.0)
    glVertex3f(1.5, 0.5, -2.0)
    glVertex3f(-1.5, 0.5, -2.0)
    glEnd()

    # Upper Body (Medium Red)
    glColor3f(0.8, 0.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-1.3, 0.5, 1.5)
    glVertex3f(1.3, 0.5, 1.5)
    glVertex3f(1.3, 1.2, -1.0)
    glVertex3f(-1.3, 1.2, -1.0)
    glEnd()

    # Roof (Light Red)
    glColor3f(1.0, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-1.0, 1.2, 0.8)
    glVertex3f(1.0, 1.2, 0.8)
    glVertex3f(0.8, 1.8, -0.5)
    glVertex3f(-0.8, 1.8, -0.5)
    glEnd()

    # Front Hood Slope (Medium Red)
    glColor3f(0.8, 0.0, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-1.3, 0.5, 1.5)
    glVertex3f(1.3, 0.5, 1.5)
    glVertex3f(0.0, 1.0, 2.5)
    glEnd()

    # Rear Trunk Slope (Medium Red)
    glColor3f(0.8, 0.0, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-1.3, 0.8, -1.5)
    glVertex3f(1.3, 0.8, -1.5)
    glVertex3f(0.0, 1.2, -2.0)
    glEnd()

    # Windows (Light Gray)
    glColor4f(0.8, 0.8, 0.8, 0.7)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Front Windshield
    glBegin(GL_QUADS)
    glVertex3f(-0.8, 1.3, 1.0)
    glVertex3f(0.8, 1.3, 1.0)
    glVertex3f(0.6, 1.7, 0.2)
    glVertex3f(-0.6, 1.7, 0.2)
    glEnd()

    # Side Windows
    glBegin(GL_QUADS)
    glVertex3f(1.2, 0.7, 0.8)
    glVertex3f(1.2, 1.1, -0.8)
    glVertex3f(0.9, 1.1, -0.6)
    glVertex3f(0.9, 0.7, 1.0)
    glEnd()

    glBegin(GL_QUADS)
    glVertex3f(-1.2, 0.7, 0.8)
    glVertex3f(-1.2, 1.1, -0.8)
    glVertex3f(-0.9, 1.1, -0.6)
    glVertex3f(-0.9, 0.7, 1.0)
    glEnd()

    # Rear Window (Keep the existing rear window)
    glBegin(GL_QUADS)
    glVertex3f(-0.7, 1.3, -0.7)
    glVertex3f(0.7, 1.3, -0.7)
    glVertex3f(0.5, 1.6, -1.2)
    glVertex3f(-0.5, 1.6, -1.2)
    glEnd()

    glDisable(GL_BLEND)

    # Rear Black Glasses
    glColor3f(0.1, 0.1, 0.1)  # Black color
    glass_width = 0.3
    glass_height = 0.2
    glass_y_offset = 0.7
    glass_z_position = -2.0  # Further back

    # Left Rear Glass
    glBegin(GL_QUADS)
    glVertex3f(-0.8, glass_y_offset, glass_z_position)
    glVertex3f(-0.5, glass_y_offset, glass_z_position)
    glVertex3f(-0.5, glass_y_offset + glass_height, glass_z_position)
    glVertex3f(-0.8, glass_y_offset + glass_height, glass_z_position)
    glEnd()

    # Right Rear Glass
    glBegin(GL_QUADS)
    glVertex3f(0.5, glass_y_offset, glass_z_position)
    glVertex3f(0.8, glass_y_offset, glass_z_position)
    glVertex3f(0.8, glass_y_offset + glass_height, glass_z_position)
    glVertex3f(0.5, glass_y_offset + glass_height, glass_z_position)
    glEnd()

    # Wheels (Black)
    glColor3f(0.1, 0.1, 0.1)
    wheel_radius_x = 0.4
    wheel_radius_y = 0.4
    wheel_positions = [
        [-1.0, 0.0, 1.2],
        [1.0, 0.0, 1.2],
        [-1.0, 0.0, -1.2],
        [1.0, 0.0, -1.2],
    ]
    for pos in wheel_positions:
        draw_circle(wheel_radius_x, wheel_radius_y, pos[0], pos[2])

    glPopMatrix()


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, window_width / window_height, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if first_person_mode:
        look_x = car_pos[0] + 5 * car_scale * math.sin(math.radians(car_rotation))
        look_y = car_pos[1] + 1.5 * car_scale
        look_z = car_pos[2] - 5 * car_scale * math.cos(math.radians(car_rotation))
        gluLookAt(
            car_pos[0], car_pos[1] + 1.5 * car_scale, car_pos[2],
            look_x, look_y, look_z,
            0, 1, 0
        )
    else:

        camera_x = car_pos[0] - 10 * car_scale * math.sin(math.radians(car_rotation + camera_angle_y))
        camera_y = car_pos[1] + camera_height  # Using camera_height for vertical adjustment
        camera_z = car_pos[2] + 10 * car_scale * math.cos(math.radians(car_rotation + camera_angle_y))

        look_x = car_pos[0] + 15 * car_scale * math.sin(math.radians(car_rotation + camera_angle_y))
        look_y = car_pos[1] + 2 * car_scale
        look_z = car_pos[2] - 15 * car_scale * math.cos(math.radians(car_rotation + camera_angle_y))

        gluLookAt(
            camera_x, camera_y, camera_z,
            look_x, look_y, look_z,
            0, 1, 0
        )



def draw_field():
    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-road_boundary * 2, -0.1, -road_boundary * 2)
    glVertex3f(road_boundary * 2, -0.1, -road_boundary * 2)
    glVertex3f(road_boundary * 2, -0.1, road_boundary * 2)
    glVertex3f(-road_boundary * 2, -0.1, -road_boundary * 2)
    glEnd()


def draw_gun():
    glPushMatrix()
    glTranslatef(car_pos[0], car_pos[1] + 1.0 * car_scale, car_pos[2])  
    glRotatef(gun_angle, 0, 1, 0)  # Rotate the gun based on car's gun angle

    glColor3f(0.5, 0.5, 0.5)  # Gray color for the gun
    glBegin(GL_QUADS)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 3 * car_scale)  # Gun length
    glVertex3f(0.1, 0, 3 * car_scale)
    glVertex3f(0.1, 0, 0)
    glEnd()

    glPopMatrix()


def draw_track():
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    for i in range(road_segments):
        z = i * road_segment_length
        glVertex3f(-road_boundary, 0, z)
        glVertex3f(road_boundary, 0, z)
        glVertex3f(road_boundary, 0, z + road_segment_length)
        glVertex3f(-road_boundary, 0, z + road_segment_length)
    glEnd()
    draw_lines()


def draw_lines():
    glColor3f(1, 1, 1)
    glLineWidth(5)
    draw_dashed_line(0)
    draw_dashed_line(-road_boundary + 10)
    draw_dashed_line(road_boundary - 10)


def draw_dashed_line(x_position):
    z = -road_segment_length
    while z < road_segments * road_segment_length:
        glBegin(GL_LINES)
        glVertex3f(x_position, line_height, z)
        glVertex3f(x_position, line_height, z + line_length)
        glEnd()
        z += line_length + gap_length



def draw_obstacle(obstacle):
    x, y, z, size, color = obstacle
    glColor3fv(color)  # Use the obstacle's color
    glPushMatrix()
    glTranslatef(x, y, z)
    glutSolidCube(size)  # Draw the obstacle as a cube
    glPopMatrix()


def check_collision():
    global car_pos, car_scale, obstacles, game_over, collision_count  # Declare the global variable
    if game_over:
        return False
    car_radius = 1.5 * car_scale  # Approximate car radius
    for obstacle in obstacles:
        ox, oy, oz, osize, _ = obstacle
        obstacle_radius = osize / 2.0
        distance = math.sqrt(
            (car_pos[0] - ox) ** 2 +
            (car_pos[1] - oy) ** 2 +  # Basic 2D collision for simplicity
            (car_pos[2] - oz) ** 2
        )
        if distance < car_radius + obstacle_radius:
            collision_count += 1  # Increment the collision count
            if collision_count >= 3:
                game_over = True
                print(f"Game Over! Collision count reached 3. Final Score: {score}")
            return True
    return False



def reset_game():
    global car_pos, car_speed, car_rotation, game_over, collision_count, obstacles, score
    car_pos = [0, 0.6 * car_scale, 0]
    car_speed = 0
    car_rotation = 0
    game_over = False
    collision_count = 0
    obstacles = []
    generate_obstacles()  # Generate obstacles at the start of the game
    score = 0  # Reset score when restarting



def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)

    if weather_mode == 'normal':
        glClearColor(0.5 * day_night_factor, 0.8 * day_night_factor, 1.0 * day_night_factor, 1.0)
    elif weather_mode == 'rainy':
        glClearColor(0.3 * day_night_factor, 0.3 * day_night_factor, 0.4 * day_night_factor, 1.0)

    setup_camera()
    draw_field()
    draw_track()
    for cloud in clouds:
        draw_cloud(cloud)
    draw_car()
    for obstacle in obstacles:
        draw_obstacle(obstacle)

    if game_over:
        # Basic on-screen display (terminal is more reliable for now)
        glColor3f(1.0, 0.0, 0.0)
        render_bitmap_string(window_width // 2 - 50, window_height // 2, GLUT_BITMAP_TIMES_ROMAN_24, "Game Over")
        glColor3f(1.0, 1.0, 1.0)
        render_bitmap_string(window_width // 2 - 80, window_height // 2 - 30, GLUT_BITMAP_HELVETICA_18,
                             f"Final Score: {score}")
        glColor3f(1.0, 1.0, 1.0)
        render_bitmap_string(window_width // 2 - 80, window_height // 2 - 60, GLUT_BITMAP_HELVETICA_18,
                             "Press 'r' to restart")

    glutSwapBuffers()



def update(value):
    global car_pos, clouds, game_over, obstacles, score

    if not game_over:

        car_pos[0] += car_speed * math.sin(math.radians(car_rotation))
        car_pos[2] -= car_speed * math.cos(math.radians(car_rotation))


        if car_pos[0] > road_boundary - 2 * car_scale:
            car_pos[0] = road_boundary - 2 * car_scale
        elif car_pos[0] < -road_boundary + 2 * car_scale:
            car_pos[0] = -road_boundary + 2 * car_scale


        check_collision()


        obstacles = [obs for obs in obstacles if obs[2] > car_pos[2] - 10 * car_scale]


        if random.random() < 0.02:
            generate_obstacles()


        score += 1


    for i in range(len(clouds)):
        clouds[i][2] += cloud_speed
        if clouds[i][2] > road_boundary * 3:
            clouds[i][2] = -road_boundary * 3
            clouds[i][0] = random.uniform(-road_boundary * 3, road_boundary * 3)
            clouds[i][1] = random.uniform(200, 500)


    glutPostRedisplay()


    glutTimerFunc(30, update, 0)




def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.5, 0.8, 1.0, 1.0)
    generate_obstacles()



# Helper function
def render_bitmap_string(x, y, font, string):
    glRasterPos2f(x, y)
    for c in string:
        glutBitmapCharacter(font, ord(c))

def special_keys(key, x, y):
    global camera_angle_x, camera_angle_y, camera_height

    if not first_person_mode:
        if key == GLUT_KEY_UP:
            camera_height += 1 * car_scale
        elif key == GLUT_KEY_DOWN:
            camera_height -= 1 * car_scale
        elif key == GLUT_KEY_LEFT:
            camera_angle_y += 2
        elif key == GLUT_KEY_RIGHT:
            camera_angle_y -= 2

    glutPostRedisplay()

def keyboard_keys(key, x, y):
    global car_pos, car_rotation, car_speed, day_night_factor, weather_mode, game_over,score
    speed = 2.0
    turn_speed = 3.0
    day_night_step = 0.05

    if game_over:
        if key == b'r':
            reset_game()
            glutPostRedisplay()
        return

    if key == b'w':
        car_speed = speed
    elif key == b's':
        car_speed = -speed
    elif key == b'a':
        car_pos[0] -= 2 * car_scale
    elif key == b'd':
        car_pos[0] += 2 * car_scale
    elif key == b'l':
        day_night_factor -= day_night_step
        if day_night_factor < 0.1:
            day_night_factor = 0.1
        glutPostRedisplay()
    elif key == b'o':
        day_night_factor += day_night_step
        if day_night_factor > 1.0:
            day_night_factor = 1.0
        glutPostRedisplay()
    elif key == b'n':
        weather_mode = 'normal'
    elif key == b'r':
        weather_mode = 'rainy'
    glutPostRedisplay()


def keyboard_up(key, x, y):
    global car_speed
    if key == b'w' or key == b's':
        car_speed = 0

def mouse_button(button, state, x, y):
    global first_person_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode
        glutPostRedisplay()

if __name__ == '__main__':
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Racing Car Game")
    init()
    glutDisplayFunc(show_screen)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboard_keys)
    glutKeyboardUpFunc(keyboard_up)  # If you have this
    glutMouseFunc(mouse_button)
    glutTimerFunc(30, update, 0)
    glutMainLoop()

