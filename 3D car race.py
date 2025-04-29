from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

import random
import math
import time

window_width, window_height = 1000, 800
camera_angle_y = 0
camera_angle_x = 30
camera_height_offset = 15
camera_distance_offset = 20
first_person_mode = False

road_boundary = 15
line_height = 0.1
line_length = 15
gap_length = 10
view_distance = 800

car_scale = 0.4
car_pos = [0, 0.6 * car_scale, 0]
car_speed = 0
max_car_speed = 3.0
car_acceleration = 0.1
car_brake_deceleration = 0.2
car_natural_deceleration = 0.02
car_rotation = 0.0
car_turn_speed = 2.0

clouds = []
num_clouds = 20
cloud_speed = 0.1
spheres_per_cloud = 5
day_night_factor = 1.0
weather_mode = 'normal'


raindrops = []
max_raindrops = 800
rain_height = 100
rain_area_size = 150
rain_speed = 1.5
rain_angle = 0.0
rain_color_day = [0.7, 0.7, 0.8, 0.6]
rain_color_night = [0.4, 0.4, 0.5, 0.4]

obstacles = []
obstacle_generation_distance = 400
obstacle_check_distance = 500
min_obstacle_distance = 50
obstacle_spawn_probability = 0.03

game_over = False
score = 0
collision_count = 0
max_collisions = 3

key_states = {}


track_curve_amp   = 10.0

track_curve_freq  = 0.01


hill_amplitude    =  2.0

hill_frequency    =  0.005


track_segments    = 20
camera_zoom = 30.0

#helper function lagbe 
def getCenterX(z):
    return track_curve_amp * math.sin(track_curve_freq * z)

def getRoadHeight(z):
    return hill_amplitude + hill_amplitude * math.sin(hill_frequency * z)

def render_bitmap_string(x, y, z, font, string):
    glRasterPos3f(x, y, z)
    for c in string:
        glutBitmapCharacter(font, ord(c))


def render_bitmap_string_2d(x, y, font, string):
    glWindowPos2f(x, y)
    for c in string:
        glutBitmapCharacter(font, ord(c))


def generate_initial_clouds():
    global clouds
    clouds = []
    for i in range(num_clouds):
        x = random.uniform(-road_boundary * 15, road_boundary * 15)
        y = random.uniform(150, 400)
        z = random.uniform(car_pos[2] - view_distance / 2, car_pos[2] + view_distance)
        size = random.uniform(30, 100)
        cloud_parts = []
        for j in range(spheres_per_cloud):
            offset_x = random.uniform(-0.4 * size, 0.4 * size)
            offset_y = random.uniform(-0.3 * size, 0.3 * size)
            offset_z = random.uniform(-0.4 * size, 0.4 * size)
            radius = random.uniform(0.3 * size, 0.6 * size)
            cloud_parts.append((offset_x, offset_y, offset_z, radius))
        clouds.append([x, y, z, size, cloud_parts])


def generate_obstacles():
    global obstacles

    eps = 0.1  
    min_z = car_pos[2] + min_obstacle_distance * car_scale * 5
    max_z = car_pos[2] + obstacle_generation_distance

   
    obstacles_ahead = sum(1 for obs in obstacles if min_z < obs[2] < max_z)
    if obstacles_ahead > 10:
        return

   
    num_new = random.randint(1, 3)
    for k in range(num_new):
       
        zc = random.uniform(min_z, max_z)
        
        xc = getCenterX(zc)
        yc = getRoadHeight(zc)

      
        dx_dz = (getCenterX(zc + eps) - xc) / eps
        theta  = math.atan2(dx_dz, 1.0)
    
        nx =  math.cos(theta)
        nz = -math.sin(theta)

       
        offs = random.uniform(-road_boundary * 0.8, road_boundary * 0.8)
        x = xc + offs * nx
        z = zc + offs * nz
      
        size = random.uniform(1.5 * car_scale, 4 * car_scale)
        y = yc + 0.5 * size

        color = random.choice([(1.0, 1.0, 0.0),(0.0, 1.0, 0.0),(1.0, 0.5, 0.0),])

        obstacles.append([x, y, z, size, color])



def draw_cloud(cloud_data):
    x, y, z, size, cloud_parts = cloud_data
    cloud_brightness = 0.8 + 0.2 * day_night_factor
    cloud_alpha = 0.6 + 0.2 * day_night_factor
    glColor4f(cloud_brightness, cloud_brightness, cloud_brightness, cloud_alpha)

    glPushMatrix()
    glTranslatef(x, y, z)
    for part in cloud_parts:
        offset_x, offset_y, offset_z, radius = part
        glPushMatrix()
        glTranslatef(offset_x, offset_y, offset_z)
        glutSolidSphere(radius, 15, 15)
        glPopMatrix()
    glPopMatrix()


def draw_circle_wheel(radius, center_x, center_z):
    glBegin(GL_POLYGON)
    num_segments = 20
    for i in range(num_segments + 1):
        angle = i * 2 * math.pi / num_segments
        x = radius * math.cos(angle)
        glVertex3f(center_x + x, 0.05, center_z + radius * math.sin(angle))
    glEnd()


def draw_car():
    glPushMatrix()
    glTranslatef(car_pos[0], car_pos[1], car_pos[2])
    glRotatef(car_rotation, 0, 1, 0)
    glScalef(car_scale, car_scale, car_scale)

    glColor3f(0.6 * day_night_factor, 0.0, 0.0)
    glPushMatrix()
    glScalef(1.5, 0.5, 2.5)
    glTranslatef(0, 0.5, 0)
    glutSolidCube(1.0)
    glPopMatrix()

    glColor3f(0.8 * day_night_factor, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0.75, -0.3)
    glScalef(1.3, 0.5, 1.5)
    glutSolidCube(1.0)
    glPopMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    window_brightness = 0.6 + 0.2 * day_night_factor
    window_alpha = 0.5 + 0.2 * day_night_factor
    glColor4f(window_brightness * 0.8, window_brightness * 0.9, window_brightness, window_alpha)

    glPushMatrix()
    glTranslatef(0, 0.85, 0.45)
    glRotatef(-20, 1, 0, 0)
    glScalef(1.25, 0.4, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0.85, -1.05)
    glRotatef(15, 1, 0, 0)
    glScalef(1.25, 0.4, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-0.65, 0.75, -0.3)
    glScalef(0.05, 0.4, 1.4)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.65, 0.75, -0.3)
    glScalef(0.05, 0.4, 1.4)
    glutSolidCube(1.0)
    glPopMatrix()

    glDisable(GL_BLEND)

    glColor3f(0.1, 0.1, 0.1)
    wheel_radius = 0.4
    wheel_z_front = 1.0
    wheel_z_rear = -1.0
    wheel_x_offset = 1.2

    draw_circle_wheel(wheel_radius, -wheel_x_offset, wheel_z_front)
    draw_circle_wheel(wheel_radius, wheel_x_offset, wheel_z_front)
    draw_circle_wheel(wheel_radius, -wheel_x_offset, wheel_z_rear)
    draw_circle_wheel(wheel_radius, wheel_x_offset, wheel_z_rear)

    glPopMatrix()


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70, window_width / window_height, 0.1, view_distance * 1.5)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    current_camera_height = camera_height_offset * car_scale
    current_camera_distance = camera_distance_offset * car_scale

    if first_person_mode:
        cam_x = car_pos[0] + 0.5 * car_scale * math.sin(math.radians(car_rotation))
        cam_y = car_pos[1] + 1.0 * car_scale
        cam_z = car_pos[2] - 1.2 * car_scale * math.cos(math.radians(car_rotation))

        look_x = cam_x + 20 * car_scale * math.sin(math.radians(car_rotation))
        look_y = cam_y
        look_z = cam_z - 20 * car_scale * math.cos(math.radians(car_rotation))

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)
    else:
        offset_x = current_camera_distance * math.sin(math.radians(car_rotation))
        offset_z = current_camera_distance * math.cos(math.radians(car_rotation))

        cam_x = car_pos[0] - offset_x * math.cos(math.radians(camera_angle_y)) \
                + offset_z * math.sin(math.radians(camera_angle_y))
        cam_z = car_pos[2] + offset_z * math.cos(math.radians(camera_angle_y)) \
                + offset_x * math.sin(math.radians(camera_angle_y))

        cam_y = car_pos[1] + current_camera_height

        look_x = car_pos[0]
        look_y = car_pos[1] + 1.5 * car_scale
        look_z = car_pos[2]

        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 1, 0)


def draw_field():
    ground_brightness = 0.1 + 0.4 * day_night_factor
    glColor3f(0.1, ground_brightness, 0.1)

    plane_size = view_distance * 2
    z_center = car_pos[2]
    y_level = -0.01

    glBegin(GL_QUADS)
    glVertex3f(-plane_size, y_level, z_center - plane_size)
    glVertex3f(plane_size, y_level, z_center - plane_size)
    glVertex3f(plane_size, y_level, z_center + plane_size)
    glVertex3f(-plane_size, y_level, z_center + plane_size)
    glEnd()


def draw_track():
    glColor3f(0.2, 0.2, 0.2)
    z0 = car_pos[2] - view_distance * 0.2
    z1 = car_pos[2] + view_distance
    dz = (z1 - z0) / track_segments

    for i in range(track_segments):
        za = z0 + i * dz
        zb = za + dz

       
        xa, xb = getCenterX(za), getCenterX(zb)
        ya, yb = getRoadHeight(za), getRoadHeight(zb)

       
        eps    = 0.1
        dx_approx = (getCenterX(za + eps) - xa) / eps
        theta  = math.atan2(dx_approx, 1.0)

        
        nx =  math.cos(theta)
        nz = -math.sin(theta)

        
        lx_a, lz_a = xa - road_boundary * nx, za - road_boundary * nz
        rx_a, rz_a = xa + road_boundary * nx, za + road_boundary * nz
        lx_b, lz_b = xb - road_boundary * nx, zb - road_boundary * nz
        rx_b, rz_b = xb + road_boundary * nx, zb + road_boundary * nz

        glBegin(GL_QUADS)
        glVertex3f(lx_a, ya, lz_a)
        glVertex3f(rx_a, ya, rz_a)
        glVertex3f(rx_b, yb, rz_b)
        glVertex3f(lx_b, yb, lz_b)
        glEnd()

    draw_lines()



def draw_lines():
    glColor3f(1, 1, 1)
    glLineWidth(3)

    start_z = math.floor((car_pos[2] - 50) / (line_length + gap_length)) * (line_length + gap_length)
    end_z   = car_pos[2] + view_distance
    z = start_z

    while z < end_z:
        za = z
        zb = z + line_length
        xa, ya = getCenterX(za), getRoadHeight(za) + line_height
        xb, yb = getCenterX(zb), getRoadHeight(zb) + line_height

        glBegin(GL_LINES)
        glVertex3f(xa, ya, za)
        glVertex3f(xb, yb, zb)
        glEnd()

        z += line_length + gap_length






def draw_dashed_line(x_position, start_z, end_z):
    z = start_z
    while z < end_z:
        glBegin(GL_LINES)
        glVertex3f(x_position, line_height, z)
        glVertex3f(x_position, line_height, z + line_length)
        glEnd()
        z += line_length + gap_length


def draw_obstacle(obstacle):
    x, y, z, size, color = obstacle
    adjusted_color = [c * (0.5 + 0.5 * day_night_factor) for c in color]
    glColor3fv(adjusted_color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size * 0.8, size * 1.2, size * 0.8)
    glutSolidCube(1.0)
    glPopMatrix()


def draw_rain():
    if not raindrops:
        return

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    color = rain_color_day if day_night_factor > 0.5 else rain_color_night
    final_color = [
                      c * (0.6 + 0.4 * day_night_factor) for c in color[:3]
                  ] + [color[3] * (0.5 + 0.5 * day_night_factor)]
    glColor4fv(final_color)

    glLineWidth(1.5)

    drop_length = 0.8
    dx = drop_length * math.tan(math.radians(rain_angle))
    dz = 0

    glBegin(GL_LINES)
    for drop in raindrops:
        x, y, z = drop
        glVertex3f(x, y, z)
        glVertex3f(x + dx, y - drop_length, z + dz)
    glEnd()

    glDisable(GL_BLEND)


def handle_continuous_keys():
    global car_speed, car_rotation, day_night_factor

    if game_over:
        global car_speed
        car_speed = 0
        return

    accelerating = False
    braking = False

    if key_states.get(b's'):
        car_speed += car_acceleration
        if car_speed > max_car_speed: car_speed = max_car_speed
        accelerating = True

    if key_states.get(b'w'):
        if car_speed > 0:
            car_speed -= car_brake_deceleration
            if car_speed < 0: car_speed = 0
            braking = True
        else:
            car_speed -= car_acceleration * 0.6
            if car_speed < -max_car_speed * 0.5: car_speed = -max_car_speed * 0.5
            accelerating = True

    if key_states.get(b'a'):
        if abs(car_speed) > 0.1 or True:
            car_rotation += car_turn_speed * (car_speed / max_car_speed if abs(car_speed) > 0.1 else 0.5)
            car_rotation %= 360

    if key_states.get(b'd'):
        if abs(car_speed) > 0.1 or True:
            car_rotation -= car_turn_speed * (car_speed / max_car_speed if abs(car_speed) > 0.1 else 0.5)
            car_rotation %= 360

    day_night_step = 0.005
    if key_states.get(b'o'):
        day_night_factor += day_night_step
        if day_night_factor > 1.0: day_night_factor = 1.0

    if key_states.get(b'l'):
        day_night_factor -= day_night_step
        if day_night_factor < 0.1: day_night_factor = 0.1

def update(value):
    global car_pos, car_speed, car_rotation, clouds, game_over, obstacles, score, day_night_factor, weather_mode, raindrops

    handle_continuous_keys()

    if not game_over:
       
        if car_speed > 0:
            car_speed -= car_natural_deceleration
            if car_speed < 0:
                car_speed = 0
        elif car_speed < 0:
            car_speed += car_natural_deceleration
            if car_speed > 0:
                car_speed = 0

       
        delta_x = car_speed * math.sin(math.radians(car_rotation))
        delta_z = car_speed * math.cos(math.radians(car_rotation))
        car_pos[0] += delta_x
        car_pos[2] -= delta_z


        car_pos[1] = getRoadHeight(car_pos[2]) + 0.6 * car_scale

    
        max_x = road_boundary - 1.5 * car_scale
        if car_pos[0] > max_x:
            car_pos[0] = max_x
            car_speed *= 0.8
        elif car_pos[0] < -max_x:
            car_pos[0] = -max_x
            car_speed *= 0.8

      
        obstacles = [obs for obs in obstacles if obs[2] > car_pos[2] - 50]

      
        max_obs_z = car_pos[2]
        if obstacles:
            max_obs_z = max(obs[2] for obs in obstacles)
        if max_obs_z < car_pos[2] + obstacle_check_distance or random.random() < obstacle_spawn_probability:
            if max_obs_z < car_pos[2] + obstacle_generation_distance:
                generate_obstacles()

       
        check_collision()
        if car_speed != 0:
            score += int(abs(car_speed) * 0.5 + 1)

      
        if weather_mode == 'rainy':
            update_rain()
        else:
            raindrops = []

   
    for i in range(len(clouds)):
        clouds[i][0] -= cloud_speed
        recycle_boundary = road_boundary * 15
        if clouds[i][0] < -recycle_boundary:
            clouds[i][0] = recycle_boundary
            clouds[i][1] = random.uniform(150, 400)
            clouds[i][2] = random.uniform(car_pos[2] - view_distance / 2, car_pos[2] + view_distance)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)




def update_rain():
    global raindrops

    new_raindrops = []
    for i in range(len(raindrops)):
        drop = raindrops[i]
        drop[1] -= rain_speed
        drop[0] += rain_speed * math.tan(math.radians(rain_angle))

        if drop[1] > 0:
            new_raindrops.append(drop)
    raindrops = new_raindrops

    num_new_drops = random.randint(10, 30)
    needed = max_raindrops - len(raindrops)
    num_new_drops = min(num_new_drops, needed)

    for m in range(num_new_drops):
        x = random.uniform(car_pos[0] - rain_area_size / 2, car_pos[0] + rain_area_size / 2)
        y = rain_height
        z = random.uniform(car_pos[2] - rain_area_size / 2, car_pos[2] + rain_area_size / 2)
        raindrops.append([x, y, z])


def check_collision():
    global car_pos, car_scale, obstacles, game_over, collision_count, score
    if game_over:
        return False

    car_width = 1.5 * car_scale
    car_length = 2.5 * car_scale
    car_height = 1.0 * car_scale

    car_front = car_pos[2] - car_length / 2
    car_back = car_pos[2] + car_length / 2
    car_left = car_pos[0] - car_width / 2
    car_right = car_pos[0] + car_width / 2
    car_bottom = car_pos[1] - car_height / 2
    car_top = car_pos[1] + car_height / 2

    collided_obstacle_indices = []

    for i, obstacle in enumerate(obstacles):
        ox, oy_center, oz, osize, _ = obstacle
        obs_half_size = osize / 2.0
        obs_front = oz - obs_half_size
        obs_back = oz + obs_half_size
        obs_left = ox - obs_half_size
        obs_right = ox + obs_half_size
        obs_bottom = oy_center - obs_half_size
        obs_top = oy_center + obs_half_size

        x_overlap = (car_left < obs_right) and (car_right > obs_left)
        z_overlap = (car_front < obs_back) and (car_back > obs_front)
        y_overlap = (car_bottom < obs_top) and (car_top > obs_bottom)

        if x_overlap and z_overlap and y_overlap:
            collision_count += 1
            print(f"Collision detected! Count: {collision_count}")
            collided_obstacle_indices.append(i)

            if collision_count >= max_collisions:
                game_over = True
                print(f"Game Over! Collision limit reached ({max_collisions}). Final Score: {score}")
                global car_speed
                car_speed = 0

    for index in sorted(collided_obstacle_indices, reverse=True):
        print(f"Removing obstacle at index {index}")
        del obstacles[index]

    return len(collided_obstacle_indices) > 0


def reset_game():
    global car_pos, car_speed, car_rotation, game_over, collision_count, obstacles, score, day_night_factor, weather_mode, raindrops, key_states, camera_angle_y, first_person_mode
    print("Resetting game...")
    car_pos = [0, 0.6 * car_scale, 0]
    car_speed = 0
    car_rotation = 0.0
    game_over = False
    collision_count = 0
    score = 0
    obstacles = []
    raindrops = []
    day_night_factor = 1.0
    weather_mode = 'normal'
    key_states = {}  # Clear held keys on reset
    camera_angle_y = 0
    first_person_mode = False
    generate_obstacles()
    generate_initial_clouds()
    print("Game reset complete.")


def show_screen():
    base_color_factor = day_night_factor
    if weather_mode == 'normal':
        glClearColor(0.4 * base_color_factor, 0.7 * base_color_factor, 0.9 * base_color_factor, 1.0)
    elif weather_mode == 'rainy':
        glClearColor(0.3 * base_color_factor, 0.35 * base_color_factor, 0.4 * base_color_factor, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    setup_camera()

    draw_field()
    for cloud in clouds:
        draw_cloud(cloud)

    draw_track()

    for obstacle in obstacles:
        draw_obstacle(obstacle)

    draw_car()

    if weather_mode == 'rainy':
        draw_rain()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, window_width, 0, window_height)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)

    glColor3f(1.0, 1.0, 1.0)

    render_bitmap_string_2d(10, window_height - 30, GLUT_BITMAP_HELVETICA_18, f"Score: {score}")
    render_bitmap_string_2d(10, window_height - 55, GLUT_BITMAP_HELVETICA_18,
                            f"Collisions: {collision_count}/{max_collisions}")
    render_bitmap_string_2d(10, window_height - 80, GLUT_BITMAP_HELVETICA_18, f"Weather: {weather_mode.capitalize()}")
    render_bitmap_string_2d(10, window_height - 105, GLUT_BITMAP_HELVETICA_18, f"Day/Night: {day_night_factor:.2f}")
    if weather_mode == 'rainy':
        render_bitmap_string_2d(10, window_height - 130, GLUT_BITMAP_HELVETICA_18, f"Rain Angle: {rain_angle:.1f}")

    if game_over:
        msg_game_over = "Game Over!"
        msg_score = f"Final Score: {score}"
        msg_restart = "Press 'R' to Restart"

        glColor3f(1.0, 0.2, 0.2)
        render_bitmap_string_2d(window_width // 2 - 60, window_height // 2 + 10, GLUT_BITMAP_TIMES_ROMAN_24,
                                msg_game_over)

        glColor3f(1.0, 1.0, 1.0)
        render_bitmap_string_2d(window_width // 2 - 70, window_height // 2 - 20, GLUT_BITMAP_HELVETICA_18, msg_score)
        render_bitmap_string_2d(window_width // 2 - 80, window_height // 2 - 50, GLUT_BITMAP_HELVETICA_18, msg_restart)

    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

    glutSwapBuffers()


def special_keys(key, x, y):
    global camera_angle_y, camera_height_offset

    if not first_person_mode and not game_over:
        if key == GLUT_KEY_UP:
            camera_height_offset += 1.0
        elif key == GLUT_KEY_DOWN:
            camera_height_offset -= 1.0
            if camera_height_offset < 2: camera_height_offset = 2
        elif key == GLUT_KEY_LEFT:
            camera_angle_y = (camera_angle_y + 3) % 360
        elif key == GLUT_KEY_RIGHT:
            camera_angle_y = (camera_angle_y - 3) % 360


def keyboard_keys_down(key, x, y):
    global game_over, weather_mode, rain_angle, first_person_mode, day_night_factor

    key_states[key] = True

    if key == b'r' and game_over:
        reset_game()
        return
    elif key == b'r' and not game_over:
        weather_mode = 'rainy' if weather_mode == 'normal' else 'normal'
        print(f"Weather changed to: {weather_mode}")
    elif key == b'n':
        weather_mode = 'normal'
        print(f"Weather changed to: {weather_mode}")
    elif key == b't':
        if weather_mode == 'rainy':
            rain_angle += 5.0
            if rain_angle > 45.0:
                rain_angle = -45.0
            print(f"Rain angle changed to: {rain_angle:.1f}")
    elif key == b'f':
        first_person_mode = not first_person_mode
        print(f"Camera mode: {'First Person' if first_person_mode else 'Third Person'}")


def keyboard_keys_up(key, x, y):
    key_states[key] = False


def mouse_button(button, state, x, y):
    global first_person_mode
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode
        print(f"Camera mode: {'First Person' if first_person_mode else 'Third Person'}")


def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    reset_game()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(50, 50)
    wind = glutCreateWindow(b'Enhanced 3D Racing Game')

    init()

    glutDisplayFunc(show_screen)
    glutSpecialFunc(special_keys)
    glutKeyboardFunc(keyboard_keys_down)
    glutKeyboardUpFunc(keyboard_keys_up)
    glutMouseFunc(mouse_button)
    glutTimerFunc(16, update, 0)

    glutMainLoop()


if __name__ == '__main__':
    main()
