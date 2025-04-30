#!/usr/bin/env python3
"""
Client de jeu Tic Tac Toe en ligne avec interface Tkinter
Se connecte au serveur via sockets et permet de jouer au jeu
"""

import asyncio
import json
import tkinter as tk
from tkinter import messagebox, simpledialog
import socket
import threading
import logging
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tic_tac_toe_client')

class TicTacToeClient:
    """Client de jeu Tic Tac Toe avec interface Tkinter"""
    
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.client_id = None
        self.player_name = None
        self.game_id = None
        self.symbol = None  # 'X' ou 'O'
        self.current_player = None
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # 0=vide, 1=X, 2=O
        self.game_over = False
        self.winner = None
        self.winning_line = None
        
        # Initialisation de l'interface Tkinter
        self.root = tk.Tk()
        self.root.title("Tic Tac Toe en ligne")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.setup_ui()
        
        # Démarrer la connexion dans un thread séparé
        self.connection_thread = threading.Thread(target=self.start_connection)
        self.connection_thread.daemon = True
        self.connection_thread.start()
    
    def setup_ui(self):
        """Configure l'interface utilisateur Tkinter"""
        # Frame principale
        self.main_frame = tk.Frame(self.root, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        self.title_label = tk.Label(
            self.main_frame, 
            text="Tic Tac Toe en ligne", 
            font=("Helvetica", 16, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Statut
        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = tk.Label(
            self.status_frame, 
            text="En attente de connexion...", 
            font=("Helvetica", 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.player_label = tk.Label(
            self.status_frame, 
            text="", 
            font=("Helvetica", 10, "bold")
        )
        self.player_label.pack(side=tk.RIGHT)
        
        # Grille de jeu (initialement cachée)
        self.game_frame = tk.Frame(self.main_frame)
        self.game_frame.pack(pady=20)
        
        self.buttons = []
        for i in range(3):
            row = []
            for j in range(3):
                button = tk.Button(
                    self.game_frame, 
                    text="", 
                    font=("Helvetica", 20, "bold"),
                    width=3, height=1,
                    command=lambda r=i, c=j: self.on_button_click(r, c)
                )
                button.grid(row=i, column=j, padx=5, pady=5)
                row.append(button)
            self.buttons.append(row)
        
        # Boutons de contrôle
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(fill=tk.X, pady=10)
        
        self.new_game_human_button = tk.Button(
            self.control_frame,
            text="Nouvelle partie (vs Humain)",
            command=lambda: self.request_new_game("human")
        )
        self.new_game_human_button.pack(side=tk.LEFT, padx=5)
        
        self.new_game_ai_button = tk.Button(
            self.control_frame,
            text="Nouvelle partie (vs IA)",
            command=lambda: self.request_new_game("ai")
        )
        self.new_game_ai_button.pack(side=tk.RIGHT, padx=5)
        
        # Désactiver les boutons jusqu'à la connexion
        self.set_buttons_state(False)
    
    def set_buttons_state(self, enabled):
        """Active ou désactive les boutons de contrôle"""
        state = tk.NORMAL if enabled else tk.DISABLED
        self.new_game_human_button.config(state=state)
        self.new_game_ai_button.config(state=state)
    
    def update_status(self, message):
        """Met à jour le message de statut"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_player_info(self):
        """Met à jour les informations du joueur"""
        if self.symbol:
            self.player_label.config(text=f"Vous jouez: {self.symbol}")
        else:
            self.player_label.config(text="")
    
    def update_board(self):
        """Met à jour l'affichage de la grille de jeu"""
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    self.buttons[i][j].config(text="", bg="SystemButtonFace")
                elif self.board[i][j] == 1:
                    self.buttons[i][j].config(text="X", bg="SystemButtonFace")
                elif self.board[i][j] == 2:
                    self.buttons[i][j].config(text="O", bg="SystemButtonFace")
        
        # Mettre en évidence la ligne gagnante
        if self.winning_line:
            for pos in self.winning_line:
                i, j = pos
                self.buttons[i][j].config(bg="light green")
    
    def on_button_click(self, row, col):
        """Gère le clic sur une case de la grille"""
        # Vérifier si le jeu est en cours et si c'est le tour du joueur
        if self.game_over:
            return
        
        if self.current_player != self.symbol:
            messagebox.showinfo("Pas votre tour", "Attendez votre tour pour jouer.")
            return
        
        # Vérifier si la case est vide
        if self.board[row][col] != 0:
            return
        
        # Envoyer le coup au serveur
        asyncio.run_coroutine_threadsafe(
            self.send_message({
                "type": "PLAY",
                "position": [row, col]
            }),
            asyncio.get_event_loop()
        )
    
    def request_new_game(self, opponent_type):
        """Demande une nouvelle partie"""
        asyncio.run_coroutine_threadsafe(
            self.send_message({
                "type": "NEW_GAME",
                "opponent_type": opponent_type
            }),
            asyncio.get_event_loop()
        )
        self.update_status("Demande de nouvelle partie envoyée...")
    
    def on_closing(self):
        """Gère la fermeture de la fenêtre"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter?"):
            # Envoyer un message de déconnexion si connecté
            if self.writer:
                asyncio.run_coroutine_threadsafe(
                    self.send_message({"type": "DISCONNECT"}),
                    asyncio.get_event_loop()
                )
            self.root.destroy()
    
    def start_connection(self):
        """Démarre la connexion au serveur dans un thread séparé"""
        try:
            # Créer une nouvelle boucle d'événements pour ce thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Demander le nom du joueur via la file d'événements Tkinter
            self.root.after(0, self.ask_player_name)
            
            # Attendre que le nom du joueur soit défini
            while self.player_name is None:
                time.sleep(0.1)
            
            # Exécuter la connexion
            loop.run_until_complete(self.connect_to_server())
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
            self.root.after(0, lambda: self.update_status(f"Erreur de connexion: {e}"))
    
    def ask_player_name(self):
        """Demande le nom du joueur"""
        try:
            # Utiliser la fenêtre principale comme parent
            name = simpledialog.askstring(
                "Nom du joueur", 
                "Entrez votre nom:",
                parent=self.root
            )
            if name:
                self.player_name = name
            else:
                self.player_name = f"Joueur_{socket.gethostname()}"
        except Exception as e:
            logger.warning(f"Erreur lors de la demande du nom: {e}")
            self.player_name = f"Joueur_{socket.gethostname()}"
    
    async def connect_to_server(self):
        """Se connecte au serveur"""
        try:
            self.update_status(f"Connexion au serveur {self.host}:{self.port}...")
            
            # Gestion spécifique pour Windows - vérifier le format de l'adresse
            if self.host == "localhost":
                try:
                    self.reader, self.writer = await asyncio.open_connection(
                        self.host, self.port
                    )
                except Exception as e:
                    if "format du nom réseau" in str(e) or "network name" in str(e):
                        # Erreur Windows spécifique - essayer avec l'adresse IP directe
                        self.update_status("Tentative de connexion avec l'adresse IP locale (127.0.0.1)...")
                        self.host = "127.0.0.1"
                        self.reader, self.writer = await asyncio.open_connection(
                            self.host, self.port
                        )
                    else:
                        raise e
            else:
                self.reader, self.writer = await asyncio.open_connection(
                    self.host, self.port
                )
            
            self.update_status("Connecté au serveur")
            
            # Envoyer les informations du joueur
            await self.send_message({
                "type": "CONNECT",
                "player_name": self.player_name
            })
            
            # Activer les boutons
            self.root.after(0, self.set_buttons_state, True)
            
            # Boucle de réception des messages
            while True:
                try:
                    data = await self.reader.read(4096)
                    if not data:
                        break
                    
                    message = json.loads(data.decode())
                    self.process_message(message)
                except json.JSONDecodeError:
                    logger.error(f"Message invalide reçu: {data}")
                except Exception as e:
                    logger.error(f"Erreur lors de la réception des messages: {e}")
                    break
            
            self.update_status("Déconnecté du serveur")
            self.set_buttons_state(False)
        except Exception as e:
            logger.error(f"Erreur de connexion: {e}")
            self.update_status(f"Erreur de connexion: {e}")
    
    async def send_message(self, message):
        """Envoie un message au serveur"""
        if not self.writer:
            return
        
        try:
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message: {e}")
    
    def process_message(self, message):
        """Traite un message reçu du serveur"""
        message_type = message.get("type", "")
        logger.info(f"Message reçu: {message_type}")
        
        if message_type == "CONNECT_RESPONSE":
            self.client_id = message.get("client_id")
            self.update_status(f"Connecté en tant que {self.player_name}")
        
        elif message_type == "GAME_CREATED":
            self.game_id = message.get("game_id")
            opponent = message.get("opponent")
            self.symbol = message.get("you_play")
            self.update_status(f"Partie créée contre {opponent}")
            self.update_player_info()
            
            # Réinitialiser la grille
            self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            self.game_over = False
            self.winner = None
            self.winning_line = None
            self.update_board()
        
        elif message_type == "GAME_STATE":
            self.board = message.get("board")
            self.current_player = message.get("current_player")
            self.game_over = message.get("game_over", False)
            self.winner = message.get("winner")
            self.winning_line = message.get("winning_line")
            
            self.update_board()
            
            if self.current_player == self.symbol and not self.game_over:
                self.update_status("C'est votre tour")
            elif not self.game_over:
                self.update_status("En attente du coup de l'adversaire")
        
        elif message_type == "GAME_OVER":
            self.game_over = True
            self.winner = message.get("winner")
            self.winning_line = message.get("winning_line")
            
            self.update_board()
            
            if self.winner == self.symbol:
                self.update_status("Vous avez gagné!")
                messagebox.showinfo("Partie terminée", "Félicitations, vous avez gagné!")
            elif self.winner == "draw":
                self.update_status("Match nul!")
                messagebox.showinfo("Partie terminée", "Match nul!")
            else:
                self.update_status("Vous avez perdu!")
                messagebox.showinfo("Partie terminée", "Vous avez perdu!")
        
        elif message_type == "WAITING":
            self.update_status("En attente d'un adversaire...")
        
        elif message_type == "OPPONENT_DISCONNECTED":
            messagebox.showinfo("Information", "Votre adversaire s'est déconnecté")
            self.update_status("Adversaire déconnecté")
            self.game_over = True
        
        elif message_type == "ERROR":
            error_message = message.get("message", "Erreur inconnue")
            self.update_status(f"Erreur: {error_message}")
            messagebox.showerror("Erreur", error_message)

def main():
    """Fonction principale pour démarrer le client"""
    try:
        # Créer une fenêtre temporaire pour les boîtes de dialogue
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre principale temporaire
        
        # Demander l'adresse du serveur
        try:
            host = simpledialog.askstring(
                "Adresse du serveur", 
                "Entrez l'adresse du serveur:\n(utilisez 127.0.0.1 au lieu de localhost sur Windows)",
                initialvalue="127.0.0.1",
                parent=root
            )
        except Exception as e:
            logger.warning(f"Erreur lors de la demande d'adresse: {e}")
            host = "127.0.0.1"
        
        if not host:
            host = "127.0.0.1"
        
        # Demander le port du serveur
        try:
            port_str = simpledialog.askstring(
                "Port du serveur", 
                "Entrez le port du serveur:",
                initialvalue="8888",
                parent=root
            )
        except Exception as e:
            logger.warning(f"Erreur lors de la demande de port: {e}")
            port_str = "8888"
        
        try:
            port = int(port_str) if port_str else 8888
        except ValueError:
            port = 8888
        
        # Détruire la fenêtre temporaire
        root.destroy()
        
        # Créer et démarrer le client
        client = TicTacToeClient(host, port)
        client.root.mainloop()
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du client: {e}")
        messagebox.showerror("Erreur", f"Erreur lors du démarrage du client: {e}")
        # Assurer que toutes les fenêtres sont fermées
        try:
            tk.Tk().destroy()
        except:
            pass

if __name__ == "__main__":
    main()
