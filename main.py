# from asyncio import subprocess
import subprocess
from cProfile import run
from game_set import *
from queue import Empty,Queue
from time import perf_counter
from threading import Thread, Timer
# from subprocess import check_output, CalledProcessError, TimeoutExpired
from subprocess import TimeoutExpired
import sys
import pygame
import time
import random
import copy
import decimal
import os
import signal
#print(pygame.ver)

# 先去看README，這裡你不用改
# 先去看README，這裡你不用改
# 先去看README，這裡你不用改

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)
score_font = pygame.font.SysFont('Comic Sans MS', 100)
step_font = pygame.font.SysFont('Comic Sans MS', 20)
screen = pygame.display.set_mode((840,640))

 
EMPTY = 0
BLACK = 1
WHITE = 2
 
black_color = [0, 0, 0]

white_color = [255, 255, 255]


# scoreboard
a_team_color = [247, 206, 92]
b_team_color = [247, 206, 92]
losser_color = [202, 203, 207]
winner_color = [110, 250, 95]

# sound
if sound_activate:
    pygame.mixer.init()
    stone_sound = pygame.mixer.Sound('sound/stone_sound1.wav')
    wrong_sound = pygame.mixer.Sound('sound/wrong_sound.wav')

# history board
history_board = [0] * 6
 

class RenjuBoard(object):
 
    def __init__(self):
        # self._board = board = [[EMPTY] * 15 for _ in range(15)]
        # board 15*15
        self._board = [[]] * 15
        self.team_score = [0] * 2
        self.team_name = ["team"] * 2
        self.team_step = [0] * 2
        self.remain_time = [0] * 2
        self.one_step = [0] * 2
        self.black_team = 0
        self.reset(0)

    def reset(self, numStone):
        self.one_step[0] = 0
        self.one_step[1] = 0
        for row in range(len(self._board)):
            self._board[row] = [EMPTY] * 15
        for i in range(numStone):
            r, c = random.randint(3, 15-4), random.randint(3, 15-4)
            while not self.move(r, c, i%2 == 0):
                r, c = random.randint(3, 15-4), random.randint(3, 15-4)
        self.remain_time[0] = 80
        self.remain_time[1] = 80

    def reset_to(self, board):
        self.one_step[0] = 0
        self.one_step[1] = 0
        self._board = board
        self.remain_time[0] = 80
        self.remain_time[1] = 80
        

    def switch(self):
        self.black_team = not self.black_team

    def isValid(self, row, col):
        if row < 0 or row >= 15:
            return False
        if col < 0 or col >= 15:
            return False
        return self._board[row][col] is EMPTY

    def move(self, row, col, is_black):
        if self.isValid(row, col):
            self._board[row][col] = BLACK if is_black else WHITE
            return True
        if sound_activate:
            pygame.mixer.music.stop()
            pygame.mixer.Sound.play(wrong_sound)
        return False

    def gain_point(self, win_team):
        if win_team == BLACK:
            self.team_score[self.black_team] += 1
            self.team_step[self.black_team] += self.one_step[self.black_team]
        else:
            self.team_score[not self.black_team] += 1
            self.team_step[not self.black_team] += self.one_step[not self.black_team]

    def draw(self, screen, winner, now_turn):
        for h in range(1, 16):
            pygame.draw.line(screen, black_color,
                             [40, h * 40], [600, h * 40], 1)
            pygame.draw.line(screen, black_color,
                             [h * 40,40], [h * 40, 600], 1)
        pygame.draw.rect(screen, black_color, [36, 36, 568, 568], 3)
 
        pygame.draw.circle(screen, black_color, [320, 320], 5, 0)
        pygame.draw.circle(screen, black_color, [160, 160], 3, 0)
        pygame.draw.circle(screen, black_color, [160, 480], 3, 0)
        pygame.draw.circle(screen, black_color, [480, 160], 3, 0)
        pygame.draw.circle(screen, black_color, [480, 480], 3, 0)
        for row in range(len(self._board)):
            for col in range(len(self._board[row])):
                if self._board[row][col] != EMPTY:
                    ccolor = black_color \
                        if self._board[row][col] == BLACK else white_color
                    pos = [40 * (col + 1), 40 * (row + 1)]
                    pygame.draw.circle(screen, ccolor, pos, 18, 0)
        # draw scoreboard
        if winner == 0:
            recta_filled = pygame.Rect(630, 20, 180, 180)
            pygame.draw.rect(screen, a_team_color, recta_filled) 
            rectb_filled = pygame.Rect(630, 420, 180, 180)
            pygame.draw.rect(screen, b_team_color, rectb_filled)
        elif winner == 1:
            recta_filled = pygame.Rect(630, 20, 180, 180)
            pygame.draw.rect(screen, winner_color, recta_filled) 
            rectb_filled = pygame.Rect(630, 420, 180, 180)
            pygame.draw.rect(screen, losser_color, rectb_filled)
        elif winner == 2:
            recta_filled = pygame.Rect(630, 20, 180, 180)
            pygame.draw.rect(screen, losser_color, recta_filled) 
            rectb_filled = pygame.Rect(630, 420, 180, 180)
            pygame.draw.rect(screen, winner_color, rectb_filled)        

        text_a_name = my_font.render(self.team_name[0], False, (0, 0, 0))
        screen.blit(text_a_name, (620,210))
        text_a_score = score_font.render(str(self.team_score[0]), False, (0, 0, 0))
        screen.blit(text_a_score, (680,50))
        text_b_name = my_font.render(self.team_name[1], False, (0, 0, 0))
        screen.blit(text_b_name, (620,370))
        text_b_score = score_font.render(str(self.team_score[1]), False, (0, 0, 0))
        screen.blit(text_b_score, (680,460))

        #team_a chess
        ccolor = black_color \
            if self.black_team == 0 else white_color
        pygame.draw.circle(screen, ccolor, [780,230], 25, 0)
        #team_b chess
        ccolor = black_color \
            if self.black_team == 1 else white_color
        pygame.draw.circle(screen, ccolor, [780,390], 25, 0)
        #team_a step info
        text_a_score = step_font.render("Win Step:"+str(self.team_step[0]), False, (0, 0, 0))
        screen.blit(text_a_score, (680,20))
        #team_b step info
        text_b_score = step_font.render("Win Step:"+str(self.team_step[1]), False, (0, 0, 0))
        screen.blit(text_b_score, (680,420))

        #team_a score info
        text_a_score = step_font.render("Score:"+str(678-self.team_step[0]-self.team_score[1]*113), False, (0, 0, 0))
        screen.blit(text_a_score, (680,40))
        #team_b score info
        text_b_score = step_font.render("Score:"+str(678-self.team_step[1]-self.team_score[0]*113), False, (0, 0, 0))
        screen.blit(text_b_score, (680,440))

        #show present team 780 230
        if (self.black_team == 0 and now_turn == True) or (self.black_team == 1 and now_turn == False):
            pygame.draw.circle(screen, [255,0,0], [780,230], 10, 0)
        else:
            pygame.draw.circle(screen, [255,0,0], [780,390], 10, 0)

    def draw_now(self, row, col):
        pygame.draw.circle(screen, [255,0,0], [40 * (col + 1), 40 * (row + 1)], 10, 0)


def UI_win(winner):
    if winner is BLACK:
        text_surface = my_font.render('Black Win', False, (255, 255, 255),(0, 0, 0))
        screen.blit(text_surface, (655,300))
        pygame.display.flip()
        print('黑棋勝')
    elif winner is WHITE:
        text_surface = my_font.render('White Win', False, (0, 0, 0),(255, 255, 255))
        screen.blit(text_surface, (655,300))
        pygame.display.flip()
        print('白棋勝')
 

def is_win(board):
    for n in range(15):

        flag = 0

        for b in board._board:
            if b[n] == 1:
                flag += 1
                if flag == 5:
                    return BLACK
            else:
                flag = 0
 
        flag = 0
        for b in board._board:
            if b[n] == 2:
                flag += 1
                if flag == 5:
                    return WHITE
            else:
                flag = 0
 
        flag = 0
        for b in board._board[n]:
            if b == 1:
                flag += 1
                if flag == 5:
                    return BLACK
            else:
                flag = 0
 
        flag = 0
        for b in board._board[n]:
            if b == 2:
                flag += 1
                if flag == 5:
                    return WHITE
            else:
                flag = 0
 
        for x in range(4, 25):
            flag = 0
            for i,b in enumerate(board._board):
                if 14 >= x - i >= 0 and b[x - i] == 1:
                    flag += 1
                    if flag == 5:
                        return BLACK
                else:
                    flag = 0
 
        for x in range(4, 25):
            flag = 0
            for i,b in enumerate(board._board):
                if 14 >= x - i >= 0 and b[x - i] == 2:
                    flag += 1
                    if flag == 5:
                        return WHITE
                else:
                    flag = 0
 
        for x in range(11, -11, -1):
            flag = 0
            for i,b in enumerate(board._board):
                if 0 <= x + i <= 14 and b[x + i] == 1:
                    flag += 1
                    if flag == 5:
                        return BLACK
                else:
                    flag = 0
 
        for x in range(11, -11, -1):
            flag = 0
            for i,b in enumerate(board._board):
                if 0 <= x + i <= 14 and b[x + i] == 2:
                    flag += 1
                    if flag == 5:
                        return WHITE
                else:
                    flag = 0
    for i in range(15):
        for j in range(15):
            if board._board[i][j] == EMPTY:
                return EMPTY
    return WHITE

def timer(stop, remainTime,list,board,is_black,process):
    # print('timer reset')
    # sleep_duration = remainTime
    
    while remainTime > 0 and stop() == False:
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
        '''
        # print(f"you have {remainTime} seconds left")
        time.sleep(1/10)
        remainTime -= 0.1
        text_time = my_font.render(str(format(remainTime, '.1f')), False, (0, 0, 0))
        screen.fill([230, 169, 37])
        board.draw(screen,EMPTY,is_black)
        screen.blit(text_time, (655,300))
        pygame.display.flip()
    if remainTime <= 0:
        process.terminate()
    # print("timer completed")
    list.append( remainTime)

def main():
    team_a_name = team_a_path[team_a_path.rfind('/')+1:team_a_path.rfind('.')]
    team_b_name = team_b_path[team_b_path.rfind('/')+1:team_b_path.rfind('.')]
    if mode == 2:
        print("測試模式說明：")
        print("每一步棋皆等待玩家操作，若按下空白鍵，則由程式下出下一手，若用滑鼠點按則可直接下下一手棋。")

    board = RenjuBoard()
    board.team_name[0] = team_a_name
    board.team_name[1] = team_b_name

    # step count

    pygame.init()
    pygame.display.set_caption('GoBang')

    screen.fill([230, 169, 37])
    board.draw(screen,EMPTY,True) 
    pygame.display.flip()

    total_set = 1
    if(mode == 3):
        total_set = 4

    set_count = 0
   
    if mode == 1 or mode == 3:
        while set_count < total_set:  
            running = True
            is_black = False
            if set_count % 2 == 0:
                board.reset( 2 * (set_count//2) )
                prevInit = copy.deepcopy(board._board)
            else:
                board.reset_to(prevInit)
            board.switch()
            
            screen.fill([230, 169, 37])
            board.draw(screen,EMPTY,is_black)
            pygame.display.flip()
            pygame.time.delay(2000)
            
            while running:
                stop_threads = False
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        stop_threads = True
                        pygame.quit()
                        return None
                
                is_black = not is_black
                screen.fill([230, 169, 37])
                board.draw(screen,EMPTY,is_black)
                pygame.display.flip()

                color = BLACK if is_black else WHITE
                team_idx = board.black_team if is_black else not board.black_team
                team_path = team_a_path if team_idx == 0 else team_b_path

                start = perf_counter()

                que = Queue()
                my_list = []
                
                try:
                    # result = check_output(f'python {sys.path[0]}/{team_path}', shell=True, input= str(str(board._board)+', '+str(color)),encoding='ascii',timeout=3).split()
                    process = subprocess.Popen(f'python {sys.path[0]}/{team_path}', shell=True,encoding='utf8',stdin= subprocess.PIPE, stdout=subprocess.PIPE)
                    
                    timer_thread = Thread(target=timer,args =(lambda : stop_threads,board.remain_time[team_idx],my_list,board,is_black,process ))
                    timer_thread.start()
                    result = process.communicate(input=str(str(board._board)+', '+str(color)+', '+str(board.remain_time[team_idx])),timeout=board.remain_time[team_idx])[0].split()
                    if len(result) == 0:
                        stop_threads = True
                        running = False
                    else:
                        stop_threads = True
                        [row, col] = [int(num) for num in result]
                except TimeoutExpired:
                    print('TIME LIMIT EXCEEDED(超時)')
                    stop_threads = True
                    running = False
                except Exception as err:
                    print(err)
                    pygame.quit()
                    exit()
                stop_threads = True
                timer_thread.join()
                board.remain_time[team_idx] = my_list[0]
                # result = que.get()
                # print('remain:',result)
                
                if running and board.move(row, col, is_black):
                    board.one_step[team_idx] += 1
                else:
                    status = 3-color
                    running = False
                end = perf_counter()

                screen.fill([230, 169, 37])
                board.draw(screen,EMPTY,is_black)
                if running:
                    if sound_activate:
                        pygame.mixer.music.stop()
                        pygame.mixer.Sound.play(stone_sound)
                    board.draw_now(row,col)
                pygame.display.flip()

                real_delay = int(time_delay-(end-start)*1000)
                if real_delay < 0: real_delay = 0
                pygame.time.wait(200+real_delay)

                if running:
                    status = is_win(board)
                if status > 0:
                    screen.fill([230, 169, 37])
                    board.gain_point(status)
                    UI_win(status)
                    board.draw(screen,EMPTY,is_black)
                    board.draw_now(row,col)
                    pygame.display.flip()
                    
                    running = False
            set_count += 1
            if mode == 3 and total_set == 4 and set_count == total_set and board.team_score[0] == board.team_score[1] and board.team_step[0] == board.team_step[1]:
                total_set += 2
            if set_count != total_set:
                pygame.time.delay(set_delay)

    elif mode == 2:
        running = True
        is_black = True
        board.reset(0)
        while running:
            for event in pygame.event.get():
                row, col = -1, -1
                color = BLACK if is_black else WHITE
                team_idx = board.black_team if is_black else not board.black_team

                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    team_path = team_a_path if is_black else team_b_path
                    start = perf_counter()

                    stop_threads = False
                    que = Queue()
                    my_list = []
                    try:
                        # result = check_output(f'python {sys.path[0]}/{team_path}', shell=True, input= str(str(board._board)+', '+str(color)),encoding='ascii',timeout=3).split()
                        process = subprocess.Popen(f'python {sys.path[0]}/{team_path}', shell=True,encoding='utf8',stdin= subprocess.PIPE, stdout=subprocess.PIPE)
                        
                        timer_thread = Thread(target=timer,args =(lambda : stop_threads,board.remain_time[team_idx],my_list,board,is_black,process ))
                        timer_thread.start()
                        result = process.communicate(input=str(str(board._board)+', '+str(color)+', '+str(board.remain_time[team_idx])),timeout=board.remain_time[team_idx])[0].split()
                        if len(result) == 0:
                            stop_threads = True
                            running = False
                        else:
                            stop_threads = True
                            [row, col] = [int(num) for num in result]
                    except TimeoutExpired:
                        print('TIME LIMIT EXCEEDED(超時)')
                        stop_threads = True
                        running = False
                    except Exception as err:
                        print(err)
                        pygame.quit()
                        exit()
                    stop_threads = True
                    timer_thread.join()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    row = round((y - 40) / 40)
                    col = round((x - 40) / 40)
                else:
                    continue
                
                if running and board.move(row, col, is_black):
                    board.one_step[0 if is_black else 1] += 1
                else:
                    print(f'Invalid index: {row}, {col}')
                    status = 3-color
                    running = False
                
                screen.fill([230, 169, 37])
                board.draw(screen,EMPTY,is_black)
                pygame.display.flip()
                if running:
                    status = is_win(board)
                if status > 0:
                    UI_win(status)
                    pygame.time.delay(set_delay)
                    board.gain_point(status)
                    running = False
                is_black = not is_black

    screen.fill([230, 169, 37])
    board.draw(screen,EMPTY,is_black)
    pygame.display.flip()

    if(board.team_score[0] > board.team_score[1]):
        board.draw(screen,1,is_black)
    elif(board.team_score[0] < board.team_score[1]):
        board.draw(screen,2,is_black)
    elif(board.team_step[0] < board.team_step[1]):
        board.draw(screen,1,is_black)
    elif(board.team_step[0] > board.team_step[1]):
        board.draw(screen,2,is_black)
    else:
        board.draw(screen,0,is_black)
    pygame.display.flip()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()

if __name__ == '__main__':
    main()
