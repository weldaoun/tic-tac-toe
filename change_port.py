#!/usr/bin/env python3
"""
Script de modification du port pour le serveur et client Tic Tac Toe
Ce script modifie les fichiers server.py et client.py pour utiliser un port différent
"""

import os
import re
import sys

def modify_port(server_file, client_file, new_port):
    """Modifie le port dans les fichiers serveur et client"""
    # Vérifier que les fichiers existent
    if not os.path.exists(server_file):
        print(f"Erreur: Le fichier serveur '{server_file}' n'existe pas.")
        return False
    
    if not os.path.exists(client_file):
        print(f"Erreur: Le fichier client '{client_file}' n'existe pas.")
        return False
    
    # Lire le contenu du fichier serveur
    with open(server_file, 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    # Lire le contenu du fichier client
    with open(client_file, 'r', encoding='utf-8') as f:
        client_content = f.read()
    
    # Modifier le port dans le fichier serveur
    server_pattern = r'port=(\d+)'
    server_content_modified = re.sub(server_pattern, f'port={new_port}', server_content)
    
    # Modifier le port par défaut dans le fichier client
    client_pattern = r'initialvalue="(\d+)"'
    client_content_modified = re.sub(client_pattern, f'initialvalue="{new_port}"', client_content)
    
    # Vérifier si des modifications ont été effectuées
    if server_content == server_content_modified and client_content == client_content_modified:
        print("Aucune modification n'a été effectuée. Les fichiers ne contiennent peut-être pas les motifs attendus.")
        return False
    
    # Sauvegarder les fichiers originaux
    with open(f"{server_file}.bak", 'w', encoding='utf-8') as f:
        f.write(server_content)
    
    with open(f"{client_file}.bak", 'w', encoding='utf-8') as f:
        f.write(client_content)
    
    # Écrire les fichiers modifiés
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(server_content_modified)
    
    with open(client_file, 'w', encoding='utf-8') as f:
        f.write(client_content_modified)
    
    print(f"Les fichiers ont été modifiés avec succès pour utiliser le port {new_port}.")
    print(f"Des sauvegardes ont été créées: {server_file}.bak et {client_file}.bak")
    return True

def main():
    """Fonction principale"""
    # Vérifier les arguments
    if len(sys.argv) != 2:
        print("Usage: python change_port.py <nouveau_port>")
        print("Exemple: python change_port.py 5000")
        return
    
    try:
        new_port = int(sys.argv[1])
        if new_port < 1024 or new_port > 65535:
            print("Erreur: Le port doit être compris entre 1024 et 65535.")
            return
    except ValueError:
        print("Erreur: Le port doit être un nombre entier.")
        return
    
    # Chemins des fichiers
    server_file = "server.py"
    client_file = "client.py"
    
    # Modifier les fichiers
    if modify_port(server_file, client_file, new_port):
        print("\nInstructions:")
        print(f"1. Démarrez le serveur: python {server_file}")
        print(f"2. Démarrez le client: python {client_file}")
        print(f"3. Utilisez le port {new_port} lorsque demandé")
        print("\nSi vous souhaitez revenir aux fichiers originaux, renommez les fichiers .bak")

if __name__ == "__main__":
    main()
