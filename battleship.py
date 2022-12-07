#This class plays battleship
import random
from ulab import numpy as np


class battleship:

    def __init__(self):
        self.board = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]] #change to 1 for hit -1 for miss
        self.shots = 0
        self.state = 0 #0 for searching, 1 for sinking
        self.shot_set = set()
        self.last_shot = [0,0]
        self.first_hit = [-1,-1]
        self.last_hit = [-1,-1]

    def hit(self):
        self.board[self.last_shot[0]][self.last_shot[1]] = 1
        if self.last_hit == [-1,-1]:
            self.first_hit = self.last_shot
        self.last_hit = self.last_shot
        self.state = 1

    def miss(self):
        self.board[self.last_shot[0]][self.last_shot[1]] = -1

    def sink(self):
        self.board[self.last_shot[0]][self.last_shot[1]] = 1
        self.last_hit = self.last_shot
        self.state = 0
    
    def whiff(self):
        self.shot_set.remove(self.last_shot)

    def calc_shot_rand(self):
        #increment shot counter
        self.shots += 1

        #generate random value pairs until the pair isn't in the set of shots that have been done so far
        while True:
                pick = random.randint(0,7)
                options = [[0,0],[0,2],[1,1],[1,3],[2,0],[2,2],[3,1],[3,3]]
                #print('generating rando shot, option ' + str(pick) + ' set ')
                #print(self.shot_set)
                if tuple(options[pick]) not in self.shot_set:
                    self.shot_set.add(tuple(options[pick]))
                    self.shots += 1
                    return options[pick]

    def calc_shot_twostate(self):
        #if we hit the last shot, switch to search mode
        #random search state
        if self.state == 0:
            while True:
                pick = random.randint(0,7)
                options = [[0,0],[0,2],[1,1],[1,3],[2,0],[2,2],[3,1],[3,3]]
                if tuple(options[pick]) not in self.shot_set:
                    self.shot_set.add(tuple(options[pick]))
                    self.shots += 1
                    self.last_shot = options[pick]
                    return options[pick]

        #sinking state
        if self.state == 1:
            #lay out options
            i = self.last_hit[0]
            j = self.last_hit[1]
            print('Searching the area around ' + str(i) + ',' + str(j))
            print()

            options = [[i-1,j],[i+1,j],[i,j-1],[i,j+1]]
            #searching for the next part of the boat
            if 0 <= i-1 <= 3 and self.board[options[0][0]][options[0][1]] == 0:
                if (i-1,j) not in self.shot_set:
                    print('Opt a')
                    print('Hit: ' + str(self.board[options[0][0]][options[0][1]]))
                    self.shot_set.add(tuple(options[0]))
                    self.last_shot = options[0]
                    return options[0]
            elif 0 <= i+1 <= 3 and self.board[options[1][0]][options[1][1]] == 0:
                if (i+1,j) not in self.shot_set:
                    self.last_shot = options[1]
                    self.shot_set.add(tuple(options[1]))
                    print('Opt b')
                    print('Hit: ' + str(self.board[options[1][0]][options[1][1]]))
                    return options[1]
            elif 0 <= j-1 <= 3 and self.board[options[2][0]][options[2][1]] == 0:
                if (i,j-1) not in self.shot_set:
                    self.last_shot = options[2]
                    self.shot_set.add(tuple(options[2]))
                    print('Opt c')
                    print('Hit: ' + str(self.board[options[2][0]][options[2][1]]))
                    return options[2]
            elif 0 <= j+1 <= 3 and self.board[options[3][0]][options[3][1]] == 0:
                if (i,j+1) not in self.shot_set:
                    self.last_shot = options[3]
                    self.shot_set.add(tuple(options[3]))
                    print('Opt d')
                    print('Hit: ' + str(self.board[options[3][0]][options[3][1]]))
                    return options[3]
            
            print('No acceptable coordinates found. Returning search to first hit on this ship.')

            i = self.first_hit[0]
            j = self.first_hit[1]
            print('Searching the area around ' + str(i) + ',' + str(j))
            print()
            options = [[i-1,j],[i+1,j],[i,j-1],[i,j+1]]
            #handling if we get started the sink from the middle of the boat
            if 0 <= i-1 <= 3 and self.board[options[0][0]][options[0][1]] == 0:
                if (i-1,j) not in self.shot_set:
                    print('Opt a')
                    print('Hit: ' + str(self.board[options[0][0]][options[0][1]]))
                    self.last_shot = options[0]
                    return options[0]
            elif 0 <= i+1 <= 3 and self.board[options[1][0]][options[1][1]] == 0:
                if (i+1,j) not in self.shot_set:
                    self.last_shot = options[1]
                    print('Opt b')
                    print('Hit: ' + str(self.board[options[1][0]][options[1][1]]))
                    return options[1]
            elif 0 <= j-1 <= 3 and self.board[options[2][0]][options[2][1]] == 0:
                if (i,j-1) not in self.shot_set:
                    self.last_shot = options[2]
                    print('Opt c')
                    print('Hit: ' + str(self.board[options[2][0]][options[2][1]]))
                    return options[2]
            elif 0 <= j+1 <= 3 and self.board[options[3][0]][options[3][1]] == 0:
                if (i,j+1) not in self.shot_set:
                    self.last_shot = options[3]
                    print('Opt d')
                    print('Hit: ' + str(self.board[options[3][0]][options[3][1]]))
            else:
                raise Exception('Impossible board state')