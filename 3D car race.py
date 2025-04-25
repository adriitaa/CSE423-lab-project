from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window_width, window_height = 1000, 800
camera_pos = [0, 500, 1000]

road_boundary = 800
line_height = 0.1
line_length = 50
gap_length = 30

car_pos = [-road_boundary+10, 0, 0]
car_speed = 0


def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(120, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 500, 500, 0, 0, 0, 0, 0, 1)


def draw_field():
    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-road_boundary * 2, road_boundary * 2, -1)
    glVertex3f(road_boundary * 2, road_boundary * 2, -1)
    glVertex3f(road_boundary * 2, -road_boundary * 2, -1)
    glVertex3f(-road_boundary * 2, -road_boundary * 2, -1)
    glEnd()


def draw_track():
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-road_boundary, road_boundary, 0)
    glVertex3f(road_boundary, road_boundary, 0)
    glVertex3f(road_boundary, -road_boundary, 0)
    glVertex3f(-road_boundary, -road_boundary, 0)
    glEnd()
    draw_lines()


def draw_lines():
    glColor3f(1, 1, 1)
    glLineWidth(10)
    draw_dashed_line(0)
    draw_dashed_line(-road_boundary+10)
    draw_dashed_line(road_boundary-10)


def draw_dashed_line(position):
    y = -road_boundary
    y_prime = road_boundary
    temp = y
    while temp < y_prime:
        glBegin(GL_LINES)
        glVertex3f(position, temp, line_height)
        glVertex3f(position, temp+line_length, line_height)
        glEnd()
        temp += line_length + gap_length


def show_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setup_camera()
    draw_field()
    draw_track()
    glutSwapBuffers()


def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.8, 1.0, 1.0)  # Sky blue


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"3D Racing Car Game")
    init()
    glutDisplayFunc(show_screen)
    glutMainLoop()


if __name__ == "__main__":
    main()
