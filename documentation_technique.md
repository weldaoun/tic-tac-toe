# Documentation Technique - Jeu Tic Tac Toe en Ligne avec Agent DRL

## Architecture Réseau

### Vue d'ensemble

L'architecture réseau du jeu Tic Tac Toe en ligne est basée sur un modèle client-serveur utilisant les sockets TCP/IP et la programmation asynchrone avec asyncio. Cette architecture permet une communication bidirectionnelle en temps réel entre les clients et le serveur.

### Composants de l'architecture réseau

#### Serveur

Le serveur est le composant central qui :
- Gère les connexions des clients
- Maintient l'état des parties en cours
- Valide les coups des joueurs
- Coordonne les parties entre joueurs ou entre un joueur et l'agent DRL
- Notifie les clients des changements d'état du jeu

**Implémentation technique :**
- Utilisation d'`asyncio.start_server()` pour créer un serveur asynchrone
- Gestion des connexions avec `asyncio.StreamReader` et `asyncio.StreamWriter`
- Traitement concurrent des clients avec des coroutines asyncio
- Utilisation de structures de données thread-safe pour l'état du jeu

#### Client

Le client est l'interface utilisateur qui :
- Se connecte au serveur
- Affiche l'état du jeu
- Capture les actions de l'utilisateur
- Envoie les coups au serveur
- Affiche les résultats et notifications

**Implémentation technique :**
- Interface graphique avec Tkinter
- Communication réseau avec `socket` standard
- Gestion des événements asynchrones avec des threads

### Protocole de communication

La communication entre le client et le serveur utilise un protocole basé sur JSON. Chaque message est un objet JSON avec un champ `type` qui définit le type de message et des champs supplémentaires spécifiques au type.

#### Types de messages du client vers le serveur

1. **CONNECT**
   ```json
   {
     "type": "CONNECT",
     "player_name": "Nom du joueur"
   }
   ```

2. **NEW_GAME**
   ```json
   {
     "type": "NEW_GAME",
     "game_type": "HUMAN_VS_HUMAN" | "HUMAN_VS_AI"
   }
   ```

3. **PLAY**
   ```json
   {
     "type": "PLAY",
     "game_id": "identifiant_de_la_partie",
     "row": 0-2,
     "col": 0-2
   }
   ```

4. **DISCONNECT**
   ```json
   {
     "type": "DISCONNECT"
   }
   ```

#### Types de messages du serveur vers le client

1. **CONNECT_RESPONSE**
   ```json
   {
     "type": "CONNECT_RESPONSE",
     "status": "SUCCESS" | "ERROR",
     "client_id": "identifiant_client",
     "message": "Message optionnel"
   }
   ```

2. **GAME_CREATED**
   ```json
   {
     "type": "GAME_CREATED",
     "game_id": "identifiant_de_la_partie",
     "player_symbol": 1 | 2,
     "opponent_name": "Nom de l'adversaire" | "AI"
   }
   ```

3. **GAME_STATE**
   ```json
   {
     "type": "GAME_STATE",
     "game_id": "identifiant_de_la_partie",
     "board": [[0,0,0],[0,0,0],[0,0,0]],
     "current_player": 1 | 2,
     "game_over": true | false,
     "winner": null | 1 | 2,
     "winning_line": [[row1, col1], [row2, col2], [row3, col3]] | null
   }
   ```

4. **MOVE_RESULT**
   ```json
   {
     "type": "MOVE_RESULT",
     "status": "SUCCESS" | "ERROR",
     "message": "Message optionnel"
   }
   ```

5. **GAME_OVER**
   ```json
   {
     "type": "GAME_OVER",
     "game_id": "identifiant_de_la_partie",
     "winner": null | 1 | 2,
     "winning_line": [[row1, col1], [row2, col2], [row3, col3]] | null
   }
   ```

6. **ERROR**
   ```json
   {
     "type": "ERROR",
     "message": "Description de l'erreur"
   }
   ```

### Gestion des connexions

1. **Établissement de la connexion**
   - Le client se connecte au serveur via TCP/IP
   - Le client envoie un message CONNECT avec son nom
   - Le serveur répond avec un message CONNECT_RESPONSE contenant un identifiant unique

2. **Maintien de la connexion**
   - Le serveur garde une liste des clients connectés
   - Chaque client est associé à un objet StreamWriter pour l'envoi de messages

3. **Gestion des déconnexions**
   - Détection des déconnexions par des exceptions de socket
   - Nettoyage des ressources associées au client
   - Notification des adversaires en cas de déconnexion pendant une partie

## Modèle DRL (Deep Reinforcement Learning)

### Vue d'ensemble

L'agent DRL implémenté utilise l'apprentissage par renforcement profond pour apprendre à jouer au Tic Tac Toe de manière optimale. L'agent est basé sur l'algorithme Deep Q-Learning (DQN) avec mémoire de replay.

### Composants du modèle DRL

#### Environnement (TicTacToeEnv)

L'environnement modélise le jeu de Tic Tac Toe et fournit :
- Un état initial (grille vide)
- Une fonction de transition (application d'un coup)
- Une fonction de récompense
- Une détection de fin de partie

**Implémentation technique :**
- Représentation de l'état sous forme de tableau NumPy 3x3
- Encodage one-hot pour les entrées du réseau neuronal
- Interface similaire à OpenAI Gym

#### Agent DRL

L'agent DRL est composé de :
- Un réseau de neurones pour approximer la fonction Q
- Une mémoire de replay pour stocker les expériences
- Une politique epsilon-greedy pour l'exploration/exploitation
- Un mécanisme d'apprentissage par lots

**Architecture du réseau neuronal :**
- Couche d'entrée : 3x3x3 (état du jeu encodé en one-hot)
- Couches cachées : 
  - Couche convolutive 2D (32 filtres, noyau 2x2)
  - Couche de pooling max
  - Couche dense (64 neurones)
- Couche de sortie : 9 neurones (un pour chaque case)

**Hyperparamètres :**
- Taux d'apprentissage : 0.001
- Facteur de remise (gamma) : 0.95
- Epsilon initial : 1.0
- Epsilon minimal : 0.1
- Décroissance d'epsilon : 0.995
- Taille de la mémoire de replay : 10000
- Taille des lots d'apprentissage : 64

### Processus d'entraînement

1. **Initialisation**
   - Création de l'environnement
   - Initialisation du réseau neuronal
   - Initialisation de la mémoire de replay vide

2. **Boucle d'entraînement**
   - Pour chaque épisode :
     - Réinitialisation de l'environnement
     - Pour chaque étape de l'épisode :
       - Sélection d'une action selon la politique epsilon-greedy
       - Exécution de l'action et observation de la récompense et du nouvel état
       - Stockage de l'expérience dans la mémoire de replay
       - Apprentissage sur un lot d'expériences aléatoires
     - Mise à jour d'epsilon

3. **Système de récompenses**
   - +1.0 pour une victoire
   - -1.0 pour une défaite
   - -0.1 pour un coup invalide
   - 0.0 pour un match nul
   - -0.01 pour chaque coup (pour encourager des parties rapides)

### Intégration avec le serveur

L'agent DRL est intégré au serveur de jeu et peut être utilisé comme adversaire pour les joueurs humains. Lorsqu'un joueur choisit de jouer contre l'IA :

1. Le serveur crée une instance de l'agent DRL
2. À chaque tour de l'IA, le serveur :
   - Convertit l'état du jeu au format attendu par l'agent
   - Demande à l'agent de choisir une action
   - Applique l'action choisie à l'état du jeu
   - Notifie le client humain du coup joué par l'IA

## Logique du jeu

### Représentation de l'état du jeu

L'état du jeu est représenté par :
- Une grille 3x3 où chaque case peut contenir :
  - 0 : case vide
  - 1 : symbole du joueur 1 (X)
  - 2 : symbole du joueur 2 (O)
- Le joueur courant (1 ou 2)
- Un indicateur de fin de partie
- Le gagnant (null, 1, ou 2)
- La ligne gagnante (trois cases alignées)

### Règles du jeu

1. Les joueurs jouent à tour de rôle, en commençant par le joueur 1 (X)
2. Un joueur ne peut jouer que sur une case vide
3. Le premier joueur à aligner trois de ses symboles (horizontalement, verticalement ou en diagonale) gagne la partie
4. Si toutes les cases sont remplies sans qu'aucun joueur n'ait gagné, la partie est déclarée nulle

### Validation des coups

Chaque coup est validé par le serveur selon les règles suivantes :
- Le coup doit être joué par le joueur dont c'est le tour
- La case ciblée doit être vide
- La partie ne doit pas être déjà terminée

### Détection de fin de partie

Après chaque coup, le serveur vérifie si la partie est terminée en :
- Vérifiant s'il y a trois symboles identiques alignés
- Vérifiant si toutes les cases sont remplies (match nul)

## Interface utilisateur

### Interface graphique

L'interface graphique est implémentée avec Tkinter et comprend :
- Une grille 3x3 pour le jeu
- Des indicateurs pour le joueur courant et l'état de la partie
- Des boutons pour les actions (nouvelle partie, quitter)
- Une zone de messages pour les notifications

### Interaction utilisateur

Les interactions utilisateur sont gérées par :
- Des événements de clic pour jouer un coup
- Des boutons pour les actions principales
- Des boîtes de dialogue pour les entrées utilisateur (connexion, choix de partie)

### Affichage de l'état du jeu

L'interface met à jour l'affichage en fonction des messages reçus du serveur :
- Mise à jour de la grille avec les symboles des joueurs
- Mise en évidence de la ligne gagnante
- Affichage des messages de statut (tour du joueur, victoire, défaite, match nul)
- Désactivation de la grille lorsque ce n'est pas le tour du joueur ou que la partie est terminée
