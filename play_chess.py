import pygame
import chess
import chess.engine

# Initialization
pygame.init()
pygame.display.set_caption('Chess Game')

# Constants
BOARD_WIDTH, TILE_SIZE, LEFT_MARGIN, BOTTOM_MARGIN = 512, 64, 30, 30
WIDTH, HEIGHT = BOARD_WIDTH + LEFT_MARGIN, TILE_SIZE * 8 + BOTTOM_MARGIN
COLORS = [(235, 236, 208), (119, 148, 85)]
STOCKFISH_PATH = r"C:\Users\Andrew\OneDrive\Desktop\Computer Science\Chess\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe"
END_GAME_CONDITIONS = {chess.Board.is_checkmate, chess.Board.is_stalemate, chess.Board.is_insufficient_material}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Load chess pieces
piece_files = {
    'P': 'pawn-w', 'p': 'pawn-b', 'R': 'rook-w', 'r': 'rook-b', 'N': 'knight-w',
    'n': 'knight-b', 'B': 'bishop-w', 'b': 'bishop-b', 'Q': 'queen-w', 'q': 'queen-b',
    'K': 'king-w', 'k': 'king-b'
}
pieces = {symbol: pygame.transform.scale(pygame.image.load(f"pieces/{filename}.png").convert_alpha(), (TILE_SIZE, TILE_SIZE)) for symbol, filename in piece_files.items()}

def get_stockfish_move(board):
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        result = engine.play(board, chess.engine.Limit(time=2.0))
        return result.move

def get_square_from_coords(x, y):
    return (y // TILE_SIZE) * 8 + (x - LEFT_MARGIN) // TILE_SIZE

def draw_board(board, held_piece=None, held_piece_pos=None):
    for row in range(8):
        for col in range(8):
            pygame.draw.rect(screen, COLORS[(row + col) % 2], (LEFT_MARGIN + col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            piece = board.piece_at(8 * row + col)
            if piece and (held_piece is None or (row, col) != divmod(held_piece, 8)):
                screen.blit(pieces[str(piece)], (LEFT_MARGIN + col * TILE_SIZE, row * TILE_SIZE))
    if held_piece:
        screen.blit(pieces[str(board.piece_at(held_piece))], (held_piece_pos[0] - TILE_SIZE // 2, held_piece_pos[1] - TILE_SIZE // 2))
    
    # Clear the left and bottom margins
    pygame.draw.rect(screen, (255, 255, 255), (0, 0, LEFT_MARGIN, HEIGHT))
    pygame.draw.rect(screen, (255, 255, 255), (0, BOARD_WIDTH, WIDTH, BOTTOM_MARGIN))
    
    # Draw rank numbers (1-8) on the left margin
    for i in range(8):
        font = pygame.font.SysFont(None, 24)
        rank_text = font.render(str(8 - i), True, (0, 0, 0))
        screen.blit(rank_text, (10, i * TILE_SIZE + TILE_SIZE // 2 - rank_text.get_height() // 2))
    
    # Draw file letters (a-h) at the bottom
    for i in range(8):
        font = pygame.font.SysFont(None, 24)
        file_text = font.render(chr(97 + i), True, (0, 0, 0))
        screen.blit(file_text, (LEFT_MARGIN + i * TILE_SIZE + TILE_SIZE // 2 - file_text.get_width() // 2, 8 * TILE_SIZE + 5))
    
    pygame.display.flip()

def display_message(message):
    font = pygame.font.SysFont(None, 50)
    text_surface = font.render(message, True, (255, 0, 0))
    screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    pygame.display.flip()

def select_mode():
    while True:
        screen.fill((255, 255, 255))
        font = pygame.font.SysFont(None, 36)
        ai_text = font.render("Play against AI", True, (0, 0, 0))
        human_text = font.render("Play against Human", True, (0, 0, 0))
        ai_rect = ai_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        human_rect = human_text.get_rect(center=(WIDTH // 2, 2 * HEIGHT // 3))
        screen.blit(ai_text, ai_rect)
        screen.blit(human_text, human_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ai_rect.collidepoint(event.pos):
                    return True
                elif human_rect.collidepoint(event.pos):
                    return False

AI_MODE = select_mode()
board = chess.Board()
game_over = False
held_piece = None
held_piece_pos = None

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            board = chess.Board()
            game_over = False
            AI_MODE = select_mode()

        elif not game_over:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                square = get_square_from_coords(x, y)
                piece = board.piece_at(square)
                if piece and (not AI_MODE or (AI_MODE and piece.color == chess.BLACK)):
                    held_piece = square
                    held_piece_pos = event.pos

            elif event.type == pygame.MOUSEMOTION and held_piece is not None:
                held_piece_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and held_piece is not None:
                destination_square = get_square_from_coords(*event.pos)
                move = chess.Move(held_piece, destination_square)
                if move in board.legal_moves:
                    board.push(move)
                    if any(condition(board) for condition in END_GAME_CONDITIONS):
                        game_over = True

                held_piece = None
                held_piece_pos = None

    draw_board(board, held_piece, held_piece_pos)

    if game_over:
        message = "Game Over! Press R to restart."
        if board.is_checkmate():
            message = "Checkmate! Press R to restart."
        elif board.is_stalemate() or board.is_insufficient_material():
            message = "Draw! Press R to restart."
        display_message(message)
        pygame.time.wait(1000)

    elif AI_MODE and board.turn == chess.WHITE:
        ai_move = get_stockfish_move(board)
        if ai_move:
            board.push(ai_move)
            if any(condition(board) for condition in END_GAME_CONDITIONS):
                game_over = True

    clock.tick(60)
