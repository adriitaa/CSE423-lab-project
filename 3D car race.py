from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

window_width, window_height = 1000, 800
camera_angle_y = 0
camera_angle_x = 30  # Initial downward angle

road_boundary = 800
line_height = 0.1
line_length = 50
gap_length = 30
road_segments = 50
road_segment_length = 100

car_scale = 0.4 # Define car_scale first
camera_height = 15 * car_scale # Initial camera height (now car_scale is defined)
camera_distance = 20 * car_scale # Initial distance behind (now car_scale is defined)

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
        # Driver's view perspective with adjustable angle and height
        camera_x = car_pos[0] - 10 * car_scale * math.sin(math.radians(car_rotation + camera_angle_y))
        camera_y = car_pos[1] + camera_height # Using camera_height for vertical adjustment
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


def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, window_width, window_height)
    setup_camera()
    draw_field()
    draw_track()
    for cloud in clouds:
        draw_cloud(cloud)
    draw_car()
    glutSwapBuffers()


def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.5, 0.8, 1.0, 1.0)


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


def mouse_button(button, state, x, y):
    global first_person_mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode
        glutPostRedisplay()


def keyboard_keys(key, x, y):
    global car_pos, car_rotation, car_speed, day_night_factor, weather_mode
    speed = 2.0
    turn_speed = 3.0
    day_night_step = 0.05

    if key == b'w':
        car_speed = speed
    elif key == b's':
        car_speed = -speed
    elif key == b'a':
        car_rotation += turn_speed
    elif key == b'd':
        car_rotation -= turn_speed
    elif key == b'l':  # Light to dark (Day to Night)
        day_night_factor -= day_night_step
        if day_night_factor < 0.1:
            day_night_factor = 0.1
    elif key == b'o':  # Dark to light (Night to Day)
        day_night_factor += day_night_step
        if day_night_factor > 1.0:
            day_night_factor = 1.0
    elif key == b'n':
        weather_mode = 'normal'
    elif key == b'r':
        weather_mode = 'rainy'

    glutPostRedisplay()



def keyboard_up(key, x, y):
    global car_speed
    if key == b'w' or key == b's':
        car_speed = 0


def update(value):
    global car_pos, clouds
    car_pos[0] += car_speed * math.sin(math.radians(car_rotation))
    car_pos[2] -= car_speed * math.cos(math.radians(car_rotation))

    if car_pos[0] > road_boundary - 2 * car_scale:
        car_pos[0] = road_boundary - 2 * car_scale
    elif car_pos[0] < -road_boundary + 2 * car_scale:
        car_pos[0] = -road_boundary + 2 * car_scale

    for i in range(len(clouds)):
        clouds[i][2] += cloud_speed
        if clouds[i][2] > road_boundary * 3:
            clouds[i][2] = -road_boundary * 3
            clouds[i][0] = random.uniform(-road_boundary * 3, road_boundary * 3)
            clouds[i][1] = random.uniform(200, 500)

    glutPostRedisplay()
    glutTimerFunc(30, update, 0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Racing Car Game")
    init()
    glutDisplayFunc(show_screen)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_button) # Add mouse button callback
    glutKeyboardFunc(keyboard_keys)
    glutKeyboardUpFunc(keyboard_up)
    glutTimerFunc(30, update, 0)
    glutMainLoop()


if __name__ == "__main__":
    main()
