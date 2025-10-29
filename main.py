import sys, os, random, json
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QMessageBox,
    QGraphicsRectItem,
)
from PySide6.QtUiTools import QUiLoader
from PySide6 import QtCore, QtWidgets
from pathlib import Path


LEVELS_FILE = Path("levels.json")


# Function to get the resource path for loading UI files
def get_resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, path)


# Load levels from levels.json
def load_levels():
    if LEVELS_FILE.exists():
        with open(LEVELS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("levels", [])
    else:
        print("No levels.json found — using default level")
        return [
            {
                "id": "default",
                "name": "Default",
                "scene_rect": [-400, -200, 800, 400],
                "snake_start": [0, 0],
                "snake_direction": "right",
                "timer_interval": 150,
                "obstacles": []
            }
        ]


# def apply_level(self, level):
#     # Scene rect
#     sx, sy, sw, sh = level.get("scene_rect", [-400, -200, 800, 400])
#     self.scene.setSceneRect(sx, sy, sw, sh)

#     # Clear existing obstacles
#     for item in list(self.obstacles):
#         try:
#             self.scene.removeItem(item)
#         except Exception:
#             pass
#     self.obstacles.clear()

#     # Add obstacles from level
#     for obs in level.get("obstacles", []):
#         rect_item = QGraphicsRectItem(obs["x"], obs["y"], obs["w"], obs["h"])
#         rect_item.setBrush(QBrush(QColor(100, 100, 100)))
#         rect_item.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
#         self.scene.addItem(rect_item)
#         self.obstacles.append(rect_item)

#     # Ensure the snake spawns safely within scene bounds
#     sx0, sy0 = level.get("snake_start", [0, 0])
#     direction_name = level.get("snake_direction", "right")
#     directions = {
#         "right": (1, 0),
#         "left": (-1, 0),
#         "up": (0, -1),
#         "down": (0, 1)
#     }
#     self.snake.direction = directions.get(direction_name, (1, 0))

#     # Clamp spawn point so it's always inside the visible scene
#     rect = self.scene.sceneRect()
#     cube_size = 15
#     if sx0 < rect.left() + cube_size:
#         sx0 = rect.left() + cube_size
#     elif sx0 > rect.right() - cube_size:
#         sx0 = rect.right() - cube_size
#     if sy0 < rect.top() + cube_size:
#         sy0 = rect.top() + cube_size
#     elif sy0 > rect.bottom() - cube_size:
#         sy0 = rect.bottom() - cube_size

#     # Ensure safe spawn (avoid spawning on obstacles)
#     def is_safe(x, y):
#         test_rect = QtCore.QRectF(x, y, cube_size, cube_size)
#         for obs in self.obstacles:
#             if test_rect.intersects(obs.rect().translated(obs.x(), obs.y())):
#                 return False
#         return True

#     if not is_safe(sx0, sy0):
#         # Snake spawn blocked by obstacle — finding new position
#         rect = self.scene.sceneRect()
#         found = False
#         step = cube_size * 2
#         # scan for an open area within the scene
#         for y in range(int(rect.top()), int(rect.bottom()), step):
#             for x in range(int(rect.left()), int(rect.right()), step):
#                 if is_safe(x, y):
#                     sx0, sy0 = x, y
#                     found = True
#                     break
#             if found:
#                 break

#     head = self.snake.cube_list[0]
#     head.setPos(sx0, sy0)

#     for i, cube in enumerate(self.snake.cube_list[1:], start=1):
#         cube.setPos(sx0 - i * cube_size * self.snake.direction[0],
#                     sy0 - i * cube_size * self.snake.direction[1])

#     # Add to scene
#     for cube in self.snake.cube_list:
#         if cube.scene() != self.scene:
#             self.scene.addItem(cube)


# Class representing Food item for the snake to consume
class Food(QGraphicsRectItem):
    def __init__(self):
        self.width = 15
        self.height = 15
        super().__init__(0, 0, self.width, self.height)  # x, y are set later
        self.setBrush(QBrush(QColor("orange")))


# Class representing individual SnakeCube (each segment of the snake)
class SnakeCube(QGraphicsRectItem):
    def __init__(self):
        self.width = 15
        self.height = 15
        super().__init__(0, 0, self.width, self.height)  # x, y are set later
        self.setBrush(QBrush(QColor("green")))


# Class representing Obstacle
class Obstacle(QGraphicsRectItem):
    def __init__(self, x, y, width=30, height=30):
        super().__init__(x, y, width, height)
        self.setBrush(QBrush(QColor("red")))  # Set obstacle color to red for visibility
        self.setPen(QtCore.Qt.NoPen)  # Remove border for cleaner look


# Class representing the Snake and its behavior
class Snake(QtWidgets.QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.direction = (1, 0)  # Start moving right
        self.cube_list = [SnakeCube() for i in range(2)]  # Snake is initially 2 cubes large
        self.move()

    def move(self):
        head = self.cube_list[0]
        tail = self.cube_list[-1]
        tail.setX(head.x() + self.direction[0] * head.width)  # Set tail position based on direction snake is heading
        tail.setY(head.y() + self.direction[1] * head.height)
        self.cube_list.insert(0, self.cube_list.pop())  # Insert tail at the beginning and remove from end

    def grow(self):
        new_cube = SnakeCube()
        self.cube_list.append(new_cube)
        self.move()

    def change_direction(self, direction):
        dx, dy = direction
        if (dx, dy) != (-self.direction[0], -self.direction[1]):  # Prevent snake from going in the opposite direction
            self.direction = (dx, dy)


# Main Window class for the Snake Game
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        ui_file_path = "main.ui"
        ui_file_abs_path = get_resource_path(ui_file_path)
        ui_file = QtCore.QFile(ui_file_abs_path)
        if not ui_file.open(QtCore.QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_abs_path}: {ui_file.errorString()}")
            sys.exit(-1)

        loader = QUiLoader()
        self.window = loader.load(ui_file)
        ui_file.close()
        if not self.window:
            print(loader.errorString())
            sys.exit(-1)

        self.graphicsView = self.window.findChild(QGraphicsView, "graphicsView")
        self.scene = QGraphicsScene(self.graphicsView)
        self.scene.setBackgroundBrush(QBrush(QColor("black")))
        self.graphicsView.setScene(self.scene)

        self.graphicsView.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.graphicsView.setAlignment(QtCore.Qt.AlignCenter)
        self.scene.setSceneRect(-400, -200, 800, 400)

        self.scoreLabel = QtWidgets.QLabel("Score: 0", self.window)
        self.escLabel = QtWidgets.QLabel("\"esc\" to pause", self.window)
        self.scoreLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.scoreLabel.setStyleSheet("color: white; font-size: 20px;")
        self.scoreLabel.setGeometry(350, 10, 100, 30)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(150)  # Set a slower timer for better game speed

        self.scene.keyPressEvent = self.scene_key_press

        # Initialize game elements
        self.obstacles = []  # List to hold obstacles
        self.food_count = 0  # Counter for food consumed
        self.create_food()
        self.snake = Snake()

        self.in_menu = True
        self.menu_selection = 0
        self.start_button = None
        self.quit_button = None
        self.show_start_menu()

        self.levels = load_levels()
        self.current_level = self.levels[0]  # default level

        self.window.show()

    def apply_level(self, level):
        # ensure a consistent cube size value
        self.cube_size = getattr(self, "cube_size", 15)

        self._set_scene_rect(level)
        self._load_obstacles(level)
        self._set_snake_start(level)
        self._ensure_snake_safe_spawn()
        self._position_and_add_snake()

    def _set_scene_rect(self, level):
        sx, sy, sw, sh = level.get("scene_rect", [-400, -200, 800, 400])
        self.scene.setSceneRect(sx, sy, sw, sh)

    def _load_obstacles(self, level):
        # Remove existing obstacle items from the scene (safe)
        for item in list(self.obstacles):
            try:
                if item.scene() == self.scene:
                    self.scene.removeItem(item)
            except Exception:
                pass
        self.obstacles.clear()

        # Create and add new obstacles with visible color
        for obs in level.get("obstacles", []):
            rect_item = QGraphicsRectItem(obs["x"], obs["y"], obs["w"], obs["h"])
            # Set a visible brush (non-colorless)
            rect_item.setBrush(QBrush(QColor(100, 100, 100)))  # gray
            rect_item.setPen(QtCore.Qt.NoPen)
            # Prevent selection and interaction
            try:
                rect_item.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
            except Exception:
                # If the Qt binding presents flag differently, ignore
                pass
            self.scene.addItem(rect_item)
            self.obstacles.append(rect_item)

    def _set_snake_start(self, level):
        sx0, sy0 = level.get("snake_start", [0, 0])
        direction_name = level.get("snake_direction", "right")
        directions = {
            "right": (1, 0),
            "left": (-1, 0),
            "up": (0, -1),
            "down": (0, 1)
        }
        self.snake.direction = directions.get(direction_name, (1, 0))
        # store start position for the next step
        self._snake_target_start = [sx0, sy0]

    def _ensure_snake_safe_spawn(self):
        rect = self.scene.sceneRect()
        cube = self.cube_size
        sx0, sy0 = self._snake_target_start

        # clamp coordinates inside the visible scene (accounting for one cube)
        sx0 = max(rect.left() + cube, min(rect.right() - cube, sx0))
        sy0 = max(rect.top() + cube, min(rect.bottom() - cube, sy0))

        # inner helper: is a cube-sized rect at (x,y) free of obstacles?
        def is_safe(x, y):
            test_rect = QtCore.QRectF(x, y, cube, cube)
            for obs in self.obstacles:
                # obs.rect() is local rect (0,0,w,h) — translate to scene pos
                obs_scene_rect = obs.rect().translated(obs.x(), obs.y())
                if test_rect.intersects(obs_scene_rect):
                    return False
            return True

        if not is_safe(sx0, sy0):
            found = False
            step = cube * 2
            # scan the scene in a grid for an open spot
            top = int(rect.top())
            bottom = int(rect.bottom())
            left = int(rect.left())
            right = int(rect.right())

            for y in range(top, bottom + 1, step):
                for x in range(left, right + 1, step):
                    if is_safe(x, y):
                        sx0, sy0 = x, y
                        found = True
                        break
                if found:
                    break

        self._snake_target_start = [sx0, sy0]

    def _position_and_add_snake(self):
        sx0, sy0 = self._snake_target_start
        cube = self.cube_size

        # place head
        head = self.snake.cube_list[0]
        head.setPos(sx0, sy0)

        # place following cubes trailing in the opposite direction of motion
        for i, cube_item in enumerate(self.snake.cube_list[1:], start=1):
            dx, dy = self.snake.direction
            cube_item.setPos(sx0 - i * cube * dx, sy0 - i * cube * dy)

        # add any not-in-scene cubes to the scene
        for cube_item in self.snake.cube_list:
            if cube_item.scene() != self.scene:
                self.scene.addItem(cube_item)

    def update_score(self):
        self.scoreLabel.setText(f"Score: {self.snake.score}")

    def scene_key_press(self, event):
        if self.in_menu:
            # Handle menu navigation and game start
            if event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_W:
                self.menu_selection = 0
                self.update_menu_selection()
            elif event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_S:
                self.menu_selection = 1
                self.update_menu_selection()
            elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                if self.menu_selection == 0:
                    self.start_game()
                elif self.menu_selection == 1:
                    QApplication.quit()
        else:
            # Handle snake movement with arrow keys or WASD
            if event.key() == QtCore.Qt.Key_Left or event.key() == QtCore.Qt.Key_A:
                self.snake.change_direction((-1, 0))
            elif event.key() == QtCore.Qt.Key_Right or event.key() == QtCore.Qt.Key_D:
                self.snake.change_direction((1, 0))
            elif event.key() == QtCore.Qt.Key_Up or event.key() == QtCore.Qt.Key_W:
                self.snake.change_direction((0, -1))
            elif event.key() == QtCore.Qt.Key_Down or event.key() == QtCore.Qt.Key_S:
                self.snake.change_direction((0, 1))
            elif event.key() == QtCore.Qt.Key_Escape:
                self.game_pause()
            self.tick()  # Move snake with every key press

    def tick(self):
        if not self.in_menu:
            # Update the scene without removing all elements
            self.render_elements()
            self.snake.move()
            self.check_collision()

    def render_elements(self):
        # Re-add food item if it exists
        if self.food and self.food.scene() != self.scene:
            self.scene.addItem(self.food)

        # Re-add all snake cubes to the scene
        for sc in self.snake.cube_list:
            if sc.scene() != self.scene:
                self.scene.addItem(sc)

        # Re-add all obstacles to the scene
        for obstacle in self.obstacles:
            if obstacle.scene() != self.scene:
                self.scene.addItem(obstacle)

    def create_food(self):
        # Create a new food object and place it in the scene
        x = self.scene.width() * (0.1 + 0.8 * (random.random()) - 0.5)
        y = self.scene.height() * (0.1 + 0.8 * (random.random()) - 0.5)
        self.food = Food()
        self.food.setX(x)
        self.food.setY(y)
        self.scene.addItem(self.food)  # Add the food item to the scene

    def create_obstacle(self):
        # Create a new obstacle and place it randomly in the scene
        x = self.scene.width() * (0.1 + 0.8 * (random.random()) - 0.5)
        y = self.scene.height() * (0.1 + 0.8 * (random.random()) - 0.5)
        obstacle = Obstacle(x, y)
        self.obstacles.append(obstacle)
        self.scene.addItem(obstacle)  # Add the obstacle to the scene

    def check_collision(self):
        head = self.snake.cube_list[0]

        # Check collision with boundaries using scene's bounding rectangle
        if not self.scene.sceneRect().contains(head.sceneBoundingRect()):
            self.game_over()
            return

        # Check self-collision by comparing positions
        head_pos = (head.x(), head.y())
        for cube in self.snake.cube_list[1:]:
            if head_pos == (cube.x(), cube.y()):
                self.game_over()
                return

        # Check collision with the food
        if head.collidesWithItem(self.food):
            self.snake.score += 1  # Score is updated by 1 for every food consumed
            self.food_count += 1  # Increment food count
            self.update_score()
            self.scene.removeItem(self.food)
            self.create_food()
            self.snake.grow()

            # Add obstacle every 5 food items consumed
            if self.food_count % 5 == 0:
                self.create_obstacle()

        # Check collision with obstacles
        for obstacle in self.obstacles:
            if head.collidesWithItem(obstacle):
                self.game_over()
                return

    def game_pause(self):
        self.timer.stop()
        msg1 = QMessageBox()
        msg1.setWindowTitle("Game Paused")
        msg1.setText(f"Your score: {self.snake.score}\n Do you want to continue?")
        msg1.setIcon(QMessageBox.Information)
        continue_button = msg1.addButton("Continue", QMessageBox.ActionRole)
        abort_button = msg1.addButton("Quit", QMessageBox.RejectRole)
        msg1.exec()
        if msg1.clickedButton() == continue_button:  # Reinitialize timer to resume game
            self.timer.start(150)
        elif msg1.clickedButton() == abort_button:
            self.game_over()

    def game_over(self):
        self.timer.stop()
        msg = QMessageBox()
        msg.setWindowTitle("Game Over")
        msg.setText(f"Your score: {self.snake.score}")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

        # Reset the game state
        self.snake = Snake()
        self.obstacles.clear()  # Clear obstacles
        self.scene.clear()  # Clear the entire scene to remove all items
        self.food = None  # Reset food

        self.in_menu = True
        self.menu_selection = 0
        self.start_button = None
        self.quit_button = None

        self.show_start_menu()
        self.update_score()

    def show_start_menu(self):
        self.in_menu = True
        self.scene.clear()

        self.start_button = QtWidgets.QLabel("START", self.window)
        self.start_button.setAlignment(QtCore.Qt.AlignCenter)
        self.start_button.setStyleSheet("color: white; font-size: 30px;")
        self.start_button.setGeometry(350, 150, 100, 50)
        self.start_button.show()
        self.start_button.mousePressEvent = self.start_button_clicked

        self.quit_button = QtWidgets.QLabel("QUIT", self.window)
        self.quit_button.setAlignment(QtCore.Qt.AlignCenter)
        self.quit_button.setStyleSheet("color: white; font-size: 30px;")
        self.quit_button.setGeometry(350, 250, 100, 50)
        self.quit_button.show()
        self.quit_button.mousePressEvent = self.quit_button_clicked

        self.dummy_text = QtWidgets.QLabel("Use Keyboard Keys or Mouse To Navigate!", self.window)
        self.dummy_text.setAlignment(QtCore.Qt.AlignCenter)
        self.dummy_text.setStyleSheet("color: green; font-size: 14px;")
        self.dummy_text.setGeometry(250, 350, 300, 50)
        self.dummy_text.show()

        self.update_menu_selection()
        self.window.update()

    def update_menu_selection(self):
        if self.menu_selection == 0:
            self.start_button.setStyleSheet("color: yellow; font-size: 30px;")
            self.quit_button.setStyleSheet("color: white; font-size: 30px;")
        else:
            self.start_button.setStyleSheet("color: white; font-size: 30px;")
            self.quit_button.setStyleSheet("color: yellow; font-size: 30px;")

    def start_button_clicked(self, event):
        self.start_game()

    def quit_button_clicked(self, event):
        QApplication.quit()

    def start_game(self):
        '''-----------OLD CODE START-----------'''
        # self.start_button.deleteLater()
        # self.quit_button.deleteLater()
        # self.in_menu = False
        # self.snake = Snake()
        # self.create_food()
        # self.obstacles.clear()  # Clear any existing obstacles
        # self.food_count = 0  # Reset food count
        # self.timer.start(150)  # Reset game timer
        # self.update_score()
        '''-----------OLD CODE FINISH-----------'''

        # Stop game timer to avoid background movement
        self.timer.stop()

        self.start_button.deleteLater()
        self.quit_button.deleteLater()

        # Stay in menu mode until the user chooses a level
        self.in_menu = True

        # Ask user to choose a level
        level_names = [lvl["name"] for lvl in self.levels]
        selected, ok = QtWidgets.QInputDialog.getItem(
            self.window, "Choose Level", "Select a level:", level_names, 0, False
        )

        if not ok:
            # User canceled => back to menu
            self.show_start_menu()
            return

        # Now that level is chosen, exit menu mode
        self.in_menu = False

        # Find selected level and apply it
        for lvl in self.levels:
            if lvl["name"] == selected:
                self.current_level = lvl
                break

        self.snake = Snake()
        self.create_food()
        self.obstacles.clear()
        self.food_count = 0

        # Start timer *after* setup
        self.timer.start(self.current_level.get("timer_interval", 150))
        self.update_score()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
