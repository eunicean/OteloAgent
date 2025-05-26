import random

DIRECTIONS = [
    (-1, -1),  # UP-LEFT
    (-1, 0),   # UP
    (-1, 1),   # UP-RIGHT
    (0, -1),   # LEFT
    (0, 1),    # RIGHT
    (1, -1),   # DOWN-LEFT
    (1, 0),    # DOWN
    (1, 1)     # DOWN-RIGHT
]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def valid_movements(board, player):
    opponent = -player
    valid_moves = []

    for x in range(8):
        for y in range(8):
            if board[x][y] != 0:
                continue

            for dx, dy in DIRECTIONS:
                i, j = x + dx, y + dy
                found_opponent = False

                while in_bounds(i, j) and board[i][j] == opponent:
                    i += dx
                    j += dy
                    found_opponent = True

                if found_opponent and in_bounds(i, j) and board[i][j] == player:
                    valid_moves.append((x, y))
                    break

    return valid_moves

# MIS MODIFICACIONES
# Tabla de valores posicionales
POSITION_WEIGHTS = [
    [500, -150, 30, 10, 10, 30, -150, 500],
    [-150, -250, 0, 0, 0, 0, -250, -150],
    [30, 0, 1, 2, 2, 1, 0, 30],
    [10, 0, 2, 16, 16, 2, 0, 10],
    [10, 0, 2, 16, 16, 2, 0, 10],
    [30, 0, 1, 2, 2, 1, 0, 30],
    [-150, -250, 0, 0, 0, 0, -250, -150],
    [500, -150, 30, 10, 10, 30, -150, 500]
]


def evaluate_board(board, player):
    # evalúa la posición del tablero desde la perspectiva del jugador dado 
    opponent = -player
    score = 0
    
    # 1. Valor posicional
    positional = 0
    # 2. Diferencial de fichas
    pieces = 0
    # 3. Movilidad
    mobility = len(valid_movements(board, player)) - len(valid_movements(board, opponent))
    
    # contar las fichas y calcular valor posicional
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                positional += POSICION_PESOS[x][y]
                pieces += 1
            elif board[x][y] == opponent:
                positional -= POSICION_PESOS[x][y]
                pieces -= 1
    
    total_pieces = sum(abs(board[x][y]) for x in range(8) for y in range(8))
    
    if total_pieces < 20:  # fase inicial
        score = 10 * positional + 100 * mobility
    elif total_pieces < 50:  # media
        score = 5 * positional + 50 * mobility + 10 * pieces
    else:  # final
        score = positional + 10 * mobility + 50 * pieces
    
    return score

def ai_move(board, player):
    valid_moves = valid_movements(board, player)
    if not valid_moves:
        return None
    
    # elección rapida con pocas opciones
    if len(valid_moves) <= 3:
        return random.choice(valid_moves)
    
    # buscar esquinas disponibles
    corners = [(0,0), (0,7), (7,0), (7,7)]
    for move in valid_moves:
        if move in corners:
            return move
    
    best_score = -float('inf')
    best_moves = []
    
    for move in valid_moves:
        new_board = [row[:] for row in board]
        x, y = move
        new_board[x][y] = player
        opponent = -player
        
        for dx, dy in DIRECTIONS:
            i, j = x + dx, y + dy
            to_flip = []
            
            while in_bounds(i, j) and new_board[i][j] == opponent:
                to_flip.append((i, j))
                i += dx
                j += dy
            
            if in_bounds(i, j) and new_board[i][j] == player:
                for (i, j) in to_flip:
                    new_board[i][j] = player
        
        # evaluando el tablero resultante
        score = evaluate_board(new_board, player)
        
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)
    
    return random.choice(best_moves)