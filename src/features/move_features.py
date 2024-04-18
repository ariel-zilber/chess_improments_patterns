import math
import chess
import chess.engine
import numpy as np


class ExtractMoveFeatures:
    def __init__(self,engine):
        self.engine=engine
        pass

    def extract(self,moves_df):
        moves=self.get_moves(moves_df)

        return {
            "total_moves_white":math.ceil(len(moves)/2),
            "total_moves_black":math.floor(len(moves)/2),
            "moves_before_casting_white":self.count_moves_before_castling(moves,True),
            "moves_before_casting_black":self.count_moves_before_castling(moves,False),
            "count_minor_pieces_defending_center_white":self.count_minor_pieces_defending_center(moves,True),
            "count_minor_pieces_defending_center_black":self.count_minor_pieces_defending_center(moves,False),
            "count_unique_pieces_moved_white":self.count_unique_pieces_moved(moves,True),
            "count_unique_pieces_moved_black":self.count_unique_pieces_moved(moves,False),
            "first_rook_to_seventh_white":self.first_rook_to_seventh(moves,True),
            "first_rook_to_seventh_black":self.first_rook_to_seventh(moves,False),
            "count_white_minor_pieces_center_attack_defense_white":self.count_white_minor_pieces_center_attack_defense(moves,True),
            "count_white_minor_pieces_center_attack_defense_black":self.count_white_minor_pieces_center_attack_defense(moves,False),
            "check_minor_before_major_development_white":self.check_minor_before_major_development(moves,True),
            "check_minor_before_major_development_black":self.check_minor_before_major_development(moves,False),
            "count_knight_edge_moves_white":self.count_knight_edge_moves(moves,True),
            "count_knight_edge_moves_black":self.count_knight_edge_moves(moves,False),
            "count_isolated_pawns_25_white":self.count_isolated_pawns(moves,True,0.25),
            "count_isolated_pawns_50_white":self.count_isolated_pawns(moves,True,0.5),
            "count_isolated_pawns_75_white":self.count_isolated_pawns(moves,True,0.75),
            "count_isolated_pawns_100_white":self.count_isolated_pawns(moves,True,0.1),
            "count_isolated_pawns_25_black":self.count_isolated_pawns(moves,False,0.25),
            "count_isolated_pawns_50_black":self.count_isolated_pawns(moves,False,0.5),
            "count_isolated_pawns_75_black":self.count_isolated_pawns(moves,False,0.75),
            "count_isolated_pawns_100_black":self.count_isolated_pawns(moves,False,0.1),
            "count_double_pawns_25_white":self.count_doubled_pawns(moves,True,0.25),
            "count_double_pawns_50_white":self.count_doubled_pawns(moves,True,0.5),
            "count_double_pawns_75_white":self.count_doubled_pawns(moves,True,0.75),
            "count_double_pawns_100_white":self.count_doubled_pawns(moves,True,0.1),
            "count_double_pawns_25_black":self.count_doubled_pawns(moves,False,0.25),
            "count_double_pawns_50_black":self.count_doubled_pawns(moves,False,0.5),
            "count_double_pawns_75_black":self.count_doubled_pawns(moves,False,0.75),
            "count_double_pawns_100_black":self.count_doubled_pawns(moves,False,0.1),
            "count_triple_pawns_25_white":self.count_triple_pawns(moves,True,0.25),
            "count_triple_pawns_50_white":self.count_triple_pawns(moves,True,0.5),
            "count_triple_pawns_75_white":self.count_triple_pawns(moves,True,0.75),
            "count_triple_pawns_100_white":self.count_triple_pawns(moves,True,0.1),
            "count_triple_pawns_25_black":self.count_triple_pawns(moves,False,0.25),
            "count_triple_pawns_50_black":self.count_triple_pawns(moves,False,0.5),
            "count_triple_pawns_75_black":self.count_triple_pawns(moves,False,0.75),
            "count_triple_pawns_100_black":self.count_triple_pawns(moves,False,0.1),
        }

    def get_moves(self,moves_str):
        moves=moves_str.split("|")
        result=[]

        for m in moves:
            if len(m)==0:
                continue
            if "{" in m:
                m=m[:m.index("{")]
            
            for move_code in [x for x in m.split(" ") if len(x)>0]:
                result.append(move_code)

        return result

    def san_to_Move(self,san_move):
        return chess.Board().parse_san(san_move)

    def extract_board_score_diff(self,moves):
        board = chess.Board()
        score_diff=[]
        for move in moves:
            info_before = self.engine.analyse(board, chess.engine.Limit(time=0.01))
            board.push_san(move)
            info_after = self.engine.analyse(board, chess.engine.Limit(time=0.01))
            
            score_before = info_before['score'].relative.score(mate_score=10000)
            score_after = info_after['score'].relative.score(mate_score=10000)
            score_diff.append(score_after-score_before)
        return score_diff


    def count_mistakes(self,score_diff_list,white):
        if white:
            m=0
        else:
            m=1

        return len([score_diff_list[i] for i in range(len(score_diff_list)) if score_diff_list[i]>=100 \
                    and score_diff_list[i]<300 \
                        and i%2 ==m])

    def count_blunders(self,score_diff_list,white):
        if white:
            m=0
        else:
            m=1

        return len([score_diff_list[i] for i in range(len(score_diff_list)) if score_diff_list[i]>=300  and i%2 ==m])

    def first_mistake(self,score_diff_list,white):
        if white:
            for i in range(len(score_diff_list)):
                if score_diff_list[i]>=100 and score_diff_list[i]<=300  and i%2 ==0:
                    return math.floor(i/2) 
            moves_count=len(score_diff_list)
            return math.floor((moves_count-1)/2) 
        else:
            for i in range(len(score_diff_list)):
                if score_diff_list[i]>=100 and score_diff_list[i]<=300 and i%2 ==0:
                    return math.ceil(i/2) 

            moves_count=len(score_diff_list)
            return math.ceil((moves_count-1)/2) 

    def first_blunder(self,score_diff_list,white):
        if white:
            for i in range(len(score_diff_list)):
                if int(score_diff_list[i])>=300  and i%2 ==0:
                    return math.floor(i/2) 
                
            moves_count=len(score_diff_list)
            return math.floor((moves_count-1)/2) 
        else:
            for i in range(len(score_diff_list)):
                if int(score_diff_list[i])>=300  and i%2 ==0:
                    return math.ceil(i/2) 
            moves_count=len(score_diff_list)
            return math.ceil((moves_count-1)/2) 

    def count_moves_before_castling(self,moves,white):
        board = chess.Board()
        move_count = 0
        if white:
            color=chess.WHITE
        else:
            color=chess.BLACK

        for move in moves:
            # Increment move count only on White's moves
            if board.turn == color:
                move_count += 1

            if board.turn != color and board.is_castling(board.parse_san(move)):
                return move_count

            board.push_san(move)

        return move_count


    def count_minor_pieces_defending_center(self,moves,white):
        

        # Get the board after the first 5 moves (10 plies)
        board = chess.Board()
        try:
            for i in range(10):  # Two plies per move
                move=moves[i]
                board.push_san(move)
        except Exception as err:
            return np.nan

        # Define the central squares
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]

        # Initialize count of White's knights and bishops defending or attacking the center
        white_minor_piece_count = 0

        # Check pieces attacking or defending the center squares
        for square in center_squares:
            if white:
                attackers = board.attackers(chess.WHITE, square)
            else:
                attackers = board.attackers(chess.BLACK, square)
            for piece_square in attackers:
                piece = board.piece_at(piece_square)
                if piece.piece_type in (chess.KNIGHT, chess.BISHOP):
                    white_minor_piece_count += 1

        return white_minor_piece_count

    def count_unique_pieces_moved(self,moves,white):
        board = chess.Board()

        # To keep track of the unique pieces that have moved
        pieces_moved = set()

        # # Process only the first 10 moves (20 plies)
        # print(moves)
        for i, move in enumerate(moves):
            if i >= 20:
                break

            # After each White move, check the piece moved
            if white:
                cond=(i%2==0)
            else:
                cond=(i%2==1)

            if cond:  # White moves are even indices (0, 2, 4, ...)
                moved_piece = board.piece_at(board.parse_san(move).to_square)
                if moved_piece:
                    # Use the piece type and color to identify unique pieces
                    pieces_moved.add((moved_piece.piece_type, moved_piece.color))
            board.push_san(move)

        # Filter out only White's unique pieces
        white_unique_pieces_count = sum(1 for piece in pieces_moved if piece[1] == chess.WHITE)
        black_unique_pieces_count = sum(1 for piece in pieces_moved if piece[1] == chess.BLACK)
        if white:
            return white_unique_pieces_count
        else:
            return black_unique_pieces_count


    def first_rook_to_seventh(self,moves,white):
        board = chess.Board()

        for i, move in enumerate(moves):
            if white:
                if board.turn == chess.BLACK:  # Check the position after White's move
                    piece = board.piece_at(board.parse_san(move).to_square)
                    if piece and piece.piece_type == chess.ROOK and piece.color == chess.WHITE:
                        if chess.square_rank(board.parse_san(move).to_square) == 6:  # 7th rank for White
                            return i + 1
            else:
                if board.turn == chess.WHITE:  # Check the position after White's move
                    piece = board.piece_at(board.parse_san(move).to_square)
                    if piece and piece.piece_type == chess.ROOK and piece.color == chess.BLACK:
                        if chess.square_rank(board.parse_san(move).to_square) == 6:  # 7th rank for White
                            return i + 1
            board.push_san(move)

        return np.nan  # No such move found

    def count_white_minor_pieces_center_attack_defense(self,moves,white):
        board = chess.Board()
        # Advance the board state by 10 plies to account for the first 5 moves
        for i,move in enumerate(moves):
            if i<10:
                board.push_san(move)


        # Define the central squares of interest
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        minors_attacking_defending = 0

        # Iterate over center squares and count White knights and bishops attacking or defending them
        if white:
            for square in center_squares:
                attackers_and_defenders = board.attackers(chess.WHITE, square)
                for piece_square in attackers_and_defenders:
                    piece = board.piece_at(piece_square)
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        minors_attacking_defending += 1
        else:
            for square in center_squares:
                attackers_and_defenders = board.attackers(chess.BLACK, square)
                for piece_square in attackers_and_defenders:
                    piece = board.piece_at(piece_square)
                    if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                        minors_attacking_defending += 1

        return minors_attacking_defending

    def check_minor_before_major_development(self,moves,white):
        board = chess.Board()
        minor_developed = set()
        major_moved = False
        if white:
            color=chess.WHITE
        else:
            color=chess.BLACK

        for move in moves:
            square=board.parse_san(move).to_square
            board.push_san(move)
            piece = board.piece_at(square)

            if piece.color == color:
                if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    minor_developed.add((piece.piece_type, square))
                elif piece.piece_type in [chess.QUEEN, chess.ROOK]:
                    major_moved = True
                    break  # Stop checking once a major piece has moved

        return not major_moved and len(minor_developed) > 0

    def get_edge_squares(self):
        edge_squares = set()
        # Add squares from the 1st and 8th ranks
        for file in range(8):  # Files are from 0 to 7
            edge_squares.add(chess.square(file, 0))  # 1st rank
            edge_squares.add(chess.square(file, 7))  # 8th rank

        # Add squares from the 'a' and 'h' files
        for rank in range(8):  # Ranks are from 0 to 7
            edge_squares.add(chess.square(0, rank))  # 'a' file
            edge_squares.add(chess.square(7, rank))  # 'h' file

        return edge_squares

    def move_knight_edge_moves(self,moves,white):
        board = chess.Board()
        edge_squares =self.get_edge_squares()

        if white:
            color=chess.BLACK
        else:
            color=chess.WHITE

        for i,move in enumerate(moves):
            square=board.parse_san(move).to_square
            board.push_san(move)


            if board.turn == color:  # After White has moved
                if board.piece_at(square) and board.piece_at(square).piece_type == chess.KNIGHT:
                    if square in edge_squares and board.piece_at(square).color == chess.WHITE:
                        return i

        return np.nan

    def count_knight_edge_moves(self,moves,white):
        board = chess.Board()
        edge_squares =self.get_edge_squares()

        knight_edge_moves = 0
        if white:
            color=chess.BLACK
        else:
            color=chess.WHITE

        for move in moves:
            square=board.parse_san(move).to_square
            board.push_san(move)


            if board.turn == color:  # After White has moved
                if board.piece_at(square) and board.piece_at(square).piece_type == chess.KNIGHT:
                    if square in edge_squares and board.piece_at(square).color == chess.WHITE:
                        knight_edge_moves += 1

        return knight_edge_moves

    def count_isolated_pawns_helper(self,board,color):
        isolated_pawns = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color ==color  and piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                is_isolated = True
                # Check neighboring files
                for neighbor_file in [file - 1, file + 1]:
                    if neighbor_file < 0 or neighbor_file > 7:
                        continue
                    if any(board.piece_at(chess.square(neighbor_file, rank)) and
                        board.piece_at(chess.square(neighbor_file, rank)).piece_type == chess.PAWN
                        for rank in range(8)):
                        is_isolated = False
                        break
                if is_isolated:
                    isolated_pawns += 1
        return isolated_pawns

    def count_isolated_pawns(self,moves,white,percentage):
        board = chess.Board()
        total_moves = len(moves)
        isolated_counts = []

        for move_number, move in enumerate(moves):
            board.push_san(move)
            if move_number ==int(total_moves * percentage):
                if white:
                    isolated_counts.append((move_number,self. count_isolated_pawns_helper(board,chess.WHITE)))
                else:
                    isolated_counts.append((move_number, self.count_isolated_pawns_helper(board,chess.BLACK)))

        return isolated_counts[0][1]


    def count_doubled_pawns(self,moves,white,percentage):
        board = chess.Board()
        total_moves = len(moves)
        doubled_pawn_counts = []

        for move_number, move in enumerate(moves):
            board.push_san(move)
            if move_number ==int(total_moves * percentage):
                if white:
                    doubled_pawn_counts.append((move_number, self.count_doubled_white_helper(board,chess.WHITE)))
                else:
                    doubled_pawn_counts.append((move_number, self.count_doubled_white_helper(board,chess.BLACK)))
        return doubled_pawn_counts[0][1]

    def count_doubled_white_helper(self,board,color):
        file_pawn_count = [0] * 8  # There are 8 files, indexed 0 to 7
        doubled_pawns = 0

        # Count pawns on each file
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                file_pawn_count[file] += 1

        # Count files with more than one pawn
        for count in file_pawn_count:
            if count > 1:
                doubled_pawns += (count - 1)  # Add the number of pawns above the first for doubling

        return doubled_pawns


    def count_triple_pawns(self,moves,white,percentage):
        board = chess.Board()
        total_moves = len(moves)
        tripled_pawn_counts = []

        for move_number, move in enumerate(moves):
            board.push_san(move)
            if move_number ==int(total_moves * percentage):
                if white:
                    tripled_pawn_counts.append((move_number, self.count_tripled_white_helper(board,chess.WHITE)))
                else:
                    tripled_pawn_counts.append((move_number, self.count_tripled_white_helper(board,chess.BLACK)))
        return tripled_pawn_counts[0][1]

    def count_tripled_white_helper(self,board,color):
        file_pawn_count = [0] * 8  # There are 8 files, indexed 0 to 7
        tripled_pawns = 0

        # Count pawns on each file
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color and piece.piece_type == chess.PAWN:
                file = chess.square_file(square)
                file_pawn_count[file] += 1

        # Count files with more than one pawn
        for count in file_pawn_count:
            if count > 2:
                tripled_pawns += (count - 1)  # Add the number of pawns above the first for doubling

        return tripled_pawns
