import sys

import pygame
from pygame.locals import KEYDOWN

from config import black, white
from connect_game import ConnectGame
from events import MouseClickEvent, MouseHoverEvent, bus
from game_data import GameData, PLAYER
from game_renderer import GameRenderer

from agents import Agent

import argparse

r'''
-- person vs person
python game.py
-- person vs AI
python game.py -p1 "RandomAgent"
-- AI vs AI
python game.py -p1 "MinimaxAgent" -p2 "RandomAgent"
-- AI vs AI - no gui
python game.py -e -p2 "MinimaxAgent" -p1 "MinimaxAgent"
#TODO - argument for how many times to evaluate
'''

HUMAN = "Human"
def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    clicked = pygame.mouse.get_pressed()[0]

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        #Mouse is in the button
        # print("IN: ", msg, clicked, action)
        pygame.draw.rect(screen, ac, (x, y, w, h))

        if clicked and action is not None:
            action()
    else:
        #Mouse is not in the button
        # print("button-2:   ", msg)
        pygame.draw.rect(screen, ic, (x, y, w, h))

    small_text = pygame.font.SysFont("monospace", 30)
    text_surf, text_rect = text_objects(msg, small_text, white)
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(text_surf, text_rect)

def parse_args():
    parser = argparse.ArgumentParser(description='Start the game.')
    parser.add_argument('-p1', '--player1', type=str, required=False, help='player 1 - Agent Name or Human', default=HUMAN)
    parser.add_argument('-p2', '--player2', type=str, required=False, help='player 2 - Agent Name or Human', default=HUMAN)
    parser.add_argument('-e', '--evaluate', action='store_true', help='evaluates 2 agents.  Requires p1 and p2 to be agents')

    return parser.parse_args()

def quit():
    sys.exit()

def getAgent(name: str) -> Agent:
    """
    NOTE: will throw ModuleNotFoundError if not found
    """
    module = __import__(name)
    class_ = getattr(module, name)
    return class_()

def getPlayer(p1, p2, data):
        p = p1 if PLAYER(data.turn) == PLAYER.Player1 else p2
        p_is_human = p is None
        # print(PLAYER(data.turn),"p=",p,"h=",p_is_human)
        return p_is_human, p

def evaluate():
    if args.player1 == HUMAN or args.player1 == HUMAN:
        raise Exception("Both players need to be AI")
    p1 = getAgent(args.player1)
    p2 = getAgent(args.player2)
    #compare_agents(agent1: Agent, agent2: Agent, n=5, alternate=True, print_progress=True) 
    data = GameData()
    game = ConnectGame(data, GameRenderer(screen, data))
    res = game.compare_agents(p1, p2, n=5, alternate=True, print_progress=True) 
    print("res:", res)

def start():
    print("+++++++++++++++ start +++++++++++++++++++++++")

    #NOTE: None means Human player
    p1 = None  # red
    p2 = None  # yellow
    if args.player1 != HUMAN:
        # print ("p1 is NOT human")
        p1 = getAgent(args.player1)
    if args.player2 != HUMAN:
        # print ("p2 is NOT human")
        p2 = getAgent(args.player2)

    data = GameData()
    screen = pygame.display.set_mode(data.size)
    game = ConnectGame(data, GameRenderer(screen, data))

    game.print_board()
    game.draw()

    pygame.display.update()
    pygame.time.wait(1000)

    #NOTE: data.turn of 0 == player 1
    #      data.turn of 1 == player 2

    # Processes mouse and keyboard events, dispatching events to the event bus.
    # The events are handled by the ConnectGame and GameRenderer classes.
    p_is_human, p = getPlayer(p1, p2, data)

    #TODO - better way to clean screen?
    bus.emit("mouse:hover", game.renderer, MouseHoverEvent(-50))

    while not game.game_data.game_over:
        pygame.time.wait(10)
        if p_is_human:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.quit()

                if event.type == pygame.MOUSEMOTION:
                    bus.emit("mouse:hover", game.renderer, MouseHoverEvent(event.pos[0]))

                pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    # print("HUMAN: Mouse:",PLAYER(data.turn),p_is_human,p)
                    bus.emit("mouse:click", game, MouseClickEvent(event.pos[0]))
                    p_is_human, p = getPlayer(p1, p2, data)

                # if event.type == KEYDOWN:
                #     if event.key == pygame.K_z:
                #         mods: int = pygame.key.get_mods()
                #         if mods & pygame.KMOD_CTRL:
                #             bus.emit("game:undo", game)
        else:
            #AI
            print("AI:",PLAYER(data.turn), p.get_name())
            game.make_movement(p.get_move(data), p.get_name())
            p_is_human, p = getPlayer(p1, p2, data)
            #keep pygame happy - otherwise freezes
            for event in pygame.event.get():
                pass

        game.update()
        game.draw()
    print("--------------------- GAME OVER ----------------------------")
    pygame.display.update()

def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def message_display(text, color, p, q, v):
    large_text = pygame.font.SysFont("monospace", v)
    text_surf, text_rect = text_objects(text, large_text, color)
    text_rect.center = (p, q)
    screen.blit(text_surf, text_rect)


if __name__ == '__main__':
    args = parse_args()
    screen = None
    if args.evaluate:
        evaluate()
        sys.exit()
    pygame.init()
    screen = pygame.display.set_mode(GameData().size)
    pygame.display.set_caption("Connect Four - AI version")
    message_display("CONNECT FOUR!!", white, 350, 150, 75)
    message_display("HAVE FUN!", (23, 196, 243), 350, 300, 75)

    running = True
    while running:
        pygame.time.wait(100)
        start_action = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                #TODO - fixme
                print("============== START")
                start_action = start

        #TODO - improve...
        button("PLAY!", 150, 450, 100, 50, white, white, start_action)
        button("PLAY", 152, 452, 96, 46, black, black, None)
        button("QUIT!", 450, 450, 100, 50, white, white, quit)
        button("QUIT", 452, 452, 96, 46, black, black, quit)
        pygame.display.update()

