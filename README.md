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

Architecture Microservices, composée de :

#### **1. Service d’ingestion (job one-shot)**

* Dockerfile dédié
* charge les JSONL
* compute embeddings
* insère dans Chroma

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

Input :

```json
{ "question": "What did Jensen say about gaming revenue in Q4 2023?" }
```

Process :

1. embedded la question
2. cherche les vecteurs les plus proches dans Chroma
3. construit un prompt
4. envoie au modèle HF
5. retourne une réponse + chunks sources

Output :

```json
{
  "answer": "...",
  "sources": [
    { "id": "...", "text": "..." }
  ]
}
```

---

## 8. 🎨 **Frontend Description**

* UI simple en React
* champ de texte pour poser une question
* affichage des résultats avec highlight
* affichage des sources

Pourquoi React ?

* rapide à mettre en place
* facile à dockeriser avec Nginx
* moderne et maintenable

---

## 9. 🧭 **Pourquoi NGINX ?**

* gère le **routing** (frontend ↔ backend)
* sert le build React en mode performant
* produit une architecture plus réaliste
* ajoute CORS, headers de sécurité
* permet SSL plus tard

---

## 10. 🧱 **Pourquoi un container dédié pour Chroma ?**

* éviter d’installer tout Chroma dans le backend
* isolation mémoire + CPU
* possibilité de scaling indépendant
* permet ingestion job séparé
* pratique pour la persistance via volumes

---

## 11. 🧪 **Setup & Run Instructions**

### 1. Clone

```
git clone <repo-url>
cd project
```

### 2. Ajouter `.env`

```
HF_API_KEY=xxxxx
```

### 3. Lancer l’application

```
docker compose up -d --build
```

### 4. Vérifier l’ingestion

```
docker logs ingest -f
```

Si succès :

```
🔥 Successfully inserted XXXX vectors
```

### 5. Ouvrir le frontend

[http://localhost:80](http://localhost:80)

---

## 12. 💬 **Exemples de questions**

```
"What did Jensen say about Data Center business growth?"
"How did Gaming revenue evolve in Q2 2023?"
"What guidance was provided for next quarter?"
```

---

## 13. ⚖️ **Trade-offs**

* J’ai choisi FastAPI plutôt que LangChain pour plus de contrôle.
* J’ai choisi Chroma plutôt que FAISS pour simplifier le Docker networking.
* Chunking simple 500 tokens : ok pour un prototype, mais améliorable.
* Pas d’auth backend — trop long pour un proof-of-concept.
* Pas de citation exacte des paragraphes (option possible).

---

## 14. 🤖 **Usage de GenAI dans le développement**

* génération initiale des modèles d’architectures
* tests de chunking et pipeline embedding
* génération partielle de code boilerplate
* optimisation ultrarapide du Dockerfile et services
* documentation + rapport généré en LLM

---

## 15. 🚀 **Suggestions de futurs travaux**

* utiliser un modèle ONNX pour réduire l’image
* intégrer reranking **bge-reranker**
* ajouter summarization des earnings calls
* améliorer le frontend (citations, highlights)
* support multi-compagnies / multi-documents
* auth Oauth2 + logs d’usage
* CI/CD GitHub actions + tests unittaires

---

# 🎉 Rapport terminé

Si tu veux :

* une **version PDF**
* une **version Markdown GitHub**
* un **diagramme mermaid**
* une **présentation PowerPoint** générée
  → Dis-moi, je te la génère.
