"""
The classic game of flappy bird. Made with python
and pygame. Features pixel perfect collision using masks :o

Date Modified:  Jul 30, 2019
Author: Tech With Tim
"""
import pygame
import random
import os
import time
import neat # stap 19 neat en pickle werden eerder nog niet geimporteerd, nu wel
import pickle
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0
class Bird:
    """
    Bird class representing the flappy bird
    """
    WIN_HEIGHT = 0
    WIN_WIDTH = 0
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.gravity = 9.8
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # terminal velocity
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # so when bird is nose diving it isn't flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    represents a pipe object
    """
    WIN_HEIGHT = WIN_HEIGHT
    WIN_WIDTH = WIN_WIDTH
    GAP = 160
    VEL = 5

    def __init__(self, x):
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0
        self.gap = 100  # gap between top and bottom pipe

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIN_WIDTH = WIN_WIDTH
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def menu_screen(win):
    """
    the menu screen that will start the game
    :param win: the pygame window surface
    :return: None
    """
    pass

def end_screen(win):
    """
    display an end screen when the player loses
    :param win: the pygame window surface
    :return: None
    """
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main(win)

        win.blit(text_label, (WIN_WIDTH/2 - text_label.get_width()/2, 500))
        pygame.display.update()

    pygame.quit()
    quit()

def draw_window(win, birds, pipes, base, score):
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :return: None
    """
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds: # stap 18
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    pygame.display.update()

#stap 4, main(win) --> main(genomes, config), zo heb je twee parameters 
def main(genomes, config):
    """
    Runs the main game loop
    :param win: pygame window surface
    :return: None
    """
#stap 6. tracken van de positie op het scherm van de vogels, zodat je hun fitness kan veranderen
    nets = []
    # (stap 4) Bird= Bird(230,350) --> birds = [], zodat er meerdere vogels tegelijker tijd kunnen starten
    birds = []
    ge = []
    
    #stap 7,  een neural network beginnen voor genomes, een bird object voor het beginnen
    #en de genome tracken in een lijst
    # er zijn drie lijsten, zodat elke positie in de lijst correspondeert met de zelfde vogel
    for genome_id, genome in genomes:
        genome.fitness = 0 #zodat je met fitness = 0 begint
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)
    
    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()
    start = False
    lost = False

    run = True
    while run and len(birds) > 0:
        pygame.time.delay(30)
        clock.tick(100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()#stap 16, dit stond op de verkeerde plek in het bestand
                quit()
                break
        #stap 11 
        pipe_ind = 0 # als er geen verdere voorwaarden zijn wordt de eerste pijp gebruikt die in beeld is
        if len(birds) > 0: #als het aantal vogels groter dan 0 is
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  #en als ze voorbij de eerste pijp zijn, en ze voorbij de breedte van de pijp zijn
                pipe_ind = 1   #dan wordt de tweede pijp gebruikt
        else: #stap 17, als er geen vogels meer over zijn, stopt het spel
            run = False
            break
# Hier is een stukje code weggehaald, deze was niet nodig
#stap 12
        for x, bird in enumerate(birds):  #hier wordt gekeken naar de lijst met vogels, x is de index en bird is het object
            ge[x].fitness += 0.1 #vogel +0.1 fitness geven per frame dat ze levend zijn
            bird.move()#zodat de vogels kunnen bewegen
            
            #stap 13 Dit haalt het neurale netwerk op dat hoort bij de specifieke vogel, Dit zorgt ervoor dat het neurale netwerk beslissingen kan nemen op basis van de positie van de vogel ten opzichte van de pipes
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
             
            if output[0] > 0.5:  #stap 14, hier wordt de tanh functie gebruikt, als de output groter is dan 0.5
                bird.jump() #dan springen
                
        base.move()


        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            #stap 5 "for bird in birds:" wordt twee keer toegevoegd
            for bird in birds:
            # check for collision, kijken of elke pipe botst met elke vogel
                if pipe.collide(bird, win):
                            #stap 8
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird)) #zo worden de vogels verwijdert die tegen de pipe aanvliegen
                        
                if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)
                        

                    
                if not pipe.passed and pipe.x < bird.x:
                    #checken of de vogels voorbij de pijp zijn
                    pipe.passed = True
                    add_pipe = True

        if add_pipe:
            score += 1 
            for genome in ge:
                genome.fitness += 5 # (stap 9) verander de fitness met +5 als de vogels erdoorheen komen en niet doodgaan, zodat de vogels liever door de pipe heengaan ipv ertegenaan vliegen 
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)
        #of de vogels de grond raken
        for bird in birds:
            #stap 10 zodat vogels verdwijnen die doodgaan
            #stap 15 de vogels gaan nu niet buiten het scherm
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

            draw_window(WIN, birds, pipes, base, score)           
        if score > 25:        
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break
    


#stap 2
def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)#al deze neat dingen staan in de configuration file

    #stap 3 
    p = neat.Population(config) 
#     Hier wordt een populatie gemaakt
#De StdOut 
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #hier worden de besten uit de populatie gehaald
    
        #p.add_reporter(neat.Checkpointer(5))

    # Hier runt het programma voor 50 generaties/ 50 keer
    winner = p.run(main, 50)
    
        # show final stats
    print('\nBest genome:\n{!s}'.format(winner))
    

#stap 1, dit creëert het pad naar de configuration file, zodat het progamma dit teksbestand kan gebruiken.
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
