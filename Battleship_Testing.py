import battleship

algo = battleship.battleship()


while True:
    print()
    shot = algo.calc_shot_twostate()
    print(algo.board[0])
    print(algo.board[1])
    print(algo.board[2])
    print(algo.board[3])
    print()
    print('Row: ' + str(shot[0]+1) + 'Col: ' + str(shot[1]+1))
    input1 = input('Did I hit?')

    if input1 == 'y':
        algo.hit()
    elif input1 == 'n':
        algo.miss()
    elif input1 == 's':
        algo.sink()
    else:
        print('bad input foo')

    #print('\033c')