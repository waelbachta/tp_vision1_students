### Sujet
Le sujet qui accompagne ce TP est dans lab\_text.md


### Environnement de travail
Pour faire tourner ce TP, beaucoup de librairies sont indispensables. Afin de bénéficier d'un environement de travail complet, je vous suggère de procéder de la sorte (fonctionnement vérifié pour une ubuntu 20.04 et 22.04) : 

- Installer Docker.

- Aller dans le dossier docker_install et vérifier la présence d'un dossier volume\_tp. 

- Ecrire :
 ```
   sudo docker pull waelbachta/ubuntu_ssh_labs:latest
 ```


Cela vous permet de télécharger une image d'un conteneur docker prête à l'emploi. Vous allez devoir utiliser votre mot de passe personnel.

- Vous lancerez votre conteneur avec une liasion ssh sur le port 220 avec votre machine personnelle.

  ```
  sudo docker run -d --rm --volume="./volume_tp:/home/" -p 220:22 waelbachta/ubuntu_ssh_labs:latest
  ```

- Se connecter avec un ssh X à votre conteneur en écrivant :
  
  ```
  sudo ssh -X -p 220 root@localhost
    ```
 Vous aurez à saisir le mot de passe du conteneur qui est root123

 - Aller dans /home et vérifier qu'il correspond bien à volume\_tp.

 - Accéder au répertoire qui correspond à votre TP.

Vous allez ainsi pouvoir modifier le code sur votre ordinateur personnel et et l'interpréter sur le conteneur.

