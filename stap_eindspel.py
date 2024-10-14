import pygame
import random
import os
import time
import neat
import pickle
pygame.font.init()  

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

    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.tilt = 0  
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
      
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):

        self.tick_count += 1

        
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2 

        
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):

 
        self.img_count += 1
        
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

       
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


   
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
      
        return pygame.mask.from_surface(self.img)


class Pipe():
   
    GAP = 160 #stap 28 de gap tussen twee pipes en de snelheid van de pipes
    VEL = 5

    def __init__(self, x):
      
        self.x = x
        self.height = 0

        
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
       
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        
        self.x -= self.VEL

    def draw(self, win):
       
        
        win.blit(self.PIPE_TOP, (self.x, self.top))
        
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        
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
    
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
  
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):

    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
       
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
     
        bird.draw(win)

  
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

 
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()
#stap 6, eval_genomes(win) --> evalgenomes(genomes, config), zo heb je twee parameters 
def eval_genomes(genomes, config):

    global WIN, gen
    win = WIN
    gen += 1

    #stap 10 tracken van de positie op het scherm van de vogels, zodat je hun fitness kan veranderen
    nets = []
    birds = [] # stap 7 Bird= Bird(230,350) --> birds = [], zodat er meerdere vogels tegelijker tijd kunnen starten
    ge = []
    
    #stap 11,  een neural network beginnen voor genomes, een bird object voor het beginnen
    #en de genome tracken in een lijst
    # er zijn drie lijsten, zodat elke positie in de lijst correspondeert met de zelfde vogel
    for genome_id, genome in genomes:
        genome.fitness = 0  #stap 12 zodat je met fitness = 0 begint
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True
    while run and len(birds) > 0:
        clock.tick(100)#stap 27, de speelsnelheid/frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0 #stap 17 als er geen verdere voorwaarden zijn wordt de eerste pijp gebruikt die in beeld is
        if len(birds) > 0: #stap 18 "als het aantal vogels groter dan 0 is"
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): #Stap 19 en als ze voorbij de eerste pijp zijn, en ze voorbij de breedte van de pijp zijn
                pipe_ind = 1  #stap 20 dan wordt de tweede pijp gebruikt                                                              

        for x, bird in enumerate(birds):  #stap 21 hier wordt gekeken naar de lijst met vogels, x is de index en bird is het object
            ge[x].fitness += 0.1 #stap 22 vogel +0.1 fitness geven per frame dat ze levend zijn
            bird.move()

            #stap 23 Dit haalt het neurale netwerk op dat hoort bij de specifieke vogel,
            #Dit zorgt ervoor dat het neurale netwerk beslissingen kan nemen op basis van de positie van de vogel ten opzichte van de pipes
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  #stap 24, hier wordt de tanh functie gebruikt, als de output groter is dan 0.5
                bird.jump() #dan springen

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            #stap 8 "for bird in birds:" wordt toegevoegd
            for bird in birds:
                if pipe.collide(bird, win):
                    #stap 13 zo worden de vogels verwijdert die tegen de pipe aanvliegen
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                #stap 14 checken of de vogels voorbij de pijp zijn
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5 # stap 15 verander de fitness met +5 als de vogels erdoorheen komen en niet doodgaan, zodat de vogels liever door de pipe heengaan ipv ertegenaan vliegen 
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)
        #stap 9, for bird in birds wordt nogmaals toegevoegd
        for bird in birds:
            #stap 16 zodat vogels verdwijnen/uit de populatie
            #worden gehaald als die doodgaan
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50: #stap 25 de vogels gaan nu niet buiten het scherm 
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # stap 26, als de score boven de 25 komt, stopt het spel, want het doel is bewaard
        #de vogel die dit heeft gehaald wordt opgeslagen
        if score > 25:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break
        
def best_player(genomes, config_s):#stap 30 hier wordt de functie best_player defined
    genome_path = os.path.join(local_dir, "best.pickle")
    with open(genome_path, "rb") as f: #het beste vogeltje wordt weer aangeroepen
        genome = pickle.load(f)
    genomes = [(1,genome)] #en als enige in de lijst genomes gezet, waardoor er alleen met dit vogeltje wordt gespeeld
    eval_genomes(genomes, config_s)


def run(config_file): # stap 2 al deze neat dingen staan in de configuration file
  
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # stap 3 hier wordt een populatie gemaakt hieruit kunnen later dan de beste vogels worden geselecteerd
    p = neat.Population(config)

    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
       #stap 4hier worden de besten uit de populatie gehaald

    #stap 5 Hier runt het programma voor x generaties/ x keer
    winner = p.run(eval_genomes, 10) #stap eindspel, 10 generaties is altijd genoeg, maar niet veel te veel
    print('\nBest genome:\n{!s}'.format(winner))
    
    #stap 29 hier wordt het beste vogeltje geladen, en de functie best_player gestart
    with open("best.pickle", "wb") as f:
        pickle.dump(winner,f)
        
    best_player("best.pickle", config)
   

#stap 1, dit creëert het pad naar de configuration file, zodat het progamma dit teksbestand kan gebruiken.
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
    
pygame.quit()
