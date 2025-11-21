# 📘 **RAPPORT TECHNIQUE — NVIDIA EARNINGS CALL RAG APP**

## 1. 🧠 **Compréhension du Problème**

Le défi consiste à construire une application capable de :

* **creer un chatbot ingérer avec des transcripts d'Earnings Calls NVIDIA**
* **filtrer, chunker, vectoriser et stocker ces informations dans une base vectorielle**
* **fournir une interface permettant de poser des questions**
* **retrouver rapidement des passages pertinents via un retrieve-and-generate (RAG)**
* **servir des réponses fiables et contextualisées**
* **fonctionner dans une architecture Dockerisée complète**
* **être simple à installer et tester localement**

L'utilisateur final doit pouvoir **poser une question en langage naturel** et recevoir une **réponse synthétique + les sources** issues des transcripts.

L’objectif général :

> **Construire un système de Q&A performant, modulaire, reproductible et scalable en peu de temps.**

---

## 2. 🏗️ **Design et Choix Techniques**

### 2.1. Choix du modèle d’embedding

J'ai choisi :

> **BAAI/bge-base-en-v1.5**
> via SentenceTransformers (ou une alternative ONNX plus rapide) a des fin de demonstration de competences (du local load) dans le cadre du test. 
> utilisation via Hugging face api plus simple (sur le model du call LLM)

🎯 Pourquoi ce modèle ?

* petite taille
* excellent score sur MTEB (benchmark SOTA)
* très adapté aux tasks de **retrieval et semantic search**
* embeddings très cohérents pour des documents business / earnings calls
* stable et mature

*(Si version ONNX : modèle plus rapide, pas besoin de PyTorch → idéal Docker slim.)*
*(Si plus gros modèle, passer via API call plutôt que local load)
---

### 2.2. Choix du Vector Store : **ChromaDB**

> **Chroma** est léger, rapide, open-source, easy-to-use, parfait pour un prototype et suffisamment robuste pour de la prod.

Pourquoi Chroma ?

* facile à containeriser
* API HTTP simple
* CRUD sur embeddings rapide
* support natif cosine similarity
* stockage persistant
* intègre parfaitement avec Python

---

### 2.3. Stratégie de chunking

* Chunk **500 tokens**, overlap 100

Pourquoi ce chunking ?

* chunks trop longs = bruit
* chunks trop courts = perte de contexte
* 500 tokens → idéal earnings calls (block logique = réponse d'un speaker)

---

### 2.4. Choix de l’architecture logicielle


#### **1. One-Time manual d’ingestion (job one-shot)**

* charge les JSONL et chunks
* compute embeddings
* insère dans Chroma

Architecture Microservices, composée de :

#### **2. Backend (FastAPI)**

* expose `/rag`
* récupère embeddings pertinents depuis Chroma - approche local loading
* prépare un prompt pour HuggingFace LLM - approche API Call
* génère la réponse

#### **3. Frontend (React/Vite)**

* interface minimaliste pour poser une question
* affiche réponse dans un chat

#### **4. Frontend (Nginx)**

* reverse proxy
* gère le routing
* sert le frontend
* protège le backend

#### **5. Vector DB — Chroma (container)**

* indépendant
* persistant
* évite d'exploser le backend si Chroma reload
* scalable horizontalement
* Single responsability

---

## 3. 📊 **Data & Preprocessing**

* Earnings Calls récupérés en fichiers `.jsonl`
* Nettoyage :
  * restructuration / epuration
  * découpe en blocs par speaker
* Tokenisation + chunking
* Génération d’un **fichier `data/nvidia_chunks.jsonl`** pour ingestion dans chroma

---

## 4. 🧹 **Vectorisation** - choix du local loading

  NB :  choix du local loading volontaire pour la demo
* modèle : `BAAI/bge-base-en-v1.5`
* embeddings normalisés (`L2 norm`)
* stockage dans Chroma via l’API HTTP
* structure d’index : metric = cosine

---

## 5. 🗄️ **Vector Store : Chroma**

Chroma stocke :

* `ids`
* `transcript`
* `metadatas`
* `embeddings`

Pourquoi un container séparé ?

* isolation mémoire
* stabilité
* évite de polluer le backend
* reboot sans perte de données
* respect du principe "1 service = 1 responsabilité"

---

## 6. 🏗️ **Architecture de la solution**

### 📌 Vue d’ensemble (diagramme ASCII)

```
                       +----------------------+
                       |      Frontend        |
                       |       React          |
                       +----------+-----------+
                                  |
                                  v
                         +--------+--------+
                         |     NGINX       |
                         |   Reverse Proxy |
                         +--------+--------+
                                  |
                                  v
                         +--------+--------+
                         |     FastAPI     |
                         |   Backend API   |
                         +--------+--------+
             retrieve →           |
                                  v
                        +---------+---------+
                        |     Chroma DB     |
                        |   Vector Store    |
                        +-------------------+

             one-shot ingestion job:
                        +-------------------+
                        |   ingest (job)    |
                        | setup_db.py       |
                        +-------------------+
```

---

## 7. ⚙️ **Backend Description**

### Endpoints

#### `POST`

- `/`  
  Health check – retourne : `{"answer": "test ok !"}`

- `/dummy`  
  Retourne tel quel l’input utilisateur (pour valider la communication frontend ↔ backend)

- `/llm`  
  Appelle le LLM **sans** RAG et retourne une réponse générée.

- `/rag`  
  Implémente le RAG tel que spécifié (retriever + contexte + appel LLM).

---

## 8. 🎨 **Frontend Description**

* UI simple en React
* trois composents principaux ChatBubble.jsx, InputBox.jsx, Messages.jsx
* responsive, extensilble au texte de differente taille


---

## 9. 🧭 **Pourquoi NGINX ?**

* gère le **routing** (frontend ↔ backend)
* sert le build React en mode performant
* produit une architecture plus réaliste
* uniformise la app entry point 
* localhost reverse proxy
* permet SSL plus tard

---

## 10. 🧱 **Pourquoi un container dédié pour Chroma ?**

* éviter d’installer tout Chroma dans le backend
* isolation mémoire + CPU
* possibilité de scaling indépendant
* permet ingestion job séparé
* pratique pour la persistance via volumes
* separation of concernes

---

## 11. 🧪 **Setup & Run Instructions**

### 1. Clone

```
git clone https://github.com/vincentcommere/mila-ai-dev-interview.git
cd mila-ai-dev-interview 
```

### 2. Ajouter `./backend/.env` votre hugginface API_KEY pour inference endpoints

[https://huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)


```
API_KEY=xxxxx
```

### 3. Build/Run la vector DB 

```
make chroma-nocache
```

### 4. executer le one-time ingest  (Mac only)

```
make db_setup
```

### 5. Build/Run backend

```
make backend-nocache
```

### 6. Build/Run frontend

```
make frontend-nocache
```

### 7. Ouvrir le frontend

[http://localhost:80](http://localhost:80)


### 8. Après la première requête, prévoir un délai de quelques minutes pour permettre l’initialisation complète du retriever (chargement de la collection et du modèle d’embeddings).
```
backend   | 🔌 Initializing Retriever...
backend   | 📚 Retriever loaded collection: nvidia_earnings_calls
```

<p align="center">
  <img src="img/Screenshot 2025-11-20-4.png" width="500"/>
</p>


### 9. arreter tout

```
make down
```

---

## 12. 💬 **Exemples de questions**

```
● “What did Nvidia report about revenue last quarter?”
● “Summarize Nvidia’s Q2 2024 guidance.”
● “List key risks mentioned by Nvidia in Q4 FY23.”
```
<p align="center">
  <img src="img/Screenshot 2025-11-19-1.png" width="450"/>
</p>
<p align="center">
  <img src="img/Screenshot 2025-11-19-2.png" width="450"/>
</p>
<p align="center">
  <img src="img/Screenshot 2025-11-19-3.png" width="450"/>
</p>
---

## 13. ⚖️ **Trade-offs**

* J’ai choisi Chroma plutôt pour simplifier le Docker networking.
* Chunking simple 500 tokens : ok pour un prototype, mais améliorable.
* Pas d’auth backend — trop long pour un proof-of-concept.
* Pas de citation exacte des paragraphes (option possible).


---

## 14. 🤖 **Usage de GenAI dans le développement**

* J’utilise ChatGPT comme un accélérateur dans mon processus de développement, tout en conservant une maîtrise complète du code produit.
* Je ne génère jamais de code que je ne comprends pas ou que je ne suis pas capable d’adapter moi-même.

* Je n’utilise pas d’outils de génération automatique tels que Cursor ou GitHub Copilot.
* Lorsque je demande des suggestions d’amélioration, je les évalue systématiquement et je décide moi-même de leur pertinence avant de les intégrer.
---

## 15. 🚀 **Suggestions de futurs travaux**


🔧 Amélioration des performances LLM

* Optimisation du modèle d’embeddings et passage de celui-ci en API call
* Exploration et amélioration des méthodes de recherche RAG
* Ajustement des stratégies de découpage (chunking)
* Intégration d’un modèle de reranking (ex. bge-reranker)
* Utilisation d’un modèle d’embedding plus léger et plus rapide

🏗️ Optimisation de l’architecture

* Réduction de la taille des images Docker (par ex. utilisation d’images Alpine)
* Optimisation de certaines librairies lourdes (ex. Sentence Transformers avec Torch)
* Mise en place ou optimisation du Vector DB
* Optimisation de l’initialisation du retriever au démarrage (actuellement plusieurs minutes), afin d’éviter les erreurs 504 Gateway Timeout lors des premières requêtes

🧑‍💻 Améliorations logicielles

* Amélioration du frontend
* Implémentation ou optimisation de l’authentification
* Ajout de tests unitaires
* Ajout de tests d’intégration
* Ajout ou amélioration du linting (Black, Flake8) et du typing
---
