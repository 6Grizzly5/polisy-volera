# Polisy sy Volera V1

Prototype jouable sur deux PC du même réseau local.

## Lancement

```powershell
python -m pip install -r requirements.txt
python -m client.main
```

## Partie LAN

PC 1 :
1. `Créer une partie`
2. Choisir `Police` ou `Voleur`
3. L'écran affiche l'IP LAN et le port. Donner ces informations au deuxième joueur.

PC 2 :
1. `Rejoindre une partie`
2. Saisir l'IP du PC 1
3. Choisir l'autre rôle.

Port TCP : `5050`.

## Règles V1

- 13 positions.
- Voleur : position 0 au départ.
- Police : positions 4, 1 et 8.
- Le voleur doit quitter le centre puis y revenir pour gagner.
- La police gagne si le voleur n'a plus aucun déplacement légal.

## Architecture

`common/` = moteur partagé  
`client/` = PyQt6 + réseau  
`server/` = serveur TCP arbitre

Le serveur est lancé automatiquement par le PC qui crée la partie.
