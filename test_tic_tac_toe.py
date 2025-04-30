#!/usr/bin/env python3
"""
Script de test pour le jeu Tic Tac Toe en ligne avec agent DRL
Vérifie le bon fonctionnement du serveur, du client et de l'agent DRL
"""

import unittest
import asyncio
import json
import socket
import threading
import time
import sys
import os
import numpy as np
from server import GameServer, TicTacToeGame
from drl_agent import DRLAgent, TicTacToeEnv

class TestTicTacToeGame(unittest.TestCase):
    """Tests unitaires pour la logique du jeu Tic Tac Toe"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.game = TicTacToeGame("test_game", "player1", "player2")
    
    def test_initial_state(self):
        """Teste l'état initial du jeu"""
        self.assertEqual(self.game.board, [[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.assertEqual(self.game.current_player, 1)
        self.assertFalse(self.game.game_over)
        self.assertIsNone(self.game.winner)
    
    def test_make_move(self):
        """Teste l'exécution d'un coup valide"""
        valid, _ = self.game.make_move(0, 0)
        self.assertTrue(valid)
        self.assertEqual(self.game.board[0][0], 1)
        self.assertEqual(self.game.current_player, 2)
    
    def test_invalid_move(self):
        """Teste l'exécution d'un coup invalide"""
        self.game.make_move(0, 0)
        valid, _ = self.game.make_move(0, 0)
        self.assertFalse(valid)
    
    def test_win_horizontal(self):
        """Teste la détection d'une victoire horizontale"""
        self.game.make_move(0, 0)  # X
        self.game.make_move(1, 0)  # O
        self.game.make_move(0, 1)  # X
        self.game.make_move(1, 1)  # O
        self.game.make_move(0, 2)  # X
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 1)
        self.assertEqual(self.game.winning_line, [(0, 0), (0, 1), (0, 2)])
    
    def test_win_vertical(self):
        """Teste la détection d'une victoire verticale"""
        self.game.make_move(0, 0)  # X
        self.game.make_move(0, 1)  # O
        self.game.make_move(1, 0)  # X
        self.game.make_move(1, 1)  # O
        self.game.make_move(2, 0)  # X
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 1)
        self.assertEqual(self.game.winning_line, [(0, 0), (1, 0), (2, 0)])
    
    def test_win_diagonal(self):
        """Teste la détection d'une victoire diagonale"""
        self.game.make_move(0, 0)  # X
        self.game.make_move(0, 1)  # O
        self.game.make_move(1, 1)  # X
        self.game.make_move(0, 2)  # O
        self.game.make_move(2, 2)  # X
        
        self.assertTrue(self.game.game_over)
        self.assertEqual(self.game.winner, 1)
        self.assertEqual(self.game.winning_line, [(0, 0), (1, 1), (2, 2)])
    
    def test_draw(self):
        """Teste la détection d'un match nul"""
        # Créer une nouvelle instance de jeu pour ce test spécifique
        game = TicTacToeGame("test_draw", "player1", "player2")
        
        # Créer directement un état de match nul valide
        # X O X
        # X X O
        # O X O
        game.board = [
            [1, 2, 1],
            [1, 1, 2],
            [2, 1, 2]
        ]
        game.moves_count = 9
        game.check_winner()
        
        # Vérifier que la partie est terminée et que c'est un match nul
        self.assertTrue(game.game_over)
        self.assertIsNone(game.winner)

class TestDRLAgent(unittest.TestCase):
    """Tests unitaires pour l'agent DRL"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.env = TicTacToeEnv()
        self.agent = DRLAgent()
    
    def test_env_reset(self):
        """Teste la réinitialisation de l'environnement"""
        state = self.env.reset()
        self.assertEqual(self.env.board.shape, (3, 3))
        self.assertEqual(np.sum(self.env.board), 0)  # Grille vide
        self.assertEqual(state.shape, (1, 3, 3, 3))  # Format d'état correct
    
    def test_valid_actions(self):
        """Teste l'obtention des actions valides"""
        self.env.reset()
        valid_actions = self.env.get_valid_actions()
        self.assertEqual(len(valid_actions), 9)  # Toutes les cases sont vides
        
        # Jouer un coup
        self.env.board[0, 0] = 1
        valid_actions = self.env.get_valid_actions()
        self.assertEqual(len(valid_actions), 8)  # Une case occupée
        self.assertNotIn(0, valid_actions)  # La case (0,0) n'est plus valide
    
    def test_agent_act(self):
        """Teste la sélection d'action par l'agent"""
        state = self.env.reset()
        valid_actions = self.env.get_valid_actions()
        
        # Forcer l'exploration à 0 pour un comportement déterministe
        self.agent.epsilon = 0
        
        action = self.agent.act(state, valid_actions)
        self.assertIn(action, valid_actions)
    
    def test_step_reward(self):
        """Teste les récompenses de l'environnement"""
        self.env.reset()
        
        # Jouer un coup gagnant
        self.env.board[0, 0] = 1
        self.env.board[0, 1] = 1
        
        # Le prochain coup sur (0,2) devrait être gagnant
        action = 2  # (0,2)
        _, reward, done, _ = self.env.step(action)
        
        self.assertTrue(done)
        self.assertEqual(reward, 1.0)  # Récompense pour une victoire

class TestNetworkIntegration(unittest.TestCase):
    """Tests d'intégration pour la communication réseau"""
    
    @classmethod
    def setUpClass(cls):
        """Démarrage du serveur pour les tests"""
        cls.server_thread = threading.Thread(target=cls.run_server)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Attendre que le serveur démarre
    
    @classmethod
    def run_server(cls):
        """Exécute le serveur dans un thread séparé"""
        asyncio.set_event_loop(asyncio.new_event_loop())
        cls.server = GameServer(port=8889)
        asyncio.get_event_loop().run_until_complete(cls.server.start_server())
    
    def test_server_connection(self):
        """Teste la connexion au serveur"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect(('localhost', 8889))
            sock.sendall(json.dumps({"type": "CONNECT", "player_name": "TestPlayer"}).encode())
            
            # Attendre la réponse
            data = sock.recv(1024)
            response = json.loads(data.decode())
            
            self.assertEqual(response["type"], "CONNECT_RESPONSE")
            self.assertIn("client_id", response)
        finally:
            sock.close()

def run_tests():
    """Exécute tous les tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter les tests
    suite.addTests(loader.loadTestsFromTestCase(TestTicTacToeGame))
    suite.addTests(loader.loadTestsFromTestCase(TestDRLAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestNetworkIntegration))
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
