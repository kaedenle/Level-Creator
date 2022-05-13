import pygame, sys, csv
import random, math
from Platform import Level, Platform

pygame.init()
WINDOW_WIDTH = 832
WINDOW_HEIGHT = 640
screen = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
pygame.display.set_caption('Game')
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)
size = 16

WHITE=(255,255,255)
BLUE=(0,0,255)
RED=(255,0,0)
GREEN=(0,255,0)
LIGHT_GRAY = (215, 215, 215)

#Creator is a modified Level class
class Creator(Level):
    def __init__(self, WINDOW_WIDTH, WINDOW_HEIGHT, TILE_SIZE, num):
        super().__init__(num, TILE_SIZE)
        self.WINDOW_WIDTH = WINDOW_WIDTH
        self.WINDOW_HEIGHT = WINDOW_HEIGHT
        
        self.grid_width = WINDOW_WIDTH
        self.grid_height = WINDOW_HEIGHT
        
        
        #scale TILE_SIZE for creator
        self.grid_tile_size = self.TILE_SIZE/(WINDOW_WIDTH/self.grid_width)
        self.scale = 1

        self.window_tile_amount_col = self.WINDOW_WIDTH/(self.grid_tile_size)
        self.window_tile_amount_row = self.WINDOW_HEIGHT/(self.grid_tile_size)
        self.tile_amount_col = self.grid_width/(self.grid_tile_size/self.scale)
        self.tile_amount_row = self.grid_height/(self.grid_tile_size/self.scale)
        
        self.master_list = pygame.sprite.Group()
        self.offset = pygame.Vector2(0, 0)
    #---------------------------------VISUALS---------------------------------
   #Draws the Gridlines
    def drawGridLines(self, display):
        #Horizontal Lines
        for x in range(self.tile_amount_col + 1):
            x_pos = x * (self.grid_tile_size/self.scale) - (self.offset.x % (self.grid_tile_size/self.scale))
            pygame.draw.line(display, LIGHT_GRAY, (x_pos, 0), (x_pos, self.grid_height), 1)
        #Vertical Lines
        for y in range(self.tile_amount_row + 1):
            y_pos = y * (self.grid_tile_size/self.scale) - (self.offset.y % (self.grid_tile_size/self.scale))
            pygame.draw.line(display, LIGHT_GRAY, (0, y_pos), (self.grid_width, y_pos), 1)
    #---------------------------------VARIABLE MANIPULATION---------------------------------
    def add_to_offset(self, x, y):
        #if max left side of max size grid strays off left side
        if(self.offset.x + x < 0):
            self.offset.x = 0
            return
        #if max right side of max size grid strays off right side
        if(self.offset.x + x > (self.window_tile_amount_col - self.tile_amount_col)*self.grid_tile_size/self.scale):
            self.offset.x = (self.window_tile_amount_col - self.tile_amount_col)*self.grid_tile_size/self.scale
            return
        #if max top of max size grid strays off left side
        if(self.offset.y + y < 0):
            self.offset.y = 0
            return
        #if max bottom of max size grid strays off right side
        if(self.offset.y + y > (self.window_tile_amount_row - self.tile_amount_row)*self.grid_tile_size/self.scale):
            self.offset.y = (self.window_tile_amount_row - self.tile_amount_row)*self.grid_tile_size/self.scale
            return
        self.offset.x += x
        self.offset.y += y
        self.update_plat_offset()
    def multiply_scale(self, mult):
        #if new number of tiles on screen is below 0
        if(int(self.grid_width/(self.grid_tile_size/(self.scale * mult))) < 1):
            return
        #if scale exeeds 1
        if(self.scale * mult >= 1):
            self.scale = 1
            self.offset.x = 0
            self.offset.y = 0
            self.update_plat_scale()
            return
        #keeps screen focused on top left when zoomed and offset
        #self.offset /= mult
        if(self.scale != 1):
            max_amount_row = (self.grid_height/self.grid_tile_size)
            saved_tile_size = self.grid_tile_size/self.scale
            saved_tile_row = self.tile_amount_row
            self.scale *= mult
            #update calcs to get new tile_amount
            self.calc_update()
            
            self.offset.y = (self.offset.y/saved_tile_size)/(1 - (saved_tile_row/max_amount_row))
            self.offset.y = (self.offset.y * (1 - (self.tile_amount_row/max_amount_row))) * (self.grid_tile_size/self.scale)
        else:
            self.scale *= mult
        
        self.update_plat_scale()
        
    #---------------------------------PLAT MANIPULATION---------------------------------
    def filter_by_pos(self, row = 0, col = 0):
        #if value is 0, there's no filter on that index
        self.platList.empty()
        for plat in self.master_list:
            #exclude plats if they are off screen
            if((col == 0 or (plat.rect.x <= col and plat.rect.x + (self.grid_tile_size/self.scale) >= 0)) and (row == 0 or (plat.rect.y <= row and plat.rect.y + (self.grid_tile_size/self.scale) >= 0))):
                self.platList.add(plat)
    def update_plat_offset(self):
        #update plat POSITION when scale or offset changes
        for plat in self.master_list:
            plat.rect.x = (self.grid_tile_size/self.scale) * plat.col - self.offset.x
            plat.rect.y = (self.grid_tile_size/self.scale) * plat.row - self.offset.y
        self.calc_update()
        #if offscreen don't render
        self.filter_by_pos(self.tile_amount_row * + (self.grid_tile_size/self.scale), self.tile_amount_col * + (self.grid_tile_size/self.scale))
    def update_plat_scale(self):
        #update plat SCALE when scale changes
        for plats in self.master_list:
            plats.image = plats.get_image(plats.row, plats.col, self.scale)
        self.update_plat_offset()
    def add_at_index(self, row, col):
        max_amount_row = (self.grid_height/self.grid_tile_size)
        max_amount_col = (self.grid_width/self.grid_tile_size)
        #if tiles are off screen
        if(col >= max_amount_col or row >= max_amount_row):
            return
        self.level[row][col] = 1
        self.update_plats()
    def remove_at_index(self, row, col):
        max_amount_row = (self.grid_height/self.grid_tile_size)
        max_amount_col = (self.grid_width/self.grid_tile_size)
        #if tiles are off screen
        if(col >= max_amount_col or row >= max_amount_row):
            return
        self.level[row][col] = 0
        self.update_plats()
    def update_plats(self):
        self.master_list.empty()
        for row, rows in enumerate(self.level):
            for col, tile in enumerate(rows):
                if(self.level[row][col] == 1):
                    self.master_list.add(Platform(row, col, self.grid_tile_size, self.grid_tile_size))
        #update scale of tiles in new masterlist
        self.update_plat_scale()
        #filter if offscreen
        self.filter_by_pos(self.tile_amount_row * + (self.grid_tile_size/self.scale), self.tile_amount_col * + (self.grid_tile_size/self.scale))
    #---------------------------------GENERAL---------------------------------
    def init(self):
        self.level = self.initialize_level()
        self.update_plats()
        
    def initialize_level(self):
        level = []
        for x in range(int(self.window_tile_amount_row)):
            level.append([])
            for y in range(int(self.window_tile_amount_col)):
                level[x].append(0)
        return level
    def calc_update(self):
        self.tile_amount_col = math.ceil(self.grid_width/(self.grid_tile_size/self.scale))
        self.tile_amount_row = math.ceil(self.grid_height/(self.grid_tile_size/self.scale))
        
        self.window_tile_amount_col = math.ceil(self.WINDOW_WIDTH/(self.TILE_SIZE))
        self.window_tile_amount_row = math.ceil(self.WINDOW_HEIGHT/(self.TILE_SIZE))
    def update(self, screen):
        self.calc_update()
        self.platList.draw(screen)
        self.drawGridLines(screen)
        
class Text:
    def __init__(self, text, x, y, font, color):
        self.font = font
        self.text = self.font.render(text, True, (0,0,0))
        self.image = pygame.Surface((300, 50))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.color = color
    def set(self, text):
        self.text = self.font.render(text, True, self.color)
    def draw(self):
        block = self.text
        screen.blit(block, (self.x, self.y))
    def update(self):
        self.draw()

#will start invisible until fade is called
class FadeText(Text):
    def __init__(self, text, x, y, font, color):
        super().__init__(text, x, y, font, color)
        self.cycle = 0
        self.text.set_alpha(0)
    def fadeOut(self):
        #Text will appear then fade out
        self.cycle = 255
    def update(self):
        if(self.cycle > 0):
            self.cycle = max(self.cycle - 4, 0)
            self.text.set_alpha(self.cycle)
        else:
            self.set("")
        self.draw()
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.buttonControl = [False for i in range(3)]
        
        self.inital_mouse_pos = pygame.Vector2(0, 0)
        self.index_row = 0
        self.index_col = 0
        
        self.map = Creator(WINDOW_WIDTH, WINDOW_HEIGHT, size, 0)
        self.map.init()
        self.textList = [Text("", 0, (0+(20*i)), font, (0, 0, 0)) for i in range(5)]
        self.textList.append(FadeText("",WINDOW_WIDTH - 100, 20, font, (0, 0, 0))) 
    def events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.map.add_to_offset(0, -4)
        if keys[pygame.K_DOWN]:
            self.map.add_to_offset(0, 4)
        if keys[pygame.K_RIGHT]:
            self.map.add_to_offset(4, 0)
        if keys[pygame.K_LEFT]:
            self.map.add_to_offset(-4, 0)
        if keys[pygame.K_d]:
            self.map.multiply_scale(2)
        if keys[pygame.K_a]:
            self.map.multiply_scale(0.5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    self.map.save_level()
                    #setup saved text
                    self.textList[-1].color = (0, 255, 0)
                    self.textList[-1].set("Saved!")
                    self.textList[-1].fadeOut()
                if event.key == pygame.K_l:
                    self.map.level = self.map.load_level()
                    #setup loaded text
                    self.textList[-1].color = (0, 0, 255)
                    self.textList[-1].set("Loaded!")
                    self.textList[-1].fadeOut()
                    
                    self.map.update_plats()
                if event.key == pygame.K_SPACE:
                   for row in self.map.level:
                       print(row)
                if event.key == pygame.K_LSHIFT:    #shift click
                    self.buttonControl[2] = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:    #shift click
                    self.buttonControl[2] = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:       #right click
                    self.buttonControl[0] = True
                elif event.button == 1:     #left click
                    self.buttonControl[1] = True
                    self.inital_mouse_pos.x, self.inital_mouse_pos.y = pygame.mouse.get_pos()
                if event.button == 5:       #down scroll (towards user)
                    self.map.multiply_scale(2)
                elif event.button == 4:     #up scroll (away from user)
                    self.map.multiply_scale(0.5)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:       #right click
                    self.buttonControl[0] = False
                if event.button == 1:       #left click
                    self.buttonControl[1] = False
                
    def get_mouse_delta(self):
        x, y = pygame.mouse.get_pos()
        ret = (x - self.inital_mouse_pos.x, y - self.inital_mouse_pos.y)
        self.inital_mouse_pos.x = x
        self.inital_mouse_pos.y = y
        return ret            
    def debugInfo(self):
        self.textList[0].set("scale: " + str(self.map.scale))
        self.textList[1].set("offset: " + str(self.map.offset))
        self.textList[2].set("TILE SIZE: " + str(self.map.grid_tile_size/self.map.scale))
        self.textList[3].set("amount x: " + str(self.map.tile_amount_col))
        self.textList[4].set("amount y: " + str(self.map.tile_amount_row))
        """
        self.textList[5].set("index x: " + str(self.index_col))
        self.textList[6].set("index y: " + str(self.index_row))
        """
    def calc_mouse_index(self):
        x, y = pygame.mouse.get_pos()
        self.index_col = int((x + self.map.offset.x)/(self.map.grid_tile_size/self.map.scale))
        self.index_row = int((y + self.map.offset.y)/(self.map.grid_tile_size/self.map.scale))
    def mouse_events(self):
        #left click
        if(self.buttonControl[1]):
            #left shift click
            if(self.buttonControl[2]):
                delta = self.get_mouse_delta()
                self.map.add_to_offset(-delta[0], -delta[1])
            else:
                self.map.add_at_index(self.index_row, self.index_col)
        #right click
        if(self.buttonControl[0]):
            self.map.remove_at_index(self.index_row, self.index_col)
                
    def update(self):
        self.events()
        self.map.update(screen)
        #mouse click calculations
        self.calc_mouse_index()
        self.mouse_events()
        #right screen
        pygame.draw.rect(screen, (155, 155, 155), (self.map.grid_width, 0, self.map.grid_width, self.map.WINDOW_WIDTH))
        #bottom screen
        pygame.draw.rect(screen, (155, 155, 155), (0, self.map.grid_height, self.map.grid_width, self.map.grid_height))
        self.debugInfo()
        #update text
        for text in self.textList:
            text.update()
        
        
        
game = Game(screen)
while True:      
    pygame.display.update()
    screen.fill(WHITE)
    clock.tick(60)
    game.update()
