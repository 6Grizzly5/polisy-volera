# Polisy sy Volera

Jeu de plateau réalisé avec Python et PyQt6. Il propose une partie locale contre le bot et une partie en réseau local (LAN) entre deux ordinateurs.

## Prérequis

- Windows et Python 3.10 ou plus récent.
- Les deux ordinateurs doivent être connectés au même réseau local (par exemple le même Wi-Fi).
- Pour jouer en LAN, le PC qui héberge doit être joignable depuis l'autre PC sur le port TCP `5050`.

## Installation ou mise à jour

Sur **chaque PC**, récupérer la dernière version du dépôt, puis ouvrir PowerShell dans le dossier du projet. Pour un premier téléchargement, utiliser `git clone <URL_DU_DEPOT>` puis entrer dans le dossier créé. Pour mettre à jour un clone existant :

```powershell
git pull
```

Créer l'environnement et installer les dépendances (à refaire après une mise à jour si `requirements.txt` a changé) :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell bloque l'activation de l'environnement, on peut lancer directement son Python sans l'activer :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Lancer le jeu

Depuis la racine du dépôt, sur chaque PC :

```powershell
python run.py
```

Ou, si l'environnement n'a pas été activé :

```powershell
.\.venv\Scripts\python.exe run.py
```

## Jouer en LAN à deux PC

1. Vérifier que les deux PC sont sur le même réseau et que chacun a installé les mêmes fichiers et dépendances.
2. Sur le **PC hôte**, choisir le rôle souhaité dans le menu, puis cliquer sur **Créer une partie LAN**. Ce PC joue aussi : il n'est pas nécessaire de lancer une commande serveur séparée.
3. La fenêtre de partie de l'hôte affiche l'adresse IPv4 LAN et le port `5050`. Communiquer cette adresse à l'autre joueur. Ne pas utiliser `127.0.0.1` : cette adresse ne fonctionne que sur le PC lui-même.
4. Sur le **PC invité**, choisir le rôle opposé à celui de l'hôte dans la liste déroulante, puis cliquer sur **Rejoindre une partie LAN** et saisir l'adresse IPv4 affichée par l'hôte.
5. La partie démarre dès que les deux rôles sont connectés. Les coups sont vérifiés par le serveur et l'état du plateau est synchronisé entre les deux joueurs.

Le serveur écoute sur toutes les interfaces réseau du PC hôte, sur TCP `5050`. Le PC invité n'a pas besoin d'ouvrir de port entrant.

### Pare-feu Windows

Au premier lancement, Windows peut demander l'autorisation réseau pour Python. Autoriser l'accès sur les **réseaux privés** sur le PC hôte. Si la demande a été refusée ou n'apparaît pas, autoriser Python ou une règle entrante TCP sur le port `5050` dans le Pare-feu Windows. Ne pas ouvrir ce port sur Internet ou sur un réseau public.

### Dépannage LAN

- **« Connexion impossible »** : vérifier l'adresse IPv4 saisie, que l'hôte a bien créé une partie, que les deux PC sont sur le même réseau et que le pare-feu autorise TCP `5050`.
- **« Ce rôle est déjà pris »** : l'invité doit choisir l'autre rôle dans le menu, puis retenter la connexion.
- **L'adresse affichée commence par `127.`** : l'hôte n'a pas pu détecter son adresse LAN. Vérifier la connexion réseau et rechercher l'adresse IPv4 du Wi-Fi/Ethernet avec `ipconfig`, puis la communiquer à l'invité.
- **Réseau Wi-Fi d'école, d'hôtel ou invité** : certains points d'accès isolent les appareils entre eux. Utiliser un réseau qui autorise les connexions directes entre les deux PC.
- Si l'adversaire quitte le jeu, recréer une partie sur l'hôte pour rejouer.

## Règles et bot

Le plateau utilise 13 positions reliées selon les lignes dessinées. Un pion ne se déplace que vers une position voisine directement reliée ; il ne peut ni sauter une position ni traverser un pion. Le voleur gagne après avoir quitté le centre puis y être revenu. La police gagne lorsque le voleur n'a plus de déplacement légal.

Le mode **Jouer contre le bot** utilise un Minimax de profondeur 3.
