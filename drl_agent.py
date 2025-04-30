#!/usr/bin/env python3
"""
Agent DRL (Deep Reinforcement Learning) pour le jeu Tic Tac Toe
Utilise TensorFlow pour implémenter un agent d'apprentissage par renforcement
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D
from tensorflow.keras.optimizers import Adam
import random
from collections import deque
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('drl_agent')

class DRLAgent:
    """Agent d'apprentissage par renforcement profond pour Tic Tac Toe"""
    
    def __init__(self, state_size=(3, 3, 3), action_size=9, load_model=False, model_path=None):
        self.state_size = state_size  # Taille de l'état (grille 3x3 avec 3 canaux: vide, X, O)
        self.action_size = action_size  # Nombre d'actions possibles (9 cases)
        self.memory = deque(maxlen=2000)  # Mémoire de replay
        self.gamma = 0.95  # Facteur de réduction pour les récompenses futures
        self.epsilon = 1.0  # Taux d'exploration
        self.epsilon_min = 0.01  # Taux d'exploration minimum
        self.epsilon_decay = 0.995  # Taux de décroissance de l'exploration
        self.learning_rate = 0.001  # Taux d'apprentissage
        self.model = self._build_model()  # Modèle de réseau de neurones
        
        if load_model and model_path:
            self.load(model_path)
            self.epsilon = self.epsilon_min  # Réduire l'exploration si on charge un modèle entraîné
    
    def _build_model(self):
        """Construit le modèle de réseau de neurones"""
        model = Sequential()
        
        # Couche de convolution pour extraire des caractéristiques spatiales
        model.add(Conv2D(32, (2, 2), activation='relu', input_shape=self.state_size))
        model.add(Flatten())
        
        # Couches denses pour l'approximation de la fonction Q
        model.add(Dense(64, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def remember(self, state, action, reward, next_state, done):
        """Stocke une expérience dans la mémoire de replay"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state, valid_actions):
        """Choisit une action en fonction de l'état actuel"""
        # Exploration aléatoire avec probabilité epsilon
        if np.random.rand() <= self.epsilon:
            return random.choice(valid_actions)
        
        # Exploitation: choisir l'action avec la plus grande valeur Q
        act_values = self.model.predict(state, verbose=0)
        
        # Filtrer les actions valides
        valid_q_values = [(i, act_values[0][i]) for i in valid_actions]
        
        # Trier par valeur Q décroissante
        valid_q_values.sort(key=lambda x: x[1], reverse=True)
        
        return valid_q_values[0][0]  # Retourner l'action avec la plus grande valeur Q
    
    def replay(self, batch_size):
        """Entraîne le modèle sur un mini-batch d'expériences"""
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.model.predict(next_state, verbose=0)[0])
            
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            
            self.model.fit(state, target_f, epochs=1, verbose=0)
        
        # Réduire epsilon pour diminuer l'exploration au fil du temps
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        """Charge les poids du modèle"""
        self.model.load_weights(name)
    
    def save(self, name):
        """Sauvegarde les poids du modèle"""
        self.model.save_weights(name)

class TicTacToeEnv:
    """Environnement Tic Tac Toe pour l'entraînement de l'agent DRL"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Réinitialise l'environnement"""
        self.board = np.zeros((3, 3), dtype=int)
        self.current_player = 1  # 1=X (agent), 2=O (adversaire)
        self.done = False
        self.winner = None
        return self._get_state()
    
    def _get_state(self):
        """Convertit la grille en représentation d'état pour le réseau de neurones"""
        # Créer une représentation à 3 canaux: vide, X, O
        state = np.zeros((*self.board.shape, 3))
        
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    state[i, j, 0] = 1  # Case vide
                elif self.board[i, j] == 1:
                    state[i, j, 1] = 1  # X
                else:
                    state[i, j, 2] = 1  # O
        
        return np.expand_dims(state, axis=0)  # Ajouter dimension de batch
    
    def step(self, action):
        """Effectue une action et retourne le nouvel état, la récompense et si la partie est terminée"""
        # Convertir l'action (0-8) en coordonnées (i, j)
        i, j = action // 3, action % 3
        
        # Vérifier si l'action est valide
        if self.board[i, j] != 0 or self.done:
            return self._get_state(), -10, self.done, {}  # Pénalité pour action invalide
        
        # Effectuer l'action
        self.board[i, j] = self.current_player
        
        # Vérifier s'il y a un gagnant
        if self._check_winner():
            self.done = True
            self.winner = self.current_player
            reward = 1.0 if self.current_player == 1 else -1.0
            return self._get_state(), reward, self.done, {}
        
        # Vérifier s'il y a match nul
        if np.all(self.board != 0):
            self.done = True
            reward = 0.5  # Récompense modérée pour un match nul
            return self._get_state(), reward, self.done, {}
        
        # Passer au joueur suivant
        self.current_player = 3 - self.current_player  # Alterne entre 1 et 2
        
        # Faire jouer l'adversaire (stratégie aléatoire pour l'entraînement)
        if self.current_player == 2 and not self.done:
            valid_actions = self.get_valid_actions()
            if valid_actions:
                opponent_action = random.choice(valid_actions)
                i, j = opponent_action // 3, opponent_action % 3
                self.board[i, j] = self.current_player
                
                # Vérifier si l'adversaire a gagné
                if self._check_winner():
                    self.done = True
                    self.winner = self.current_player
                    return self._get_state(), -1.0, self.done, {}  # Pénalité pour défaite
                
                # Vérifier s'il y a match nul
                if np.all(self.board != 0):
                    self.done = True
                    return self._get_state(), 0.5, self.done, {}  # Récompense modérée pour un match nul
                
                # Revenir à l'agent
                self.current_player = 3 - self.current_player
        
        return self._get_state(), 0.1, self.done, {}  # Petite récompense pour action valide
    
    def _check_winner(self):
        """Vérifie s'il y a un gagnant"""
        # Vérifier les lignes
        for i in range(3):
            if self.board[i, 0] == self.board[i, 1] == self.board[i, 2] != 0:
                return True
        
        # Vérifier les colonnes
        for j in range(3):
            if self.board[0, j] == self.board[1, j] == self.board[2, j] != 0:
                return True
        
        # Vérifier les diagonales
        if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] != 0:
            return True
        if self.board[0, 2] == self.board[1, 1] == self.board[2, 0] != 0:
            return True
        
        return False
    
    def get_valid_actions(self):
        """Retourne la liste des actions valides (cases vides)"""
        valid_actions = []
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:
                    valid_actions.append(i * 3 + j)
        return valid_actions
    
    def render(self):
        """Affiche l'état actuel de la grille"""
        symbols = [' ', 'X', 'O']
        print("-" * 13)
        for i in range(3):
            row = "| "
            for j in range(3):
                row += symbols[self.board[i, j]] + " | "
            print(row)
            print("-" * 13)

def train_agent(episodes=1000, batch_size=32, save_path='drl_agent_model.h5'):
    """Entraîne l'agent DRL sur un certain nombre d'épisodes"""
    env = TicTacToeEnv()
    agent = DRLAgent()
    
    # Statistiques d'entraînement
    wins = 0
    losses = 0
    draws = 0
    
    for e in range(episodes):
        state = env.reset()
        total_reward = 0
        
        while True:
            valid_actions = env.get_valid_actions()
            if not valid_actions:
                break
                
            action = agent.act(state, valid_actions)
            next_state, reward, done, _ = env.step(action)
            total_reward += reward
            
            agent.remember(state, action, reward, next_state, done)
            state = next_state
            
            if done:
                if env.winner == 1:
                    wins += 1
                elif env.winner == 2:
                    losses += 1
                else:
                    draws += 1
                
                if e % 10 == 0:
                    logger.info(f"Episode: {e}/{episodes}, Reward: {total_reward}, Epsilon: {agent.epsilon:.4f}")
                    logger.info(f"Stats - Wins: {wins}, Losses: {losses}, Draws: {draws}")
                
                break
        
        # Entraîner l'agent sur un mini-batch d'expériences
        if len(agent.memory) > batch_size:
            agent.replay(batch_size)
        
        # Sauvegarder le modèle périodiquement
        if e % 100 == 0:
            agent.save(save_path)
    
    # Sauvegarder le modèle final
    agent.save(save_path)
    logger.info(f"Entraînement terminé - Wins: {wins}, Losses: {losses}, Draws: {draws}")
    return agent

def integrate_with_server(agent, board, player_symbol):
    """Intègre l'agent DRL avec le serveur de jeu"""
    # Convertir la grille du serveur en état pour l'agent
    state = np.zeros((3, 3, 3))
    
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                state[i, j, 0] = 1  # Case vide
            elif board[i][j] == 1:
                state[i, j, 1] = 1  # X
            else:
                state[i, j, 2] = 1  # O
    
    state = np.expand_dims(state, axis=0)  # Ajouter dimension de batch
    
    # Déterminer les actions valides
    valid_actions = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                valid_actions.append(i * 3 + j)
    
    # Obtenir l'action de l'agent
    if valid_actions:
        action = agent.act(state, valid_actions)
        row, col = action // 3, action % 3
        return row, col
    
    return None, None

if __name__ == "__main__":
    # Entraîner l'agent
    logger.info("Début de l'entraînement de l'agent DRL...")
    agent = train_agent(episodes=1000)
    logger.info("Entraînement terminé!")
    
    # Test de l'agent
    env = TicTacToeEnv()
    state = env.reset()
    env.render()
    
    while not env.done:
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            break
            
        action = agent.act(state, valid_actions)
        state, reward, done, _ = env.step(action)
        
        print(f"Action: {action}, Reward: {reward}")
        env.render()
