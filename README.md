# Jeu Tic Tac Toe en Ligne avec Agent DRL

Ce projet implémente un jeu de Tic Tac Toe (Morpion) en ligne avec une architecture client-serveur et un agent d'intelligence artificielle basé sur le Deep Reinforcement Learning (DRL). Le projet a été développé dans le cadre du cours Fondement des Réseaux à l'École Supérieure d'Économie Numérique, Université de la Manouba.

## Fonctionnalités

- Jeu de Tic Tac Toe jouable en ligne
- Architecture client-serveur avec communication asynchrone
- Interface graphique utilisateur avec Tkinter
- Agent d'intelligence artificielle utilisant le Deep Reinforcement Learning
- Support pour les modes de jeu suivants :
  - Joueur humain vs Joueur humain
  - Joueur humain vs IA

## Architecture du Système

Le système est composé de trois composants principaux :

1. **Serveur de jeu** : Gère la logique du jeu, la communication entre les joueurs et l'état des parties
2. **Client de jeu** : Interface utilisateur permettant aux joueurs d'interagir avec le jeu
3. **Agent DRL** : Intelligence artificielle basée sur le Deep Reinforcement Learning

### Diagramme d'architecture

```
+----------------+       +----------------+       +----------------+
|                |       |                |       |                |
|  Client 1      |<----->|  Serveur       |<----->|  Client 2      |
|  (Joueur 1)    |       |  - État du jeu |       |  (Joueur 2     |
|                |       |  - Validation  |       |  ou Agent DRL) |
+----------------+       |  - Coordination|       +----------------+
                         |                |
                         +-------^--------+
                                 |
                         +-------v--------+
                         |                |
                         |  Agent DRL     |
                         |  (intégré au   |
                         |   serveur)     |
                         |                |
                         +----------------+
```

## Prérequis

- Python 3.10 ou supérieur
- Bibliothèques Python :
  - socket
  - asyncio
  - tkinter
  - tensorflow
  - numpy

## Installation

1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/votre-nom/tic-tac-toe-drl.git
   cd tic-tac-toe-drl
   ```

2. Installez les dépendances requises :
   ```bash
   pip install tensorflow numpy
   ```

## Utilisation

### Démarrer le serveur

1. Ouvrez un terminal et naviguez vers le répertoire du projet
2. Exécutez le serveur :
   ```bash
   python server.py
   ```
   Le serveur démarrera par défaut sur l'adresse 0.0.0.0 et le port 8888.

### Démarrer le client

1. Ouvrez un nouveau terminal et naviguez vers le répertoire du projet
2. Exécutez le client :
   ```bash
   python client.py
   ```
3. Dans la boîte de dialogue, entrez l'adresse du serveur (par défaut : localhost) et le port (par défaut : 8888)
4. Entrez votre nom de joueur lorsque demandé

### Jouer au jeu

1. Une fois connecté, vous pouvez choisir de démarrer une nouvelle partie :
   - Contre un autre joueur humain (en attente d'un adversaire)
   - Contre l'IA

2. Pendant le jeu :
   - Cliquez sur une case pour placer votre symbole (X ou O)
   - Attendez votre tour lorsque c'est au tour de l'adversaire
   - Le jeu se termine lorsqu'un joueur aligne trois symboles ou lorsque la grille est pleine (match nul)

## Structure du Code

- `server.py` : Implémentation du serveur de jeu avec asyncio et sockets
- `client.py` : Client de jeu avec interface Tkinter
- `drl_agent.py` : Agent d'intelligence artificielle utilisant TensorFlow
- `test_tic_tac_toe.py` : Tests unitaires et d'intégration

### Protocole de Communication

La communication entre le client et le serveur utilise un protocole basé sur JSON. Les principaux types de messages sont :

#### Messages du client vers le serveur :
- `CONNECT` : Demande de connexion au serveur
- `PLAY` : Envoi d'un coup
- `NEW_GAME` : Demande de nouvelle partie
- `DISCONNECT` : Notification de déconnexion

#### Messages du serveur vers le client :
- `GAME_STATE` : État actuel du jeu
- `MOVE_RESULT` : Résultat d'un coup
- `GAME_OVER` : Fin de partie
- `ERROR` : Message d'erreur

## Agent DRL

L'agent d'intelligence artificielle utilise le Deep Reinforcement Learning pour apprendre à jouer au Tic Tac Toe de manière optimale. L'implémentation utilise :

- Un réseau de neurones convolutif pour extraire des caractéristiques spatiales
- L'algorithme Deep Q-Learning avec mémoire de replay
- Un système de récompenses pour encourager les victoires et pénaliser les défaites

L'agent est entraîné en jouant contre lui-même, ce qui lui permet d'améliorer sa stratégie au fil du temps.

## Tests

Le projet inclut une suite de tests unitaires et d'intégration pour valider le bon fonctionnement de tous les composants :

- Tests de la logique du jeu
- Tests de l'agent DRL
- Tests d'intégration pour la communication réseau

Pour exécuter les tests :
```bash
python test_tic_tac_toe.py
```

## Contribution

Les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request


## Auteurs
Armen Aoun
Nour el houda Hammemi

## Remerciements

- École Supérieure d'Économie Numérique, Université de la Manouba
- Prof. Amine Dhraief pour l'encadrement du projet
