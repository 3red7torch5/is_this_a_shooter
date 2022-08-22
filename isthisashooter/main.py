import pygame as pg
import random, math
pg.init()
pg.mixer.init()
FPS = 60
clock = pg.time.Clock()
scale = 1
width = int(600*scale)
height = int(900*scale)
window = pg.display.set_mode((width,height))
pg.display.set_caption("is this a shooter?")
pg.display.set_icon(pg.image.load("app.bmp"))
barrier = height//5
controllability = 8
enablesound = True
enablemusic = False
fon0 = pg.image.load("f0.png")
fon1 = pg.transform.flip(fon0,True,True)
fon = fon0
active = True
tick = 1
fon_a = 127
boom = pg.transform.scale(pg.image.load("boom.png"),(100,100))
cross_rotate_factor=360/width
#классы
class sound():
    music = pg.mixer.Sound("music.ogg")
    music.set_volume(0.15)
    blop0 = pg.mixer.Sound("blop0.ogg")
    blop0.set_volume(0.02)
    blop1 = pg.mixer.Sound("blop1.ogg")
    blop1.set_volume(0.02)
sprites = []
class GameSprite(pg.sprite.Sprite):
    def __init__(self,x,y,x_vel,y_vel,image,x_width,y_height):
        sprites.append(self)
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.x_width = x_width
        self.y_height = y_height
        self.image = pg.transform.scale(pg.image.load(image),(x_width,y_height))
    def draw(self):
        window.blit(self.image,(self.x-(self.x_width//2),self.y-(self.y_height//2)))
textures = []
class texture(pg.sprite.Sprite):
    def __init__(self,x,y,image,x_width,y_height,timer):
        textures.append(self)
        self.priority = 0
        self.x,self.y = x,y
        self.image = pg.transform.scale(pg.image.load(image),(x_width,y_height))
        self.timer = timer
        self.a_factor = 255/self.timer
        self.image.set_alpha(self.timer*self.a_factor)
    def update(self):
        self.timer-=1
        self.image.set_alpha(self.timer*self.a_factor)
        if self.timer <= 0:
            textures.remove(self)
    def draw(self):
        window.blit(self.image,(self.x,self.y))
class crosshair(GameSprite):
    def __init__(self,x,y,x_vel,y_vel,image,x_width,y_height):
        GameSprite.__init__(self,x,y,x_vel,y_vel,image,x_width,y_height)
        self.priority = 0
        self.root_img = self.image
        self.alt_img = pg.transform.smoothscale(pg.image.load("cross1.png"), (self.x_width, self.y_height))
    def update(self):
        global barrier,controllability
        mpos = pg.mouse.get_pos()
        stable(self)
        self.x_vel += (mpos[0] - self.x)//4
        self.y_vel += (mpos[1] - self.y)//4
        #if self.x_vel in range(-controllability,controllability):
        #    self.x = mpos[0]
        #    self.x_vel = 0
        #if self.y_vel in range(-controllability,controllability):
        #    self.y = mpos[1]
        #    self.y_vel = 0
        self.x += self.x_vel//controllability
        self.y += self.y_vel//controllability
        if self.y < barrier:
            self.image = self.alt_img
        else:
            self.image = self.root_img
        if self.x-(self.x_width//2)<=0:
            self.x = self.x_width//2
            self.x_vel = -(self.x_vel//2)
        if self.x+(self.x_width//2)>=width:
            self.x = width-(self.x_width//2)
            self.x_vel = -(self.x_vel//2)
targets = []
class target(GameSprite):
    def __init__(self,image,x_width,y_height):
        targets.append(self)
        self.priority = 5
        x,y = random.randint(x_width,width-x_width),-random.randint(80,120)
        x_vel,y_vel = random.randint(-20,20),random.randint(30,70)
        GameSprite.__init__(self, x, y, x_vel, y_vel, image, x_width, y_height)
        self.root_img = self.image
        self.alt_img = pg.transform.smoothscale(pg.image.load("target1.png"),(self.x_width,self.y_height))
    def respawn(self):
        expl = texture(self.x-(self.x_width//2),self.y-(self.y_height//2),"boom.png",int(100*scale),(100*scale),10)
        if enablesound:
            if bool(random.randint(0,1)):
                sound.blop0.play()
            else:
                sound.blop1.play()
        self.x, self.y = random.randint(self.x_width,width-self.x_width),-random.randint(80,120)
        self.x_vel,self.y_vel = random.randint(-20,20),random.randint(30,70)
    def update(self):
        stable(self)
        if self.y <= barrier:
            self.available = False
            self.image = self.alt_img
        else:
            self.available = True
            self.image = self.root_img
        if self.y >= height:
            self.respawn()
        else:
            self.x += self.x_vel//10
            self.y += self.y_vel//10
        if self.x-(self.x_width//2)<=0:
            self.x = self.x_width//2
            self.x_vel = -self.x_vel
        if self.x+(self.x_width//2)>=width:
            self.x = width-(self.x_width//2)
            self.x_vel = -self.x_vel
magnets = []
class magnet(GameSprite):
    def __init__(self,x,y,image,x_width,y_height,power,timer):
        magnets.append(self)
        GameSprite.__init__(self,x,y,0,0,image,x_width,y_height)
        self.priority = 0
        self.power = power
        self.timer = timer
        self.a_factor = 255/self.timer
        self.image.set_alpha(self.timer*self.a_factor)
    def update(self):
        for q in targets:
            if q.available:
                q.x_vel+=((self.x - q.x)//10)*self.power
                q.y_vel+=((self.y - q.y)//10)*self.power
        self.timer-=1
        self.image.set_alpha(self.timer*self.a_factor)
        if self.timer <= 0:
            magnets.remove(self)
            sprites.remove(self)
#функции
def entertimestop():
    for k in sprites:
        if k != pcross:
            k.priority = 11
    for k in textures:
        k.priority = 11
def exittimestop():
    for k in sprites:
        if k != pcross:
            k.priority = 0
    for k in textures:
        k.priority = 0
def fon_toggle():
    global fon,fon0,fon1
    fon0.set_alpha(120)
    fon1.set_alpha(120)
    if fon == fon0:
        fon = fon1
    elif fon == fon1:
        fon = fon0
    else:
        pass
def stable(a):
    if a.x_vel < -100:
        a.x_vel += 5
    elif a.x_vel > 100:
        a.x_vel -= 5
    if a.y_vel < -100:
        a.y_vel += 5
    elif a.y_vel > 100:
        a.y_vel -= 5
    a.x_vel,a.y_vel=int(a.x_vel),int(a.y_vel)
#создание всякого
for _ in range(10):
    stone = target("target.png",int(100*scale),int(100*scale))
circle0 = magnet(500,400,"magnet.png",25,25,0.5,200)
pcross = crosshair(width//2,height//2,0,0,"cross.png",int(128*scale),int(128*scale))
#музычка
if enablemusic:
    sound.music.play(-1)
#главный цикл
while active:
    #тикрейт
    clock.tick(FPS)
    #просчет который сейчас тик
    if tick < 10:
        tick+=1
    else:
        tick=0
    #получение списка нажатых клавишь
    keys = pg.key.get_pressed()
    #очистка окна и приколы с фоном
    if fon_a>=0:
        fon_a-=3
    else:
        fon_toggle()
        fon_a=120
    if fon == fon0:
        fon1.set_alpha(120)
        fon0.set_alpha(fon_a)
        window.blit(fon1,(0,0))
        window.blit(fon0, (0, 0))
    elif fon == fon1:
        fon0.set_alpha(120)
        fon1.set_alpha(fon_a)
        window.blit(fon0, (0, 0))
        window.blit(fon1, (0, 0))
    pg.draw.line(window,(255,255,255),(0,barrier),(width,barrier))
    #выход
    if keys[pg.K_ESCAPE]:
        active = False
    for e in pg.event.get():
        if e.type == pg.QUIT:
            active = False
    #приколы
    mpos = pg.mouse.get_pos()
    if keys[pg.K_LALT]:
        entertimestop()
    else:
        exittimestop()
    if keys[pg.K_SPACE] and circle0.timer == 0:
        circle0 = magnet(mpos[0],mpos[1],"magnet.png", 25, 25, 0.5, 30)
    #проверка попадания
    for s in targets:
        if s.x in range(pcross.x-(s.x_width//3),pcross.x+(s.x_width//3)) and s.y in range(pcross.y-(s.y_height//3),pcross.y+(s.y_height//3))and s.available:
            s.respawn()
    #рендер и обновление спрайтов
    for s in sprites:
        s.draw()
    for t in textures:
        t.draw()
    for s in sprites:
        if tick >= s.priority:
            s.update()
    for t in textures:
        if tick >= t.priority:
            t.update()
    #обновление экрана
    pg.display.flip()