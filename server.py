#!/usr/bin/env python3
"""
Serveur de jeu Tic Tac Toe en ligne avec support pour agent DRL
Utilise asyncio et sockets pour la communication réseau
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tic_tac_toe_server')

class TicTacToeGame:
    """Classe représentant la logique du jeu Tic Tac Toe"""
    
    def __init__(self, game_id, player1_id, player2_id=None, vs_ai=False):
        self.game_id = game_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.vs_ai = vs_ai
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # 0=vide, 1=X, 2=O
        self.current_player = 1  # 1=X (premier joueur), 2=O (deuxième joueur)
        self.winner = None
        self.winning_line = None
        self.game_over = False
        self.moves_count = 0
        self.created_at = datetime.now()
        
    def get_state(self):
        """Retourne l'état actuel du jeu"""
        return {
            "type": "GAME_STATE",
            "game_id": self.game_id,
            "board": self.board,
            "current_player": "X" if self.current_player == 1 else "O",
            "game_over": self.game_over,
            "winner": self.get_winner_symbol() if self.winner else None,
            "winning_line": self.winning_line
        }
    
    def get_winner_symbol(self):
        """Convertit le numéro du gagnant en symbole"""
        if not self.winner:
            return None
        return "X" if self.winner == 1 else "O"
    
    def make_move(self, row, col):
        """Effectue un coup sur la grille"""
        # Vérifier si le coup est valide
        if row < 0 or row > 2 or col < 0 or col > 2:
            return False, "Position hors limites"
        
        if self.board[row][col] != 0:
            return False, "Case déjà occupée"
        
        if self.game_over:
            return False, "La partie est terminée"
        
        # Effectuer le coup
        self.board[row][col] = self.current_player
        self.moves_count += 1
        
        # Vérifier s'il y a un gagnant
        self.check_winner()
        
        # Si la partie n'est pas terminée, passer au joueur suivant
        if not self.game_over:
            self.switch_player()
            
        return True, "Coup valide"
    
    def switch_player(self):
        """Passe au joueur suivant"""
        self.current_player = 2 if self.current_player == 1 else 1
    
    def check_winner(self):
        """Vérifie s'il y a un gagnant"""
        # Vérifier les lignes
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != 0:
                self.winner = self.board[i][0]
                self.winning_line = [(i, 0), (i, 1), (i, 2)]
                self.game_over = True
                return
        
        # Vérifier les colonnes
        for j in range(3):
            if self.board[0][j] == self.board[1][j] == self.board[2][j] != 0:
                self.winner = self.board[0][j]
                self.winning_line = [(0, j), (1, j), (2, j)]
                self.game_over = True
                return
        
        # Vérifier la diagonale principale
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != 0:
            self.winner = self.board[0][0]
            self.winning_line = [(0, 0), (1, 1), (2, 2)]
            self.game_over = True
            return
        
        # Vérifier la diagonale secondaire
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != 0:
            self.winner = self.board[0][2]
            self.winning_line = [(0, 2), (1, 1), (2, 0)]
            self.game_over = True
            return
        
        # Vérifier s'il y a match nul (toutes les cases sont remplies)
        if self.moves_count == 9:
            self.game_over = True
            self.winner = None  # S'assurer que winner est None en cas de match nul
            return

class GameServer:
    """Serveur de jeu Tic Tac Toe utilisant asyncio et sockets"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.clients = {}  # {client_id: {"writer": writer, "reader": reader, "name": name}}
        self.games = {}    # {game_id: TicTacToeGame}
        self.waiting_players = []  # Liste des joueurs en attente d'une partie
        
    async def start_server(self):
        """Démarre le serveur et attend les connexions entrantes"""
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f'Serveur démarré sur {addr}')
        
        async with server:
            await server.serve_forever()
    
    async def handle_client(self, reader, writer):
        """Gère une connexion client"""
        # Générer un ID unique pour ce client
        client_id = str(uuid.uuid4())
        
        # Stocker les informations du client
        self.clients[client_id] = {
            "reader": reader,
            "writer": writer,
            "name": f"Joueur_{client_id[:8]}",  # Nom par défaut
            "game_id": None
        }
        
        addr = writer.get_extra_info('peername')
        logger.info(f'Nouvelle connexion de {addr}, client_id: {client_id}')
        
        # Envoyer un message de bienvenue
        await self.send_message(client_id, {
            "type": "CONNECT_RESPONSE",
            "client_id": client_id,
            "message": "Connecté au serveur Tic Tac Toe"
        })
        
        try:
            # Boucle de lecture des messages
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode())
                    await self.process_message(client_id, message)
                except json.JSONDecodeError:
                    logger.error(f"Message invalide reçu de {client_id}: {data}")
                    await self.send_message(client_id, {
                        "type": "ERROR",
                        "message": "Format de message invalide"
                    })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Erreur lors du traitement des messages de {client_id}: {e}")
        finally:
            # Nettoyage à la déconnexion
            await self.handle_disconnect(client_id)
            writer.close()
            await writer.wait_closed()
            logger.info(f'Connexion fermée pour {client_id}')
    
    async def process_message(self, client_id, message):
        """Traite un message reçu d'un client"""
        message_type = message.get("type", "")
        logger.info(f"Message reçu de {client_id}: {message_type}")
        
        if message_type == "CONNECT":
            # Mise à jour du nom du joueur
            player_name = message.get("player_name", f"Joueur_{client_id[:8]}")
            self.clients[client_id]["name"] = player_name
            logger.info(f"Joueur {client_id} s'est identifié comme {player_name}")
            
            await self.send_message(client_id, {
                "type": "CONNECT_RESPONSE",
                "client_id": client_id,
                "player_name": player_name,
                "message": f"Bienvenue, {player_name}!"
            })
        
        elif message_type == "NEW_GAME":
            # Demande de nouvelle partie
            opponent_type = message.get("opponent_type", "human")
            
            if opponent_type == "ai":
                # Créer une partie contre l'IA
                await self.create_game(client_id, vs_ai=True)
            else:
                # Ajouter le joueur à la liste d'attente
                if client_id not in self.waiting_players:
                    self.waiting_players.append(client_id)
                
                # Informer le joueur qu'il est en attente
                await self.send_message(client_id, {
                    "type": "WAITING",
                    "message": "En attente d'un adversaire..."
                })
                
                # Vérifier s'il y a au moins deux joueurs en attente
                if len(self.waiting_players) >= 2:
                    player1_id = self.waiting_players.pop(0)
                    player2_id = self.waiting_players.pop(0)
                    await self.create_game(player1_id, player2_id)
        
        elif message_type == "PLAY":
            # Coup joué par un joueur
            position = message.get("position", [])
            
            if len(position) != 2:
                await self.send_message(client_id, {
                    "type": "ERROR",
                    "message": "Format de position invalide"
                })
                return
            
            row, col = position
            game_id = self.clients[client_id].get("game_id")
            
            if not game_id or game_id not in self.games:
                await self.send_message(client_id, {
                    "type": "ERROR",
                    "message": "Vous n'êtes pas dans une partie active"
                })
                return
            
            game = self.games[game_id]
            
            # Vérifier si c'est le tour du joueur
            player_number = 1 if game.player1_id == client_id else 2
            if player_number != game.current_player:
                await self.send_message(client_id, {
                    "type": "ERROR",
                    "message": "Ce n'est pas votre tour"
                })
                return
            
            # Effectuer le coup
            valid, message_text = game.make_move(row, col)
            
            if not valid:
                await self.send_message(client_id, {
                    "type": "ERROR",
                    "message": message_text
                })
                return
            
            # Envoyer le résultat du coup aux deux joueurs
            await self.broadcast_game_state(game_id)
            
            # Si c'est une partie contre l'IA et que c'est au tour de l'IA
            if game.vs_ai and game.current_player == 2 and not game.game_over:
                await self.ai_play(game_id)
        
        elif message_type == "DISCONNECT":
            # Déconnexion volontaire
            await self.handle_disconnect(client_id)
    
    async def create_game(self, player1_id, player2_id=None, vs_ai=False):
        """Crée une nouvelle partie"""
        game_id = str(uuid.uuid4())
        
        # Créer l'objet de jeu
        game = TicTacToeGame(game_id, player1_id, player2_id, vs_ai)
        self.games[game_id] = game
        
        # Mettre à jour les informations des clients
        self.clients[player1_id]["game_id"] = game_id
        if player2_id:
            self.clients[player2_id]["game_id"] = game_id
        
        # Informer les joueurs que la partie commence
        player1_name = self.clients[player1_id]["name"]
        player2_name = self.clients[player2_id]["name"] if player2_id else "IA"
        
        await self.send_message(player1_id, {
            "type": "GAME_CREATED",
            "game_id": game_id,
            "opponent": player2_name,
            "you_play": "X"
        })
        
        if player2_id:
            await self.send_message(player2_id, {
                "type": "GAME_CREATED",
                "game_id": game_id,
                "opponent": player1_name,
                "you_play": "O"
            })
        
        # Envoyer l'état initial du jeu
        await self.broadcast_game_state(game_id)
        
        logger.info(f"Nouvelle partie créée: {game_id} entre {player1_name} et {player2_name}")
        return game_id
    
    async def broadcast_game_state(self, game_id):
        """Envoie l'état du jeu à tous les joueurs de la partie"""
        if game_id not in self.games:
            return
        
        game = self.games[game_id]
        game_state = game.get_state()
        
        # Envoyer l'état au premier joueur
        await self.send_message(game.player1_id, game_state)
        
        # Envoyer l'état au deuxième joueur (s'il existe)
        if game.player2_id:
            await self.send_message(game.player2_id, game_state)
        
        # Si la partie est terminée, envoyer un message de fin
        if game.game_over:
            winner_message = {
                "type": "GAME_OVER",
                "game_id": game_id,
                "winner": game.get_winner_symbol(),
                "winning_line": game.winning_line
            }
            
            await self.send_message(game.player1_id, winner_message)
            if game.player2_id:
                await self.send_message(game.player2_id, winner_message)
            
            # Nettoyer la partie terminée après un certain délai
            asyncio.create_task(self.cleanup_game(game_id, delay=60))
    
    async def ai_play(self, game_id):
        """Fait jouer l'IA dans une partie"""
        if game_id not in self.games:
            return
        
        game = self.games[game_id]
        
        # Pour l'instant, l'IA joue de manière aléatoire
        # Cela sera remplacé par l'agent DRL dans une étape ultérieure
        import random
        available_moves = []
        
        for i in range(3):
            for j in range(3):
                if game.board[i][j] == 0:
                    available_moves.append((i, j))
        
        if available_moves:
            row, col = random.choice(available_moves)
            game.make_move(row, col)
            
            # Envoyer l'état mis à jour
            await self.broadcast_game_state(game_id)
    
    async def handle_disconnect(self, client_id):
        """Gère la déconnexion d'un client"""
        if client_id not in self.clients:
            return
        
        # Retirer le joueur de la liste d'attente
        if client_id in self.waiting_players:
            self.waiting_players.remove(client_id)
        
        # Gérer la partie en cours
        game_id = self.clients[client_id].get("game_id")
        if game_id and game_id in self.games:
            game = self.games[game_id]
            
            # Informer l'autre joueur de la déconnexion
            other_player_id = None
            if game.player1_id == client_id and game.player2_id:
                other_player_id = game.player2_id
            elif game.player2_id == client_id:
                other_player_id = game.player1_id
            
            if other_player_id:
                await self.send_message(other_player_id, {
                    "type": "OPPONENT_DISCONNECTED",
                    "message": "Votre adversaire s'est déconnecté"
                })
                
                # Mettre à jour l'état du jeu
                self.clients[other_player_id]["game_id"] = None
            
            # Nettoyer la partie
            asyncio.create_task(self.cleanup_game(game_id, delay=0))
        
        # Supprimer le client
        del self.clients[client_id]
    
    async def cleanup_game(self, game_id, delay=0):
        """Nettoie une partie terminée après un délai"""
        if delay > 0:
            await asyncio.sleep(delay)
        
        if game_id in self.games:
            del self.games[game_id]
            logger.info(f"Partie {game_id} nettoyée")
    
    async def send_message(self, client_id, message):
        """Envoie un message à un client"""
        if client_id not in self.clients:
            return
        
        writer = self.clients[client_id]["writer"]
        try:
            writer.write(json.dumps(message).encode())
            await writer.drain()
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message à {client_id}: {e}")

async def main():
    """Fonction principale pour démarrer le serveur"""
    server = GameServer()
    await server.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Serveur arrêté par l'utilisateur")
