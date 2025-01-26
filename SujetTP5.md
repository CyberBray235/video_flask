# RT0705 : Gestion d’une vidéothèque

Le but de ce sujet est la gestion d’une vidéothèque.

---

## Modélisation

Nous cherchons à proposer une solution de gestion d’une vidéothèque, c’est-à-dire une collection de films, numériques ou sur format physique.

### 1. Fonctionnalités
Listez l’ensemble des fonctionnalités offertes par le système à un utilisateur.

### 2. Acteurs & schéma général
- Définissez l’ensemble des acteurs présents dans le système, ainsi que leurs rôles et leurs charges.
- Définissez les échanges de données entre les différents acteurs.

### 3. Données du système
Définissez l’ensemble des objets exploités par le système, ainsi que leur constitution et type.

### 4. Modèle d’exécution et échanges
Proposez un modèle d’exécution pour les différentes opérations, ainsi que la description des échanges réalisés et des opérations effectuées à la réception.

---

## Implémentation

Nous souhaitons maintenant plonger cette application dans un modèle WEB de type **3 tiers** :
- **Un tiers client** : un navigateur ;
- **Un tiers présentation** : un site web ;
- **Un tiers d’accès aux données** : une API REST agissant sur un stockage JSON.

L’ensemble des services sera porté par des conteneurs Docker. Les communications entre les services se feront au format JSON.

---

### 1. Architecture générale
- Reprenez la modélisation précédente.
- En prenant en compte les contraintes ci-dessus, proposez une architecture pour votre système en précisant les éléments systèmes et réseau.

### 2. Architecture du tiers données
- Le tiers données sera assuré par une API REST.
- Donnez la hiérarchie de l’architecture des données, ainsi que la description de l’API REST que vous allez utiliser.
- Précisez les opérations implémentées et réalisées.
- Donnez le format JSON de chacune des données présentes dans le système.

### 3. Architecture du tiers de présentation
- Listez l’ensemble des pages et scripts qui composeront le tiers présentation.
- Pour chaque page ou script, donnez les opérations, ainsi que les appels à l’API si nécessaire.

---

## Mise en œuvre

### 1. Mise en place d'éléments de l'infrastructure  
1. Rejoignez le lab **M1RT RT0705 TP** sur la plateforme RemoteLabz.  
2. Installez **VSCode** sur votre machine physique.  
3. Installez le module **Remote Development** de VSCode si nécessaire.  
4. Mettez en place un échange de clé RSA entre la machine physique et la machine virtuelle.  
5. Connectez-vous depuis VSCode à la machine virtuelle.  
6. Vérifiez l'installation des éléments suivants :
   - Docker, Docker Compose ;
   - Git.

7. Créez deux projets VSCode et GIT :
   - **serveur**, qui portera le code du tiers de présentation ;
   - **API**, qui portera le tiers d'accès aux données (API REST + fichier JSON).

---

## Développement

### 1. Création et test des conteneurs Flask  
Créez une image Docker utilisateur contenant les éléments suivants :
- Python 3 ;
- Flask ;
- L'architecture de répertoires nécessaire à l'exécution d'une application Flask. Cette application doit être dans un volume partagé avec l'hôte Docker.

Vous pouvez utiliser l'image de base de votre choix.

#### Tests du conteneur
Développez les éléments suivants pour tester votre conteneur :
- Une page HTML simple ;
- Une page HTML contenant un formulaire et une page de traitement de ce formulaire en Python/Jinja ;
- Une page HTML contenant un template Jinja exploitant des données issues d’un fichier JSON (par exemple, un fichier de vidéothèque).

---

### 2. Création du tiers de données  
En reprenant l’API REST définie précédemment, proposez une implémentation de l’ensemble des différentes fonctions.  
- Toutes les données qui transitent entre le client et le serveur doivent être au format JSON.  
- Exécutez le serveur Flask portant l’API REST dans le conteneur instanciant l’image précédemment créée.

#### Tests
- Testez toutes les fonctions écrites à l’aide d’outils comme **Postman**, **Rested**, un script Python ou des commandes `curl`.

---

### 3. Création du tiers de présentation  
Codez toutes les pages définies dans la première partie. Créez ces différentes pages.  
- Exécutez le serveur Flask portant le serveur web dans le conteneur instanciant l’image précédemment créée.  
- Effectuez une création coordonnée des deux conteneurs.

--- 
