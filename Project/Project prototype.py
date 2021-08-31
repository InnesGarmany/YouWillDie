import pygame, sys
from pygame.locals import *
import time
import random
from random import randint
import mysql.connector


pygame.init()
vec = pygame.math.Vector2

#Initialisation
window_length = 1314
window_height = 800

ACC = 1.1
FRIC = -0.05
FramePerSec = pygame.time.Clock()
FPS = 60

#Creating colour tuples
GREY=(128,128,128)
BLACK = (0,0,0)
RED=(255,0,0)
GREEN=(0,255,0)
BLUE=(0,0,255)
WHITE=(255,255,255)

background_image= pygame.image.load('kitchen_background1.jpg')

#Initialisation
DISPLAYSURF = pygame.display.set_mode((window_length, window_height))
pygame.display.set_caption('You. Will. Die.')
no_deaths = 0
player_dead = False
scream = pygame.mixer.Sound('death.mp3')
game_started = False
score_sent = False
input_active = False



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('biff_transparent.png')
        self.surf = pygame.Surface((65, 90))
        self.rect = self.surf.get_rect()

        self.pos = vec((150, window_height-1650))
        self.vel = vec(0,0)
        self.acc = vec(0,0)


        self.game_won = False



    def draw(self, surface):
        surface.blit(self.image, self.rect)






    #Allows the player to jump by adding vertical velocity
    def jump(self):
        collision = pygame.sprite.spritecollide(P, platforms, False)
        if collision:
            self.vel.y = -19
    





    def collision_check(self):
        #Checks for a collision
        collision = pygame.sprite.spritecollide(P, platforms, False)
        touching_trophy = pygame.sprite.spritecollide(P, goal_sprite, False)


        if collision:
            #Places the player on top of any platform they land on and sets their downwards speed to 0
            if self.rect.top < collision[0].rect.top - 70 :
                self.pos.y = collision[0].rect.top + 1
                self.vel.y = 0

                if collision[0].rect.width == 600:
                    self.player_won()

            #Handles the player coming from the side or below
            else:
                #Sets vertical speed to 0 if the player moves up into the platform, has no effect if they fall past it
                if self.vel.y < 0:
                    self.vel.y = 0    

                #If they come from the side the lose sideways momentum
                if self.rect.top <  collision[0].rect.top :

                    #Makes sure the player can't phase into the side of platforms
                    if self.vel.x > 0 or self.acc.x > 0:
                        self.rect.right = collision[0].rect.left 
                    elif self.vel.x<0 or self.acc.x < 0:
                        self.rect.left = collision[0].rect.right
                    self.vel.x = 0
                    self.acc.x = 0
                #If they come from below they are placed below the platform to ensure they can't come up through a platform from below
                else:
                    self.rect.top = collision[0].rect.bottom - 3
        
        if touching_trophy :
            self.game_won = True
            P.player_won()
                        






    def move(self):
        self.acc = vec(0,1)

        key_pressed = pygame.key.get_pressed()

        #Only allows the player to change direction if they are on the ground
        collision = pygame.sprite.spritecollide(P, platforms, False)
        if collision and self.vel.y == 0 and game_started == True:
            if key_pressed[K_LEFT] or key_pressed[K_a]:
                self.acc.x = -ACC

            if key_pressed[K_RIGHT] or key_pressed[K_d]:
                self.acc.x = ACC
            #Makes sure the air doesn't have friction
            self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + (0.5*self.acc)

        #Move the player to the other end of the screen if they go off the side
        if self.pos.x > window_length+30:
            self.pos.x = -30
        if self.pos.x < -30 :
            self.pos.x = window_length+30

        self.rect.midbottom = self.pos

    





    def scroll_screen(self):
        collision = pygame.sprite.spritecollide(P, platforms, False)
        if collision and self.vel.y ==0:

            if self.pos.y < window_height/3*2:
                self.pos.y+= 7
                T.rect.bottom +=7
                for plat in platforms:
                    plat.rect.y += 7
                    if plat.rect.top >= window_height + 90:
                        plat.kill()
                    
    
    def player_dead(self):


        for entity in all_sprites:
           entity.kill()

        death_text_rect = death_text.get_rect()
        death_text_rect.center = (window_length/2,window_height/2 )


        restart_text = small_font.render('Click to retry.', True, WHITE )
        restart_text_rect = restart_text.get_rect()
        restart_text_rect.center = (window_length/2, window_height/2+60)

        DISPLAYSURF.blit(death_text, death_text_rect)
        DISPLAYSURF.blit(restart_text, restart_text_rect)






    def player_won(self):


        #Renders text congratulating player
        end_text= title_font.render("You beat the game!", True, RED, WHITE)
        end_text_rect = end_text.get_rect()
        end_text_rect.center = (window_length/2, window_height/10*2)

        #Renders different text based on how well the player did
        if no_deaths == 0:
            final_message = ("YOU DIDN'T DIE, NOT EVEN ONCE! YOU ARE THE GAMER-GOD!")
        elif no_deaths == 1:
            final_message = ("So close to perfection, excellent job!")
        elif no_deaths <11:
            final_message = ("You only died " + str(no_deaths) + " times, stellar job.")
        elif no_deaths <21:
            final_message = ("You died a few times but you made it, and with a respectable score of " + str(no_deaths) + " deaths.")
        else:
            final_message = ("You persevered and made it through, dying " + str(no_deaths) + " times - well done.")



        final_text = smaller_font.render(str(final_message), True, RED, WHITE)
        final_text_rect = final_text.get_rect()
        final_text_rect.center = (window_length/2,window_height/10*3)

        #Prints the text rendered above
        DISPLAYSURF.blit(end_text, end_text_rect)
        DISPLAYSURF.blit(final_text, final_text_rect)


        #Sends the player's score to the database and fetches the leaderboard
        if score_sent == True:
            score_sent = True
            mydb = mysql.connector.connect(
                host = "localhost"
                user = "root"
                password = ""
                charset = "utf8"
                database = "You. Will. Die."
            )

            curs = mydb.cursor()
            curs.execute("INSERT VALUES (player_score) INTO deaths")
            curs.execute("SELECT * FROM deaths")

            list_scores = curs.fetchall()
            #Bubble sort to put 5 top scores to top of list
            swapped = True
            x = 0
            while swapped == False and x < 5:
                swapped = False
                x+=1
                for i in range(0, len(list_scores)-x):
                    if list_scores(i) > list_scores(i+1):
                        list_scores(i), list_scores(i+1) = list_scores(i+1), list_scores(i)
                        swapped = True
        

        #Renders and displays leaderboard
        for y in range(1,5):
            end_text= small_font.render("1st: " + list_scores(len(list_scores)-y), True, RED, WHITE)
            end_text_rect = end_text.get_rect()
            end_text_rect.center = (window_length/2, window_height + (1300-100*y))




        
def reset_game():

    #resets player position
    P.pos = vec((100, window_height-10))
    P.vel = vec(0,0)
    P.acc = vec(0,0)

    T.rect.center = (window_length-100, window_height - 1788)

    #resets platform positions
    PT1 = Platform(window_length, window_length/2, window_height - 5)
    PT2 = Platform(200, window_length - 100, window_height - 175)
    PT3 = Platform(200, window_length - 550, window_height - 320)
    PT4= Platform(200, window_length - 850, window_height - 470)
    PT5 = Platform(300, window_length - 625, window_height - 600)
    PT6 = Platform(400, window_length - 400, window_height - 725)
    PT7 = Platform(200, window_length - 800, window_height - 850)
    PT8 = Platform(250, 125, window_height - 1000)
    PT9 = Platform(300, window_length - 700, window_height - 1100)
    PT10 = Platform(500, window_length - 250, window_height - 1250)
    PT11 = Platform(225, window_length - 625, window_height - 1400)
    PT12 = Platform(260, window_length - 1000, window_height - 1450)
    PT13 = Platform(176, 88, window_height - 1550)
    PT14 = Platform(300, window_length - 900, window_height - 1675)
    PT15 = Platform(600, window_length - 300, window_height - 1750)

    #adds reset platforms back to the platform group
    platforms.add(PT1)
    platforms.add(PT2)
    platforms.add(PT3)
    platforms.add(PT4)
    platforms.add(PT5)
    platforms.add(PT6)
    platforms.add(PT7)
    platforms.add(PT8)
    platforms.add(PT9)
    platforms.add(PT10)
    platforms.add(PT11)
    platforms.add(PT12)
    platforms.add(PT13)
    platforms.add(PT14)
    platforms.add(PT15)


    #Adds reset sprites to the all sprites group
    all_sprites.add(P)
    all_sprites.add(T)
    for entity in platforms:
        all_sprites.add(entity)

    DISPLAYSURF.blit(background_image, (0,0))

    for entity in all_sprites:
        entity.draw(DISPLAYSURF)






class Platform(pygame.sprite.Sprite):
    def __init__(self, length, centerX, centerY):
        super().__init__()
        self.surf = pygame.Surface((length, 10))
        self.surf.fill(GREY)
        self.rect = self.surf.get_rect(center = (centerX, centerY))

    def draw(self, surface):
        surface.blit(self.surf, self.rect )

class Trophy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image= pygame.image.load('trophy.png')
        self.surf=pygame.Surface((45, 70))
        self.rect = self.surf.get_rect()
        
        self.rect.center = (window_length-100, window_height - 1788)

    def draw(self, surface):
        surface.blit(self.image, self.rect)







    
    







#Creates 3 different fonts
large_font = pygame.font.Font('freesansbold.ttf', 70)
small_font = pygame.font.Font('freesansbold.ttf', 50)
smaller_font = pygame.font.Font('freesansbold.ttf', 35)
deaths_font = pygame.font.Font ('freesansbold.ttf', 30)
title_font = pygame.font.Font('freesansbold.ttf', 65)    



#Various messages which can be played upon the player's death
death_message = ["You died there? I didn't know that was possible.", "You can do it, don't give up!"]
death_message.append("You died. Better luck next time, Champ!")
death_message.append("I'm impressed that you managed to die there")
death_message.append("Persevere - you'll get there, eventually")
death_message.append("I really though that would be the one")
death_message.append("You going for the high score?")
death_message.append("You know that dying is a bad thing, right?")
death_message.append("Next time; try not to die")
death_message.append("Ooh, I felt that one")
death_message.append("Keep going, someone must have a worse score")



#Creates player and platform objects
P = Player()
T = Trophy()
PT1 = Platform(window_length, window_length/2, window_height - 5)
#Reminder of window size: window_length = 1314       window_height = 800
#Reminder of platform parameters(length, centerX, centerY)
PT2 = Platform(200, window_length - 100, window_height - 175)
PT3 = Platform(200, window_length - 550, window_height - 320)
PT4= Platform(200, window_length - 850, window_height - 470)
PT5 = Platform(300, window_length - 625, window_height - 600)
PT6 = Platform(400, window_length - 400, window_height - 725)
PT7 = Platform(200, window_length - 800, window_height - 850)
PT8 = Platform(250, 125, window_height - 1000)
PT9 = Platform(300, window_length - 700, window_height - 1100)
PT10 = Platform(500, window_length - 250, window_height - 1250)
PT11 = Platform(225, window_length - 625, window_height - 1400)
PT12 = Platform(260, window_length - 1000, window_height - 1450)
PT13 = Platform(176, 88, window_height - 1550)
PT14 = Platform(300, window_length - 900, window_height - 1675)
PT15 = Platform(600, window_length - 300, window_height - 1750)


#Creates a grouping of all the platforms
platforms = pygame.sprite.Group()
platforms.add(PT1)
platforms.add(PT2)
platforms.add(PT3)
platforms.add(PT4)
platforms.add(PT5)
platforms.add(PT6)
platforms.add(PT7)
platforms.add(PT8)
platforms.add(PT9)
platforms.add(PT10)
platforms.add(PT11)
platforms.add(PT12)
platforms.add(PT13)
platforms.add(PT14)
platforms.add(PT15)



#Creates a grouing of all sprites
all_sprites =  pygame.sprite.Group()
all_sprites.add(P)
all_sprites.add(T)
for entity in platforms:
    all_sprites.add(entity)

goal_sprite = pygame.sprite.Group()
goal_sprite.add(T)

#Renders start screen
title_text = title_font.render("You. Will. Die.", True, RED)
title_text_rect = title_text.get_rect()
title_text_rect.center = (window_length/2, window_height/2)


start_prompt = small_font.render("Click anywhere to start", True, RED)
start_prompt_rect = start_prompt.get_rect()
start_prompt_rect.center = (window_length/2, window_height/2+45)


while True: # main game loop

    for event in pygame.event.get():        
        


        if game_started == False:
            if event.type == pygame.MOUSEBUTTONDOWN:
                game_started = True

        else:
            if event.type == QUIT:
                pygame.quit()
                sys.exit()     
 
            if event.type == KEYDOWN:

                if event.key == pygame.K_UP  or event.key == pygame.K_w:
                    P.jump()

            if player_dead == True and event.type == pygame.MOUSEBUTTONDOWN:
                pygame.time.delay(300)
                reset_game()
                player_dead = False


    DISPLAYSURF.blit(background_image, (0,0))

    P.move()
    P.collision_check()
    if P.rect.bottom < window_height/3*2:   
        P.scroll_screen()



    for entity in all_sprites:
        entity.draw(DISPLAYSURF)


    #Renders and displayes a live deaths tally in the top right corner of the screen
    death_counter = deaths_font.render('Deaths: ' + str(no_deaths), True, WHITE)
    death_counter_rect = death_counter.get_rect()
    death_counter_rect.center = (window_length - 100 , 15)
    DISPLAYSURF.blit(death_counter, death_counter_rect)


    if P.rect.top > window_height:



        #Tallys the player's deaths
        if player_dead == False:
            scream.play()
            no_deaths+=1   
            player_dead = True
            #Creates a death message which is randomly selected after the first death
            if no_deaths == 1:       
                death_text = large_font.render('Told you', True, RED, WHITE)
            else:
                message_no = randint(0, len(death_message)-1)
                death_text = large_font.render(death_message[message_no], True, RED, WHITE)


        #Continually updates the screen with the death message
        P.player_dead()

    

    
    #Displays start screen
    if game_started == False:
        DISPLAYSURF.blit(start_prompt, start_prompt_rect)
        DISPLAYSURF.blit(title_text, title_text_rect)






    pygame.display.update()
    FramePerSec.tick(FPS)
