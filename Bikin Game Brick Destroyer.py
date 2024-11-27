import tkinter as tk

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                return game_object.hit()
        return 0

class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        self.speed = 15
        self.dx = 0  
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#D4F6FF')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        
        new_x = coords[0] + self.dx
        new_right = new_x + self.width
        
        if new_x >= 0 and new_right <= width:
            super(Paddle, self).move(self.dx, 0)
            if self.ball is not None:
                self.ball.move(self.dx, 0)

    def start_move(self, direction):
        self.dx = direction * self.speed

    def stop_move(self):
        self.dx = 0

class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2', 4: '#FFB643', 5: '#FF6B6B'}
    POINTS = {1: 10, 2: 20, 3: 30, 4: 40, 5: 50}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
            return Brick.POINTS[1]
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])
            return 5

class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 0
        self.score = 0
        self.minimum_win_score = 150
        self.width = 900
        self.height = 650
        self.canvas = tk.Canvas(self, bg='#7BD3EA',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 30, 5)
            self.add_brick(x + 37.5, 50, 4)
            self.add_brick(x + 37.5, 70, 3)
            self.add_brick(x + 37.5, 90, 2)
            self.add_brick(x + 37.5, 110, 1)

        self.hud = None
        self.score_text = None
        self.setup_game()
        self.canvas.focus_set()
        
        self.canvas.bind('<Left>', lambda _: self.paddle.start_move(-1))
        self.canvas.bind('<Right>', lambda _: self.paddle.start_move(1))
        self.canvas.bind('<KeyRelease-Left>', lambda _: self.paddle.stop_move())
        self.canvas.bind('<KeyRelease-Right>', lambda _: self.paddle.stop_move())

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(450, 250,
                                   'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 10, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        text = 'Score: %s' % self.score
        if self.score_text is None:
            self.score_text = self.draw_text(150, 10, text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.paddle.update()
        
        points = self.check_collisions()
        self.score += points
        self.update_score_text()
        
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            if self.score >= self.minimum_win_score:
                self.ball.speed = None
                self.draw_text(450, 250, f'Kamu Memenangkan Gamenya Dengan {self.score} Points!')
            else:
                self.draw_text(450, 250, f'Tidak Cukup Point! Butuh {self.minimum_win_score} Untuk Memenangkan Gamenya.')
                self.ball.speed = None
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(450, 250, f'Permainan Berakhir! Skor Akhir: {self.score}')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        return self.ball.collide(objects)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Pecahkan Kotaknya!')
    game = Game(root)
    game.mainloop()