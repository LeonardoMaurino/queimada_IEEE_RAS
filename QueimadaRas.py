import pygame
import math
import random
import copy
from sys import exit
PLAYER_SIZE = 50;

BALL_SIZE = 20;

WIDTH, HEIGHT = 1200, 900

DECELERATION_FACTOR = 0.95

STEP = 25;
BACKGROUND_COLOR = (255, 217, 232)
INITIAL_BALL_COLOR = (192, 192, 192)
FINAL_BALL_COLOR = (255, 0, 0)
ARROW_COLOR = (255, 127, 0)
ARROW_LENGTH = 50;
THROW_SPEED = 25;
TICK_SPEED = 84;

MAX_MOVS = 5;
MAX_PASS = 2;


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
fundoMenu = pygame.image.load("img/FundoMenu.png")
Pause = pygame.image.load("img/Pause.png")

pygame.display.set_caption('Queimada RAS')
clock = pygame.time.Clock()

colors = {'white': (255, 255, 255), 'gray': (128, 128, 128), 'darkred': (139, 0, 0), 'black': (0, 0, 0),
          'yellow': (255, 255, 0), 'orange': (255, 165, 0), 'purple': (128, 0, 128), 'cyan': (0, 255, 255),
          'green': (0, 128, 0)}

class Dodgeball:

    pass_counter = 0;
    
    def __init__(self):

        powers = [ 0, 1, 2, 3, 4]
        random.shuffle(powers)

        self.A1 = Player([ 100, 200], Player.team_blue,  0, PLAYER_SIZE, powers[0]) # time azul
        self.A2 = Player([ 100, 600], Player.team_blue,  1, PLAYER_SIZE, powers[1])
        self.A3 = Player([ 500, 200], Player.team_blue, 2, PLAYER_SIZE, powers[2])
        self.A4 = Player([ 500, 600], Player.team_blue, 3, PLAYER_SIZE, powers[3])

        random.shuffle(powers)

        self.V1 = Player([ 100+600, 200], Player.team_red,  0, PLAYER_SIZE, powers[0])
        self.V2 = Player([ 100+600, 600], Player.team_red,  1, PLAYER_SIZE, powers[1])
        self.V3 = Player([ 500+600, 200], Player.team_red, 2, PLAYER_SIZE, powers[2])
        self.V4 = Player([ 500+600, 600], Player.team_red, 3, PLAYER_SIZE, powers[3])

        self.Ref = Player([1600, 1300], Player.team_red, 0, PLAYER_SIZE, Player.pawn)

        self.ball = Ball([0,0], BALL_SIZE)

        self.players = [[],[]];

        self.players[Player.team_blue] = [ self.A1, self.A2, self.A3, self.A4]
        self.players[Player.team_red] = [ self.V1, self.V2, self.V3, self.V4]

        for teams in self.players:
            for player in teams:
                player.draw();
    
        #sorteio de quem começa jogando

        rand = random.randint(0, 1)
        if(rand == Player.team_blue):
            rand = random.randint(0, 3)
            self.ball_player = self.players[Player.team_blue][rand];
        elif(rand == Player.team_red):
            rand = random.randint(0, 3)
            self.ball_player = self.players[Player.team_red][rand];
    
        self.arrow = Arrow(self.ball_player.truePosition)
    
    def reset_ball(self, team):
        if(team == Player.team_blue):
            rand = random.randint(0, 3)
            self.ball_player = self.players[Player.team_blue][rand];
        elif(team == Player.team_red):
            rand = random.randint(0, 3)
            self.ball_player = self.players[Player.team_red][rand];
        
        self.ball.pos = self.ball_player.truePosition
        self.arrow = Arrow(self.ball_player.truePosition)

    def get_distance(self, pos1, pos2):
        x_diff = abs(pos1[0] - pos2[0]);
        y_diff = abs(pos1[1] - pos2[1]);
        return math.hypot(x_diff, y_diff);

    def get_nearest(self, ball, team = None):

        retplayer = self.Ref;
        least = self.get_distance(retplayer.truePosition, self.ball.pos)

        if(team == Player.team_blue or team == None):
            for player in self.players[Player.team_blue]:
                if(player.alive == Player.alive):
                    new = self.get_distance(player.truePosition, ball.pos)
                    if(new < least):
                        least = new;
                        retplayer = player;

        if(team == Player.team_red or team == None):
            for player in self.players[Player.team_red]:
                if(player.alive == Player.alive):
                    new = self.get_distance(player.truePosition, ball.pos)
                    if(self.get_distance(player.truePosition, ball.pos) < least):
                        least = new;
                        retplayer = player; 

        return retplayer;

    def get_collision(self, nearest):
        if(self.get_distance(nearest.truePosition, self.ball.pos) < self.ball.size + nearest.size/2):
            return True;
        else:
            return False;

    def draw_players(self):
        for teams in self.players:
            for player in teams:
                player.draw();

    def check_game_end(self, team):
        for teams in self.players:
            for player in teams:
                if(player.alive == True and player.team == team):
                    return False
        return True
    
    def game_reset(self):
        self.__init__();

class Ball:

    def __init__(self, pos, size):
        self.pos = [pos[1], pos[0]];
        self.size = size;
        self.velocity = [0,0];
        self.throw_time = 0;
        self.hot = False;

    def draw_ball(self, color):
        pygame.draw.circle(screen, color, self.pos, self.size)

class Arrow:

    def __init__(self, pos):
        self.pos = [pos[1], pos[0]];
        self.ready = False;
        self.angle = 270;

    def draw_arrow(self, length):
        x_end = self.pos[0] + length * math.cos(math.radians(self.angle))
        y_end = self.pos[1] - length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, ARROW_COLOR, self.pos, (x_end, y_end), 5)

class Player:

    pawn = 0;
    tank = 1;
    speedster = 2;
    pitcher = 3;
    endless = 4;

    team_blue = 1;
    team_red = 0;
    alive = 1;
    dead = 0;
    move_counter = 0;

    step = STEP;
    power = pawn;
    scope_length = ARROW_LENGTH;
    max_movs = MAX_MOVS;
    throw_speed = THROW_SPEED;
    lives = 1;


    def __init__(self, pos, team, id, size, power):
        self.truePosition = pos
        self.team = team
        self.alive = Player.alive
        self.size = size
        self.id = id;
        self.empower(power)

    def draw(self):
        if self.alive == Player.alive:
            if self.team == Player.team_blue:
                pygame.draw.circle(screen, 'blue', self.truePosition, self.size/2)

            elif self.team == Player.team_red:
                pygame.draw.circle(screen, 'red', self.truePosition, self.size/2)

            instruction_text = pygame.font.Font(None, 36).render(str(self.pwr_str), True, (0,0,0))
            screen.blit(instruction_text, (self.truePosition[0]-25, self.truePosition[1]+45))

            match self.power:
                case Player.pawn:
                    pygame.draw.circle(screen, 'white', self.truePosition, self.size/3)

                case Player.tank:
                    pygame.draw.circle(screen, 'gray', self.truePosition, self.size/3)
                    if(self.lives > 1):
                        pygame.draw.circle(screen, 'brown', self.truePosition, self.size/5)

                case Player.endless:
                    pygame.draw.circle(screen, 'purple', self.truePosition, self.size/3)

                case Player.speedster:
                    pygame.draw.circle(screen, 'green', self.truePosition, self.size/3)

                case Player.pitcher:
                    pygame.draw.circle(screen, 'orange', self.truePosition, self.size/3)


    def empower(self, power):
        self.power = power;
        match power:
            case Player.pawn:
                self.pwr_str = "Pawn"

            case Player.tank:
                self.pwr_str = "Tank"
                self.lives = 2;
                self.max_movs = MAX_MOVS/2;
    
            case Player.speedster:
                self.pwr_str = "Speedster"
                self.max_movs = MAX_MOVS*2;
                self.step = STEP*2;
    
            case Player.pitcher:
                self.pwr_str = "Pitcher"
                self.throw_speed = 2*THROW_SPEED
                self.scope_length = 2*ARROW_LENGTH
    
            case Player.endless:
                self.pwr_str = "Endless"


    def move(self, n):

        if(self.move_counter < self.max_movs):

            match n:
                case 1:
                    self.truePosition[0] += self.step  # move to the right
                case 2:
                    self.truePosition[0] -= self.step  # move to the left
                case 3:
                    self.truePosition[1] += self.step  # move down
                case 4:
                    self.truePosition[1] -= self.step  # move up
                case _:
                    pass

            if self.truePosition[1] < 25:
                self.truePosition[1] = 25

            if self.truePosition[1] > 875:
                self.truePosition[1] = 875

            if self.team == Player.team_blue:
                if self.truePosition[0] < 25:
                    self.truePosition[0] = 25
                elif self.truePosition[0] > 575:
                    self.truePosition[0] = 575
            elif self.team == Player.team_red:
                if self.truePosition[0] < 25+600:
                    self.truePosition[0] = 25+600
                elif self.truePosition[0] > 575+600:
                    self.truePosition[0] = 575+600

        self.move_counter += 1;

class Button:
    def __init__(self, surface, image_path, rect):
        self.surface = surface
        self.image = pygame.image.load(image_path)
        self.rect = rect

    def draw(self):
        self.surface.blit(self.image, self.rect)

play_button = Button(screen, "img/BotaoJogar.png", pygame.Rect(450, 400, 300, 100))
exit_button = Button(screen, "img/BotaoSair.png", pygame.Rect(450, 600, 300, 100))
resume_button = Button(screen, "img/BotaoVoltar.png" , pygame.Rect(450, 400, 300, 100),)
restart_button = Button(screen, "img/BotaoRestart.png", pygame.Rect(450, 400, 300, 100),)

active = True
game_state = 'menu'
Game = Dodgeball()

while active and game_state == 'menu':
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'menu':
                if play_button.rect.collidepoint(event.pos):
                    game_state = 'ingame'
                elif exit_button.rect.collidepoint(event.pos):
                    active = False
                    pygame.quit()
    screen.blit(fundoMenu, (0, 0))
    play_button.draw()
    exit_button.draw()

    pygame.display.update()
    clock.tick(TICK_SPEED)

while active and (game_state == 'ingame' or game_state == 'pausado'):

            

    if game_state == 'ingame':    
            screen.fill(BACKGROUND_COLOR)
            line = pygame.draw.line(screen, 'black', (600, 0), (600, 900), 15)
            Game.draw_players();    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and not Game.ball.hot:
                    if event.key == pygame.K_ESCAPE:
                        game_state = 'pausado'
                    if event.key == pygame.K_LEFT:
                        Game.ball_player.move(2);
                    elif event.key == pygame.K_RIGHT:
                        Game.ball_player.move(1);
                    elif event.key == pygame.K_DOWN:
                        Game.ball_player.move(3);
                    elif event.key == pygame.K_UP:
                        Game.ball_player.move(4);
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        Game.ball.hot = True;
                        Game.ball_player.move_counter = 0;
                        Game.ball.velocity = [Game.ball_player.throw_speed * math.cos(math.radians(Game.arrow.angle)),
                                            -Game.ball_player.throw_speed * math.sin(math.radians(Game.arrow.angle))]
                        Game.ball.pos = copy.deepcopy(Game.ball_player.truePosition);

            nearest = Game.get_nearest(Game.ball);

            if Game.get_collision(nearest):
                if nearest != Game.ball_player:
                    Game.arrow.angle = 270;
                
                if nearest.team == Game.ball_player.team and nearest != Game.ball_player:
                    if Game.pass_counter < MAX_PASS:
                        Game.ball_player = nearest;
                        Game.ball.hot = False;
                        Game.pass_counter += 1;
                    elif Game.pass_counter == MAX_PASS:
                        Game.pass_counter = 0;
                        Game.ball.hot = False;
                        if nearest.team == Player.team_blue:
                            while(True):
                                Game.reset_ball(Player.team_red)
                                if(Game.ball_player.alive == True):
                                    break;

                        if nearest.team == Player.team_red:
                            while(True):
                                Game.reset_ball(Player.team_blue)
                                if(Game.ball_player.alive == True):
                                    break;
                
                elif nearest.team != Game.ball_player.team and nearest != Game.ball_player:
                    Game.pass_counter = 0;
                    Game.ball.hot = False;
                    rand = random.random();

                    if(rand < progress or nearest.power == Player.endless):
                        if(nearest.lives > 0):
                            nearest.lives -= 1;
                        if(nearest.lives == 0):
                            nearest.alive = False;
                            while True:
                                Game.reset_ball(nearest.team)
                                if Game.ball_player.alive == True:
                                    break;
                                if Game.check_game_end(nearest.team):
                                    Game.__init__();
                                    break;
                        else:
                            Game.ball_player = nearest;
                            Game.ball.hot = False;
            
                    else:

                        Game.ball_player = nearest;
                        Game.ball.hot = False;

                        

            if not Game.ball.hot:
                Game.arrow.pos = Game.ball_player.truePosition
                if(Game.ball_player.team == Player.team_blue):
                    Game.arrow.angle += 1;
                    if Game.arrow.angle > 360:
                        Game.arrow.angle = 0
                
                if(Game.ball_player.team == Player.team_red):
                    Game.arrow.angle -= 1;
                    if Game.arrow.angle == 0:
                        Game.arrow.angle = 360

            if Game.ball.hot:
                Game.ball.pos[0] += Game.ball.velocity[0]*2
                Game.ball.pos[1] += Game.ball.velocity[1]*2
                if(Game.ball_player.power != Player.endless):
                    Game.ball.velocity[0] *= DECELERATION_FACTOR
                    Game.ball.velocity[1] *= DECELERATION_FACTOR

                if abs(Game.ball.velocity[0]) < 0.1 and abs(Game.ball.velocity[1]) < 0.1:
                    Game.ball.hot = False
                    if(Game.ball.pos[0] < 600):
                        Game.ball_player = Game.get_nearest(Game.ball, Player.team_blue);
                        Game.arrow.angle = 270;
                
                    if(Game.ball.pos[0] > 600):
                        Game.ball_player = Game.get_nearest(Game.ball, Player.team_red);
                        Game.arrow.angle = 270;

                if Game.ball.pos[0] <= 20:
                    Game.ball.pos[0] = 20
                    Game.ball.velocity[0] = -Game.ball.velocity[0]
                if Game.ball.pos[0] >= WIDTH - 20:
                    Game.ball.pos[0] = WIDTH - 20
                    Game.ball.velocity[0] = -Game.ball.velocity[0]

                if Game.ball.pos[1] <= 20:
                    Game.ball.pos[1] = 20
                    Game.ball.velocity[1] = -Game.ball.velocity[1]
                if Game.ball.pos[1] >= HEIGHT - 20:
                    Game.ball.pos[1] = HEIGHT - 20
                    Game.ball.velocity[1] = -Game.ball.velocity[1]

                progress = min(math.hypot(Game.ball.velocity[0], Game.ball.velocity[1]) / Game.ball_player.throw_speed, 1)
                current_ball_color = ( 
                    int(INITIAL_BALL_COLOR[0] + (FINAL_BALL_COLOR[0] - INITIAL_BALL_COLOR[0]) * progress),
                    int(INITIAL_BALL_COLOR[1] + (FINAL_BALL_COLOR[1] - INITIAL_BALL_COLOR[1]) * progress),
                    int(INITIAL_BALL_COLOR[2] + (FINAL_BALL_COLOR[2] - INITIAL_BALL_COLOR[2]) * progress)
                )

                Game.ball.draw_ball(current_ball_color)
            if not Game.ball.hot:
                Game.arrow.draw_arrow(Game.ball_player.scope_length);
                instruction_text = pygame.font.Font(None, 36).render("Press Enter to throw the ball", True, (255, 255, 255))
                screen.blit(instruction_text, (WIDTH // 2 - 200, HEIGHT - 50))


    elif game_state == 'pausado':
            resume_button.draw()
            exit_button.draw()
            screen.blit(Pause, (100, 100))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if resume_button.rect.collidepoint(event.pos):
                        game_state = 'ingame'
                    if exit_button.rect.collidepoint(event.pos):
                        active = False
                        pygame.quit()
    pygame.display.update()
    clock.tick(TICK_SPEED)
