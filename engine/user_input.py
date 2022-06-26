"""Handles keyboard and mouse inputs in pygame"""


# keyboard
keys = {}
pressed = set()


def key_press(key_event):
    """Sets a key to be pressed"""
    keys[key_event.key] = True
    pressed.add(key_event.key)


def key_release(key_event):
    """Sets a key to be released"""
    keys[key_event.key] = False


def is_key_pressed(key):
    """Returns if a key is pressed"""
    return keys.get(key, False)


def is_key_clicked(key):
    """Return if a key was clicked"""
    return key in pressed


def update():
    """Updates keyboard - clears the pressed set"""
    pressed.clear()


# mouse
mouse = [False for i in range(4)]
mouse_clicked = set()
x_pos, y_pos = 0, 0
x_scroll, y_scroll = 0, 0
x_move, y_move = 0, 0
x_ratio, y_ratio = 1, 1


def mouse_button_press(key_event):
    """Sets a mouse button to be pressed"""
    if key_event.button < 4:
        mouse[key_event.button] = True
        mouse_clicked.add(key_event.button)
        return
    mouse_scroll_update(key_event)


def mouse_button_release(key_event):
    """Sets a mouse button to be released"""
    if key_event.button < 4:
        mouse[key_event.button] = False


def mouse_button_clicked(key: int):
    """If mouse button was clicked"""
    return key in mouse_clicked


def mouse_scroll_update(scroll_event):
    """Mouse scroll update"""
    global y_scroll
    # even is up, odd is down
    direction = scroll_event.button % 2 == 0
    y_scroll = -scroll_event.button//2
    if direction:
        y_scroll = scroll_event.button//2


def mouse_move_update(move_event):
    """Move mouse"""
    global x_pos, y_pos, x_move, y_move
    x_move, y_move = move_event.rel[0], move_event.rel[1]
    x_pos, y_pos = move_event.pos[0], move_event.pos[1]


def is_mouse_button_press(key: int) -> bool:
    """Check if a mouse button was pressed"""
    return mouse[key]


def get_mouse_pos():
    """Get mouse position relative to the screen"""
    # convert to framebuffer area?
    
    return x_pos * x_ratio, y_pos * y_ratio


def update_ratio(width, height, o_width, o_height):
    """update the screen ratio to get accurate mouse coordinates"""
    global x_ratio, y_ratio
    x_ratio = o_width / width
    y_ratio = o_height / height


def update():
    """Updates keyboard - clears the pressed set"""
    global y_scroll, x_scroll
    pressed.clear()
    mouse_clicked.clear()
    y_scroll = 0
    x_scroll = 0