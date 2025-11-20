# 📘 **RAPPORT TECHNIQUE — NVIDIA EARNINGS CALL RAG APP**

## 1. 🧠 **Compréhension du Problème**

Le défi consiste à construire une application capable de :

* **ingérer des transcripts d'Earnings Calls NVIDIA**
* **chunker, vectoriser et stocker ces informations dans une base vectorielle**
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

> **BAAI/bge-large-en-v1.5**
> via SentenceTransformers (ou une alternative ONNX plus rapide).

🎯 Pourquoi ce modèle ?

* excellent score sur MTEB (benchmark SOTA)
* très adapté aux tasks de **retrieval et semantic search**
* embeddings très cohérents pour des documents business / earnings calls
* stable et mature

*(Si version ONNX : modèle plus rapide, pas besoin de PyTorch → idéal Docker slim.)*

---

### 2.2. Choix du Vector Store : **ChromaDB**

> **Chroma** est léger, rapide, open-source, easy-to-use, parfait pour un prototype et suffisamment robuste pour de la prod.

Pourquoi Chroma ?

* API HTTP simple
* CRUD sur embeddings rapide
* support natif cosine similarity
* stockage persistant
* facile à containeriser
* intègre parfaitement avec Python

---

### 2.3. Stratégie de chunking

* Chunk **500 tokens**, overlap 100
* Format JSONL avec :

  ```json
  { "id": "...", "text": "...", "metadata": { "year": "...", "quarter": "..." } }
  ```

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

* expose `/query`
* récupère embeddings pertinents depuis Chroma
* prépare un prompt pour HuggingFace LLM
* génère la réponse

#### **3. Frontend (React/Vite)**

* interface minimaliste pour poser une question
* affiche réponse + sources

#### **4. Reverse proxy — Nginx**

* gère le routing
* sert le frontend
* protège le backend
* force CORS & SSL si besoin

#### **5. Vector DB — Chroma container**

* indépendant
* persistant
* évite d'exploser le backend si Chroma reload
* scalable horizontalement

---

## 3. 📊 **Data & Preprocessing**

* Earnings Calls récupérés en fichiers `.txt`
* Nettoyage :

  * suppression timestamps
  * normalisation whitespaces
  * découpe en blocs par speaker
* Tokenisation + chunking
* Génération d’un **fichier `data/nvidia_chunks.jsonl`**

---

## 4. 🧹 **Vectorisation**

* modèle : `BAAI/bge-large-en-v1.5`
* embeddings normalisés (`L2 norm`)
* stockage dans Chroma via l’API HTTP
* structure d’index : HNSW, metric = cosine

---

## 5. 🗄️ **Vector Store : Chroma**

Chroma stocke :

* `ids`
* `documents`
* `metadatas`
* `embeddings`

Accès rapide (O(log n)) via index HNSW.

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

#### `POST /query`

/ # health check return {"answer":"test ok !"}
/dummy # return user input to validation frontend backend comunication
/llm # answer using llm without rag
/rag # implement le rag tel que demande

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

```
API_KEY=xxxxx
```

### 3. Build/Run la vector DB 

```
make chroma-nocache
```

### 4. executer le one-time ingest  (Mac only)

```
cd ingest
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python setup_db.py 
deactivate
cd ..
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


### 8. Patienter quelque minute a lissue de la premiere requete afin que le retriever sinisalise ( load collection, load embeddings models)

```
backend   | 🔌 Initializing Retriever...
backend   | 📚 Retriever loaded collection: nvidia_earnings_calls
```

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

* jai utilise chat gpt, je ne genere pas de code que je ne comprend ou ne metreise pas jutilise lia pour accelerer ce que je veux faire. je nai pas utilise cursor ou co pilot, je demande egalement quels sont els amelioration que je peut faire, puis jaccepte ou nom cell ci 

---

## 15. 🚀 **Suggestions de futurs travaux**


Perfomance LLM
  - embeddings model
  - RAG search methodes
  - chunks methodes
  - intégrer reranking **bge-reranker**
  - model embedding plus leger

Perfomance Architecture
- reduiction du build taille des images peuvent etre reduit a parti dimage alpine
- reduiction du build les utiliseation de certainses librairies peuvent etre optimiset (Sentence Transformer qui utilise torch par exemple)
- Vector DB setup up
- At startup, retriever inittialisation peut etre optimise car il prend plusieurs minutes, les premieres requestes genere parfois des A 504 Gateway Timeout error 

Software
- Frontend
- authentification
- test unitaire
- test integration
- linting (blakc, flake8) et typing


---
