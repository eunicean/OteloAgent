import random
from copy import deepcopy

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
# DATA IMPORTANTE
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

# patrones comunes de apertura y mejores respuestas para el segundo jugador
OPENING_BOOK = {
    ((3, 3), (4, 4)): [(2, 4), (4, 2), (5, 3), (3, 5)],
    ((3, 4), (4, 3)): [(2, 3), (3, 2), (4, 5), (5, 4)],
    ((3, 3), (3, 4)): [(2, 2), (2, 4), (4, 2), (4, 5)],
}

# esquinas
CORNERS = [(0,0), (0,7), (7,0), (7,7)]

# evaluar el tablero considerando en que fase del juego estoy, dando una calificacion
def evaluate_board(board, player, phase):
    opponent = -player
    score = 0
    
    # valor posicional
    positional = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                positional += POSITION_WEIGHTS[x][y]
            elif board[x][y] == opponent:
                positional -= POSITION_WEIGHTS[x][y]
    
    # numero de movimientos posibles
    mobility = len(valid_movements(board, player)) - len(valid_movements(board, opponent))
    
    # control de esquinas, quien tiene ventajas sobre las esquinas
    corner_control = 0
    for (x, y) in CORNERS:
        if board[x][y] == player:
            corner_control += 25
        elif board[x][y] == opponent:
            corner_control -= 25
    
    # diferencia de fichas
    piece_diff = sum(1 for row in board for cell in row if cell == player) - \
                 sum(1 for row in board for cell in row if cell == opponent)
    
    if phase == 'opening':  # 0-20 fichas fase importante
        score = 10 * positional + 100 * mobility + 50 * corner_control
    elif phase == 'midgame':  # 20-50 fichas
        score = 5 * positional + 50 * mobility + 30 * corner_control + 5 * piece_diff
    else:  # endgame 50+ fichas
        score = positional + 10 * mobility + 20 * corner_control + 100 * piece_diff
    
    return score

# simula un movimiento y devuelve el nuevo tablero
def simulate_move(board, move, player):
    new_board = deepcopy(board)
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

    return new_board

# obtener la fase del juego en la que estoy actualmente
def get_game_phase(board):
    total_pieces = sum(abs(board[x][y]) for x in range(8) for y in range(8))
    if total_pieces < 20:
        return 'opening'
    elif total_pieces < 50:
        return 'midgame'
    else:
        return 'endgame'

def ai_move(board, player):
    valid_moves = valid_movements(board, player)
    if not valid_moves:
        return None
    
    # verificar libro de aperturas cuando el agente tiene primer turno
    if player == 1 and sum(abs(cell) for row in board for cell in row) <= 4:
        for pattern, moves in OPENING_BOOK.items():
            if all(board[x][y] == 1 for (x, y) in pattern):
                available = [m for m in moves if m in valid_moves]
                if available:
                    return random.choice(available)
    
    # elegir esquinas siempre que sea un movimiento valido
    available_corners = [c for c in CORNERS if c in valid_moves]
    if available_corners:
        return random.choice(available_corners)
    
    # determinar fase del juego
    phase = get_game_phase(board)
    
    # si soy jugador blanco y es fase inicial, estrategia más defensiva
    if player == -1 and phase == 'opening':
        # evitar casillas peligrosas cerca de esquinas para no regalar puntos
        danger_zones = [(0,1), (1,0), (1,1), (0,6), (1,6), (1,7), (6,0), (6,1), (7,1), (6,6), (6,7), (7,6)]
        safe_moves = [m for m in valid_moves if m not in danger_zones]
        if safe_moves:
            valid_moves = safe_moves # intercambiar mov validos por los seguros
    
    # búsqueda de mi movimiento + mejor respuesta del oponente
    best_score = -float('inf')
    best_moves = []
    
    for move in valid_moves:
        # simular mi movimiento
        new_board = simulate_move(board, move, player)
        
        # simular la mejor respuesta del oponente
        opponent_moves = valid_movements(new_board, -player)
        if opponent_moves:
            # encontrar mi peor caso, mejor movimiento del oponente
            worst_case = float('inf')
            for opp_move in opponent_moves:
                opp_board = simulate_move(new_board, opp_move, -player)
                score = evaluate_board(opp_board, player, phase)
                if score < worst_case:
                    worst_case = score
            current_score = worst_case
        else:
            current_score = evaluate_board(new_board, player, phase)
        
        # actualizar mejores movimientos
        if current_score > best_score:
            best_score = current_score
            best_moves = [move]
        elif current_score == best_score:
            best_moves.append(move) # si dos movimientos son igual de buenos
    
    # si no hay mejor movimiento
    if not best_moves or (player == -1 and phase == 'opening' and len(best_moves) > 1):
        min_flips = float('inf')
        conservative_moves = []
        for move in valid_moves:
            flips = sum(1 for x in simulate_move(deepcopy(board), move, player)) - 1
            if flips < min_flips:
                min_flips = flips
                conservative_moves = [move]
            elif flips == min_flips:
                conservative_moves.append(move)
        return random.choice(conservative_moves)
    
    return random.choice(best_moves)