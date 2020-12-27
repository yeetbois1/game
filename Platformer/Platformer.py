import pygame, sys, os, random, pytmx

clock = pygame.time.Clock()

from pygame.locals import *

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()  # initiates pygame

pygame.display.set_caption('Pygame Platformer')

WINDOW_SIZE = (600, 400)

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)  # initiate the window

display = pygame.Surface((300, 200))  # used as the surface for rendering, which is scaled

global animation_frames
animation_frames = {}

def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        # player_animations/idle/idle_0.png
        animation_image = pygame.image.load(img_loc).convert()
        animation_image.set_colorkey((255, 255, 255))
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data


def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


def collision_test(rect, tiles, level):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile[0]):
            hit_list.append(tile[0])
            if tile[1] == 1:
                level = True
            
    return hit_list, level


def move(rect, movement, tiles, level):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list, level = collision_test(rect, tiles, level)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list, level = collision_test(rect, tiles, level)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types, level

def collision_test2(rect, tiles, level):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile[0]):
            hit_list.append(tile[0])
            if tile[1] == 3:
                level = True
            
    return hit_list, level


def move2(rect, movement, tiles, level):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    hit_list, level = collision_test(rect, tiles, level)
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list, level = collision_test(rect, tiles, level)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types, level

def menu():
    button_1 = pygame.Rect(130, 290, 60, 20)
    button_2 = pygame.Rect(260, 290, 60, 20)
    button1_surface = pygame.Surface((60,20))
    button2_surface = pygame.Surface((60,20))
    button_1.centery = 200
    button_2.centery = 200
    button_1.centerx = 150
    button_2.centerx = 430
    font = pygame.font.SysFont('arial', 20)

    while True:
        screen.fill((0,0,0))

        pygame.draw.rect(button1_surface, (55,255,0), (0, 0, 60, 20))
        pygame.draw.rect(button2_surface, (55,255,0), (0, 0, 60, 20))

        start_txt = font.render('Start', 1, (255,255,255))
        controls_txt = font.render('Controls', 1, (255,255,255))

        button1_surface.blit(start_txt, ((60-(start_txt.get_width()))/2, (20-(start_txt.get_height()))/2))
        button2_surface.blit(controls_txt, ((60-(controls_txt.get_width()))/2, (20-(controls_txt.get_height()))/2))

        screen.blit(button1_surface, (120, 190))
        screen.blit(button2_surface, (400, 190))
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint(event.pos):
                        level1()
                        break
                    if button_2.collidepoint(event.pos):
                        controls()
                        break
        
        
        pygame.display.update()

def level1():
    pygame.mixer.music.load('music.wav')
    pygame.mixer.music.play(-1)
    level1_map = pytmx.load_pygame('level1.tmx')

    moving_right = False
    moving_left = False
    vertical_momentum = 0
    air_timer = 0
    level = False

    timer = 60
    timetick = 0

    grass_sound_timer = 0

    true_scroll = [0, 0]
    
    animation_database = {}

    animation_database['run'] = load_animation('player_animations/run', [7, 7])
    animation_database['idle'] = load_animation('player_animations/idle', [7, 7, 40])\

    grass_img = pygame.image.load('grass.png')
    dirt_img = pygame.image.load('dirt.png')
    flag_img = pygame.image.load('flag.png')

    jump_sound = pygame.mixer.Sound('jump.wav')
    grass_sounds = [pygame.mixer.Sound('grass_0.wav'), (pygame.mixer.Sound('grass_1.wav'))]

    for sound in grass_sounds:
        sound.set_volume(0.2)

    player_action = 'idle'
    player_frame = 0
    player_flip = False

    player_rect = pygame.Rect(100, 100, 5, 13)

    background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                          [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

    font = pygame.font.SysFont('arial', 50)

    while True:  # game loop
        timetick+=1
        if timetick == 60:
            timetick = 0
            timer-=1
        if timer == 0:
            lose_screen()
        if grass_sound_timer > 0:
            grass_sound_timer -= 1
        display.fill((146, 244, 255))  # clear screen by filling it with blue
        if player_rect.y > 400:
            player_rect.x = 100
            player_rect.y = 0

        true_scroll[0] += (player_rect.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player_rect.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                                   background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                                   background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(display, (14, 222, 150), obj_rect)
            else:
                pygame.draw.rect(display, (9, 91, 85), obj_rect)

        tile_rects = []
        y = 0
        for layer in level1_map.visible_layers:
            x = 0
            for x, y, tile in layer:
                if tile == 3:
                    display.blit(dirt_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile == 2:
                    display.blit(grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile == 1:
                    display.blit(flag_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile != 0:
                    tile_rects.append([pygame.Rect(x * 16, y * 16, 16, 16), tile])
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right == True:
            player_movement[0] += 2
        if moving_left == True:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player_action, player_frame = change_action(player_action, player_frame, 'idle')
        if player_movement[0] > 0:
            player_flip = False
            player_action, player_frame = change_action(player_action, player_frame, 'run')
        if player_movement[0] < 0:
            player_flip = True
            player_action, player_frame = change_action(player_action, player_frame, 'run')

        player_rect, collisions, level = move(player_rect, player_movement, tile_rects, level)
        if level:
            level2(grass_img, dirt_img, flag_img, jump_sound, grass_sounds)

        if collisions['bottom'] == True:
            air_timer = 0
            vertical_momentum = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        else:
            air_timer += 1

        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0
        player_img_id = animation_database[player_action][player_frame]
        player_img = animation_frames[player_img_id]
        display.blit(pygame.transform.flip(player_img, player_flip, False),
                     (player_rect.x - scroll[0], player_rect.y - scroll[1]))
        timertxt = font.render(str(timer), 1, (255,255,255))
        display.blit(timertxt, (0,0))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_SPACE:
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_momentum = -3
                if event.key == K_w:
                    pygame.mixer.music.fadeout(1000)
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)

def controls():
    font = pygame.font.SysFont('arial', 20)
    line1 = font.render('Press the right arrow key to go right', 1, (255,255,255))
    line2 = font.render('Press the left arrow key to go left', 1, (255,255,255))
    line3 = font.render('Press the space bar to jump', 1, (255,255,255))
    buttonline = font.render('Menu', 1, (255,255,255))

    button_1 = pygame.Rect(540, 0, 60, 20)
    button1_surface = pygame.Surface((60,20))

    while True:
        screen.fill((0,0,0))

        screen.blit(line1, (0,0))
        screen.blit(line2, (0,20))
        screen.blit(line3, (0,40))

        pygame.draw.rect(button1_surface, (55,255,0), (0,0,60,20))
        button1_surface.blit(buttonline, ((60-(buttonline.get_width()))/2, (20-(buttonline.get_height()))/2))
        screen.blit(button1_surface, (540, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint(event.pos):
                        menu()
                        break

        pygame.display.update()

def level2(grass_img, dirt_img, flag_img, jump_sound, grass_sounds):
    level1_map = pytmx.load_pygame('level2.tmx')

    moving_right = False
    moving_left = False
    vertical_momentum = 0
    air_timer = 0
    level = False

    timer = 120
    timetick = 0

    grass_sound_timer = 0

    true_scroll = [0, 0]
    
    animation_database = {}

    animation_database['run'] = load_animation('player_animations/run', [7, 7])
    animation_database['idle'] = load_animation('player_animations/idle', [7, 7, 40])\

    grass_img = pygame.image.load('grass.png')
    dirt_img = pygame.image.load('dirt.png')
    flag_img = pygame.image.load('flag.png')

    jump_sound = pygame.mixer.Sound('jump.wav')
    grass_sounds = [pygame.mixer.Sound('grass_0.wav'), (pygame.mixer.Sound('grass_1.wav'))]

    for sound in grass_sounds:
        sound.set_volume(0.2)

    player_action = 'idle'
    player_frame = 0
    player_flip = False

    player_rect = pygame.Rect(100, 100, 5, 13)

    background_objects = [[0.25, [120, 10, 70, 400]], [0.25, [280, 30, 40, 400]], [0.5, [30, 40, 40, 400]],
                          [0.5, [130, 90, 100, 400]], [0.5, [300, 80, 120, 400]]]

    font = pygame.font.SysFont('arial', 50)

    while True:  # game loop
        timetick+=1
        if timetick == 60:
            timetick = 0
            timer-=1
        if timer == 0:
            lose_screen()
        if grass_sound_timer > 0:
            grass_sound_timer -= 1
        display.fill((146, 244, 255))  # clear screen by filling it with blue
        if player_rect.y > 400:
            player_rect.x = 100
            player_rect.y = 0

        true_scroll[0] += (player_rect.x - true_scroll[0] - 152) / 20
        true_scroll[1] += (player_rect.y - true_scroll[1] - 106) / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])

        pygame.draw.rect(display, (7, 80, 75), pygame.Rect(0, 120, 300, 80))
        for background_object in background_objects:
            obj_rect = pygame.Rect(background_object[1][0] - scroll[0] * background_object[0],
                                   background_object[1][1] - scroll[1] * background_object[0], background_object[1][2],
                                   background_object[1][3])
            if background_object[0] == 0.5:
                pygame.draw.rect(display, (14, 222, 150), obj_rect)
            else:
                pygame.draw.rect(display, (9, 91, 85), obj_rect)

        tile_rects = []
        y = 0
        for layer in level1_map.visible_layers:
            x = 0
            for x, y, tile in layer:
                if tile == 2:
                    display.blit(dirt_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile == 1:
                    display.blit(grass_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile == 3:
                    display.blit(flag_img, (x * 16 - scroll[0], y * 16 - scroll[1]))
                if tile != 0:
                    tile_rects.append([pygame.Rect(x * 16, y * 16, 16, 16), tile])
                x += 1
            y += 1

        player_movement = [0, 0]
        if moving_right == True:
            player_movement[0] += 2
        if moving_left == True:
            player_movement[0] -= 2
        player_movement[1] += vertical_momentum
        vertical_momentum += 0.2
        if vertical_momentum > 3:
            vertical_momentum = 3

        if player_movement[0] == 0:
            player_action, player_frame = change_action(player_action, player_frame, 'idle')
        if player_movement[0] > 0:
            player_flip = False
            player_action, player_frame = change_action(player_action, player_frame, 'run')
        if player_movement[0] < 0:
            player_flip = True
            player_action, player_frame = change_action(player_action, player_frame, 'run')

        player_rect, collisions, level = move2(player_rect, player_movement, tile_rects, level)
        if level:
            win_screen()

        if collisions['bottom'] == True:
            air_timer = 0
            vertical_momentum = 0
            if player_movement[0] != 0:
                if grass_sound_timer == 0:
                    grass_sound_timer = 30
                    random.choice(grass_sounds).play()
        else:
            air_timer += 1

        player_frame += 1
        if player_frame >= len(animation_database[player_action]):
            player_frame = 0
        player_img_id = animation_database[player_action][player_frame]
        player_img = animation_frames[player_img_id]
        display.blit(pygame.transform.flip(player_img, player_flip, False),
                     (player_rect.x - scroll[0], player_rect.y - scroll[1]))
        timertxt = font.render(str(timer), 1, (255,255,255))
        display.blit(timertxt, (0,0))

        for event in pygame.event.get():  # event loop
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_SPACE:
                    if air_timer < 6:
                        jump_sound.play()
                        vertical_momentum = -3
                if event.key == K_w:
                    pygame.mixer.music.fadeout(1000)
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False

        screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
        pygame.display.update()
        clock.tick(60)

def lose_screen():
    pygame.mixer.music.stop()
    font = pygame.font.SysFont('arial', 20)
    buttonline = font.render('Menu', 1, (255,255,255))

    button_1 = pygame.Rect(540, 0, 60, 20)
    button1_surface = pygame.Surface((60,20))
    line1 = font.render('You lost', 1, (255,255,255))

    while True:
        screen.fill((0,0,0))

        pygame.draw.rect(button1_surface, (55,255,0), (0,0,60,20))
        screen.blit(line1, (0,0))
        button1_surface.blit(buttonline, ((60-(buttonline.get_width()))/2, (20-(buttonline.get_height()))/2))
        screen.blit(button1_surface, (540, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint(event.pos):
                        menu()
                        break

        pygame.display.update()

def win_screen():
    pygame.mixer.music.stop()
    font = pygame.font.SysFont('arial', 50)
    buttonline = font.render('Menu', 1, (255,255,255))

    button_1 = pygame.Rect(540, 0, 60, 20)
    button1_surface = pygame.Surface((60,20))
    line1 = font.render('You win!', 1, (255,255,255))

    while True:
        screen.fill((0,0,0))

        pygame.draw.rect(button1_surface, (55,255,0), (0,0,60,20))
        screen.blit(line1, (0,0))
        button1_surface.blit(buttonline, ((60-(buttonline.get_width()))/2, (20-(buttonline.get_height()))/2))
        screen.blit(button1_surface, (540, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button_1.collidepoint(event.pos):
                        menu()
                        break

        pygame.display.update()
    
menu()
