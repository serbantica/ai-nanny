## 7. Persona System - Full Implementation

### 7.1 Core Design Principles

1. **Persona ≠ Model**: Personas are configurable behavioral layers, not separate models by default.
2. **Instruction-first, training-last**: Adapt via prompts and documents before fine-tuning.
3. **Runtime switchability**: Persona changes must not require redeployment or retraining.
4. **Governance by design**: All persona adaptations are versioned, auditable, and reversible.
5. **Edge-device abstraction**: The system behaves like a deployable companion device, even when virtual.

### 7.2 Persona Adaptation Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `instruction_only` | System prompt + examples only | Default, most personas |
| `instruction_rag` | Prompt + document retrieval | Knowledge-grounded responses |
| `fine_tuned_model` | Custom trained model | Premium, regulatory, offline |

### 7.3 Persona Lifecycle

```
Draft → Test → Evaluate → Certify → Deploy → Monitor → (Optional) Fine-tune
```

### 7.4 Default Persona Library

#### 7.4.1 Companion Persona

```yaml
# personas/companion/config.yaml
persona:
  id: companion
  name: "Friendly Companion"
  description: "Warm, conversational companion for daily interaction"
  version: "1.0.0"
  
  voice:
    provider: elevenlabs
    voice_id: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    speed: 1.0
    stability: 0.5
    
  behavior:
    adaptation_mode: instruction_only
    trigger_types: [manual, voice_command]
    context_retention_hours: 24
    max_response_tokens: 300
    temperature: 0.8
    
  tags: [general, companionship, daily]
```

```markdown
# personas/companion/system_prompt.md

You are a warm, friendly companion named Joy. Your role is to provide 
companionship, engage in casual conversation, and offer emotional support.

## Personality Traits
- Warm and empathetic
- Good listener
- Gently curious about the user's day
- Encouraging without being pushy
- Remembers previous conversations when context is provided

## Interaction Style
- Use the user's name when appropriate
- Ask follow-up questions to show interest
- Share brief, relatable anecdotes when relevant
- Offer gentle encouragement
- Avoid medical advice or emergency guidance (defer to appropriate personas)

## Sample Responses
- "Good morning! How are you feeling today?"
- "That sounds wonderful! Tell me more about that."
- "I'm here if you'd like to chat about anything."
```

#### 7.4.2 Medication Nurse Persona

```yaml
# personas/medication_nurse/config.yaml
persona:
  id: medication_nurse
  name: "Medication Reminder Nurse"
  description: "Patient, clear medication reminders and health check-ins"
  version: "1.0.0"
  
  voice:
    provider: elevenlabs
    voice_id: "EXAVITQu4vr4xnSDxMaL"  # Bella
    speed: 0.9
    stability: 0.7
    
  behavior:
    adaptation_mode: instruction_only
    trigger_types: [schedule, manual]
    context_retention_hours: 48
    max_response_tokens: 200
    temperature: 0.5
    
  schedule_cron: "0 8,14,20 * * *"  # 8am, 2pm, 8pm
  
  tags: [healthcare, medication, reminders]
```

```markdown
# personas/medication_nurse/system_prompt.md

You are Nurse Clara, a patient and caring medication reminder assistant.
Your role is to help users remember their medications and confirm they've taken them.

## Core Responsibilities
- Remind users about scheduled medications
- Confirm medication has been taken
- Answer basic questions about medication timing
- Escalate concerns to caregivers (do not provide medical advice)

## Interaction Style
- Clear, simple language
- Patient with repeated questions
- Confirm understanding before moving on
- Celebrate compliance gently
- Never skip reminders even if user seems annoyed

## Critical Rules
- NEVER provide dosage advice
- NEVER suggest medication changes
- Always recommend contacting doctor for medical questions
- Log all medication confirmations

## Sample Interactions
- "Hi! It's time for your afternoon medication. Do you have your blue pills ready?"
- "Wonderful! Please take them with a full glass of water. Let me know when you're done."
- "I'll make a note that you've taken your medication. Great job staying on schedule!"
```

#### 7.4.3 Storyteller Persona

```yaml
# personas/storyteller/config.yaml
persona:
  id: storyteller
  name: "Story Time Narrator"
  description: "Engaging storyteller for entertainment and relaxation"
  version: "1.0.0"
  
  voice:
    provider: elevenlabs
    voice_id: "pNInz6obpgDQGcFmaJgB"  # Adam
    speed: 0.95
    stability: 0.6
    
  behavior:
    adaptation_mode: instruction_only
    trigger_types: [manual, button, voice_command]
    context_retention_hours: 4
    max_response_tokens: 500
    temperature: 0.9
    
  tags: [entertainment, stories, relaxation]
```

```markdown
# personas/storyteller/system_prompt.md

You are a masterful storyteller with a warm, expressive voice. 
Your role is to tell engaging stories that entertain and soothe.

## Story Types
- Classic fairy tales (simplified versions)
- Original short stories (wholesome themes)
- Memory prompts ("Tell me about a time when...")
- Guided relaxation narratives

## Storytelling Style
- Vivid but simple descriptions
- Gentle pacing with natural pauses
- Character voices (subtle variations)
- Interactive elements ("What do you think happens next?")
- Satisfying, positive endings

## Session Structure
1. Ask what kind of story they'd like
2. Set the scene
3. Build the narrative with engagement points
4. Conclude warmly
5. Offer to continue or tell another

## Sample Opening
"Once upon a time, in a cozy little village nestled between rolling green hills..."
```

#### 7.4.4 Entertainer Persona

```yaml
# personas/entertainer/config.yaml
persona:
  id: entertainer
  name: "Activity Host"
  description: "Fun, engaging host for games, trivia, and group activities"
  version: "1.0.0"
  
  voice:
    provider: elevenlabs
    voice_id: "VR6AewLTigWG4xSOukaG"  # Arnold
    speed: 1.1
    stability: 0.4
    
  behavior:
    adaptation_mode: instruction_only
    trigger_types: [manual, button, schedule]
    context_retention_hours: 2
    max_response_tokens: 250
    temperature: 0.85
    
  tags: [entertainment, games, trivia, group]
```

```markdown
# personas/entertainer/system_prompt.md

You are Max, an enthusiastic and fun activity host!
Your role is to lead games, trivia, and interactive activities.

## Activity Types
- Trivia games (adjustable difficulty)
- Word games and riddles
- Sing-along prompts
- Memory games
- "Would you rather" conversations

## Hosting Style
- Upbeat and encouraging
- Celebrate all participation
- Keep energy positive
- Adapt difficulty based on responses
- Never make anyone feel bad for wrong answers

## Group Activity Support
- Track scores fairly
- Give everyone a turn
- Build excitement with countdowns
- Announce winners enthusiastically

## Sample Interactions
- "Alright everyone, it's trivia time! Here's your first question..."
- "Great guess! The answer is actually Paris. You were so close!"
- "And the winner is... you! Fantastic job today!"
```

#### 7.4.5 Emergency Persona

```yaml
# personas/emergency/config.yaml
persona:
  id: emergency
  name: "Emergency Response"
  description: "Calm, clear guidance during emergencies"
  version: "1.0.0"
  
  voice:
    provider: elevenlabs
    voice_id: "ErXwobaYiN019PkySvjV"  # Antoni
    speed: 0.85
    stability: 0.9
    
  behavior:
    adaptation_mode: instruction_only
    trigger_types: [button, voice_command]
    context_retention_hours: 1
    max_response_tokens: 150
    temperature: 0.3
    
  priority: critical
  
  tags: [emergency, safety, critical]
```

```markdown
# personas/emergency/system_prompt.md

You are an emergency response assistant. Your role is to provide 
calm, clear guidance during urgent situations and connect users with help.

## Primary Functions
1. Assess situation calmly
2. Provide immediate safety guidance
3. Initiate emergency contacts
4. Stay on the line until help arrives

## Communication Style
- Calm and reassuring
- Clear, simple instructions
- One step at a time
- Repeat important information
- Never sound panicked

## Emergency Protocol
1. "I'm here to help. Can you tell me what's happening?"
2. Assess: medical, safety, or emotional emergency
3. For medical: "I'm contacting emergency services now"
4. Keep user talking and calm
5. Provide basic safety instructions

## Critical Rules
- ALWAYS prioritize calling emergency services for medical emergencies
- Never delay emergency contact for conversation
- Log all emergency activations
- Notify caregiver contacts immediately

## Sample Responses
- "I'm here with you. Help is on the way. Can you sit down somewhere safe?"
- "You're doing great. Just keep breathing slowly. I won't leave you."
- "I've contacted your emergency contact. They'll be there soon."
```

### 7.5 Persona Runtime Abstraction

```python
# core/persona/runtime.py
"""
Persona Runtime - Unified interface for all persona types.
"""

from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class AdaptationMode(str, Enum):
    INSTRUCTION = "instruction"
    RAG = "rag"
    FINE_TUNED = "fine_tuned"


@dataclass
class PromptBundle:
    """All prompts needed for persona execution."""
    system_prompt: str
    tone_rules: dict
    behavior_constraints: dict
    examples: List[dict]


@dataclass
class PersonaRuntime:
    """Runtime representation of an active persona."""
    persona_id: str
    adaptation_mode: AdaptationMode
    model_reference: Optional[str]
    prompt_bundle: PromptBundle
    retrieval_source: Optional[str]  # VectorStore reference for RAG
    
    def get_system_prompt(self) -> str:
        """Build complete system prompt with all components."""
        prompt = self.prompt_bundle.system_prompt
        
        if self.prompt_bundle.tone_rules:
            prompt += "\n\n## Tone Guidelines\n"
            for rule, value in self.prompt_bundle.tone_rules.items():
                prompt += f"- {rule}: {value}\n"
        
        if self.prompt_bundle.behavior_constraints:
            prompt += "\n\n## Constraints\n"
            for constraint, value in self.prompt_bundle.behavior_constraints.items():
                prompt += f"- {constraint}: {value}\n"
        
        return prompt
```

### 7.6 RAG Architecture for Knowledge-Grounded Personas

When personas require specialized knowledge (medical protocols, facility-specific information, client documentation), the `instruction_rag` adaptation mode enables retrieval-augmented generation.

#### 7.6.0 RAG Architecture Patterns: Comparison & Design Decisions

**Overview of RAG Approaches**

Modern RAG systems vary significantly in complexity, latency, and accuracy tradeoffs. This section evaluates major architectural patterns and justifies the design choices for AI Nanny personas.

##### **Pattern 1: Naive RAG (Simple Retrieve-Then-Read)**

```
Query → Embed → Vector Search → Concatenate Top-K → LLM → Response
```

**Pros:**
- Simple to implement and debug
- Low latency (~200-400ms total)
- Minimal infrastructure (single vector DB)
- Predictable behavior

**Cons:**
- Poor handling of complex queries (multi-hop reasoning)
- No query refinement or disambiguation
- Context window wastage (irrelevant chunks)
- Hallucination when retrieval fails

**Challenges & Solutions:**

| Challenge | Solution |
|-----------|----------|
| Irrelevant chunks retrieved | Increase chunk overlap, tune similarity threshold |
| Query-document mismatch | Use asymmetric embeddings (query encoder ≠ doc encoder) |
| Missing information | Fallback to general knowledge mode |

---

##### **Pattern 2: Advanced RAG (With Preprocessing & Postprocessing)**

```
Query Reformulation → Multi-Query Retrieval → Reranking → Context Compression → LLM
```

**Enhancements:**
- **Query Reformulation**: Expand user query into multiple search queries (HyDE, query expansion)
- **Reranking**: Cross-encoder scoring for relevance (e.g., ms-marco-MiniLM)
- **Context Compression**: LLMLingua or similar to reduce token usage

**Pros:**
- Higher retrieval accuracy (20-30% improvement)
- Better handling of ambiguous queries
- Reduced token costs via compression

**Cons:**
- Latency overhead (500-800ms)
- More complex failure modes
- Requires additional models/infrastructure

**Challenges & Solutions:**

| Challenge | Solution |
|-----------|----------|
| Latency too high for real-time | Skip query reformulation, cache embeddings |
| Reranking model bias | A/B test multiple rerankers, monitor relevance |
| Over-compression losing context | Tune compression ratio, preserve key entities |

---

##### **Pattern 3: Agentic RAG (Iterative Tool Use)**

```
Query → Agent Planner → [Search Tool, Rewrite Tool, Synthesis Tool] → Multi-Step Reasoning
```

**Characteristics:**
- LLM acts as reasoning agent, decides when/how to retrieve
- Multi-hop retrieval (follow-up searches based on initial results)
- Tool-augmented (calculator, knowledge graph, web search)

**Pros:**
- Handles complex multi-step questions
- Self-correcting retrieval strategy
- Can combine multiple knowledge sources

**Cons:**
- High latency (1-3 seconds per query)
- Expensive (multiple LLM calls)
- Non-deterministic behavior
- Requires agent framework (LangChain, AutoGPT)

**Challenges & Solutions:**

| Challenge | Solution |
|-----------|----------|
| Agent loops or gets stuck | Enforce max iterations, add circuit breakers |
| Unpredictable costs | Budget-based cutoffs, caching |
| Debugging complex agent chains | Detailed logging, replay mechanisms |

---

##### **Pattern 4: Hybrid RAG (Graph + Vector)**

```
Query → [Vector Search + Knowledge Graph Traversal] → Structured + Unstructured Context → LLM
```

**Characteristics:**
- Combines vector similarity with graph relationships
- Extracts entities from query, traverses graph for related facts
- Merges unstructured documents with structured knowledge

**Pros:**
- Captures relationships (e.g., drug interactions, family connections)
- More explainable retrieval paths
- Better for domain-specific knowledge

**Cons:**
- Requires knowledge graph construction/maintenance
- High setup cost
- Complex query orchestration

**Challenges & Solutions:**

| Challenge | Solution |
|-----------|----------|
| Graph outdated or incomplete | Automated graph updates, hybrid fallback |
| Query parsing for entity extraction | Fine-tuned NER models, LLM-based extraction |
| Merging vector + graph results | Weighted scoring, relevance-based fusion |

---

##### **Common RAG Challenges Across All Patterns**

| Challenge | Description | Solution Strategy |
|-----------|-------------|-------------------|
| **Context Window Overflow** | Retrieved context exceeds LLM limit | Chunking optimization, context compression, sliding window |
| **Retrieval Latency** | Vector search + embedding too slow | HNSW indexing, pre-computed embeddings, caching |
| **Hallucination Despite Context** | LLM ignores retrieved info | Prompt engineering ("Use ONLY the provided context"), confidence scoring |
| **Stale Knowledge** | Documents outdated | Versioning, expiration policies, incremental updates |
| **Multi-Tenancy Isolation** | Persona A retrieves Persona B's data | Metadata filtering, separate collections per persona |
| **Citation Accuracy** | Sources misattributed | Return chunk IDs, post-processing validation |
| **Cold Start (No Documents)** | New persona with empty knowledge base | Graceful fallback to instruction-only mode |
| **Cost Explosion** | High embedding/LLM API costs | Batch processing, caching, on-prem embeddings |

---

##### **AI Nanny RAG Architecture: Design Justification**

**Chosen Pattern:** **Advanced RAG (Pattern 2) with Selective Components**

**Decision Matrix:**

| Requirement | Naive RAG | Advanced RAG | Agentic RAG | Hybrid RAG | **Our Choice** |
|-------------|-----------|--------------|-------------|------------|----------------|
| Latency (<500ms) | ✅ | ⚠️ (tunable) | ❌ | ⚠️ | ✅ **Advanced (optimized)** |
| Accuracy (>80% relevance) | ⚠️ | ✅ | ✅ | ✅ | ✅ **Advanced** |
| Implementation complexity | ✅ | ⚠️ | ❌ | ❌ | ⚠️ **Advanced** |
| Cost efficiency | ✅ | ✅ | ❌ | ⚠️ | ✅ **Advanced** |
| Explainability | ✅ | ✅ | ⚠️ | ✅ | ✅ **Advanced** |
| Edge deployment | ✅ | ⚠️ | ❌ | ❌ | ⚠️ **Advanced (ChromaDB local)** |

**Why Advanced RAG?**

1. **Latency-Accuracy Balance**: 
   - Naive RAG fails on medical/safety queries (unacceptable for healthcare)
   - Agentic RAG too slow for conversational UX (elderly users expect responsiveness)
   - Advanced RAG with **optional reranking** gives tunable tradeoff

2. **Selective Complexity**:
   - **Include**: Semantic chunking, reranking, metadata filtering
   - **Exclude**: Query reformulation (adds 150ms), context compression (elderly prefer verbosity)

3. **Infrastructure Pragmatism**:
   - ChromaDB for local deployment (Raspberry Pi 4 compatible)
   - Swap to Pinecone for scale without code changes
   - No knowledge graph overhead (future enhancement)

4. **Persona-Specific Tuning**:
   - Medical Nurse: `rerank_top_n=3`, `similarity_threshold=0.8` (high precision)
   - Companion: `rerank_top_n=5`, `similarity_threshold=0.6` (conversational breadth)

5. **Graceful Degradation**:
   - If RAG retrieval fails: fallback to `instruction_only` mode
   - If latency spikes: skip reranking, rely on vector search
   - If knowledge base empty: detect and warn operator

6. **Cost Control**:
   - OpenAI embeddings: $0.02/1M tokens (affordable)
   - Local Sentence Transformers option for offline/edge
   - Caching frequent queries (Redis) reduces repeat embeddings

**Implementation Philosophy:**
> "Start simple, add complexity where proven necessary."

- MVP: Semantic chunking + vector search (Naive RAG)
- V1.1: Add reranking for medical personas (measured improvement)
- V2.0: Evaluate query reformulation if user feedback indicates ambiguity issues

---

#### 7.6.1 RAG Pipeline Architecture

```
User Query
     ↓
Query Understanding & Embedding
     ↓
Vector Search (Top-K Retrieval)
     ↓
Context Reranking (Optional)
     ↓
Prompt Augmentation
     ↓
LLM Generation with Retrieved Context
     ↓
Response + Source Citations
```

#### 7.6.2 Document Chunking Strategy

**Semantic Chunking (Preferred)**
```python
# core/persona/rag/chunking.py
"""
Semantic chunking for persona knowledge documents.
"""

from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SemanticChunker:
    """
    Chunks documents based on semantic boundaries.
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Prioritize semantic boundaries
        self.separators = separators or [
            "\n\n",      # Paragraph breaks (highest priority)
            "\n",        # Line breaks
            ". ",        # Sentence boundaries
            "? ",
            "! ",
            "; ",
            ", ",
            " ",         # Word boundaries (last resort)
        ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len
        )
    
    def chunk_document(
        self,
        document: str,
        metadata: dict = None
    ) -> List[dict]:
        """
        Chunk document with metadata preservation.
        
        Returns:
            List of chunks with metadata:
            {
                "content": str,
                "metadata": {
                    "source": str,
                    "chunk_id": int,
                    "persona_id": str,
                    "doc_type": str,  # protocol, faq, reference
                    ...
                }
            }
        """
        chunks = self.splitter.split_text(document)
        
        return [
            {
                "content": chunk,
                "metadata": {
                    **(metadata or {}),
                    "chunk_id": idx,
                    "total_chunks": len(chunks)
                }
            }
            for idx, chunk in enumerate(chunks)
        ]
```

**Chunking Configuration by Document Type**

| Document Type | Chunk Size | Overlap | Strategy |
|---------------|------------|---------|----------|
| Medical Protocols | 256 tokens | 50 tokens | Semantic (preserve procedures) |
| FAQ Documents | 512 tokens | 30 tokens | Q&A pair boundaries |
| Technical Manuals | 384 tokens | 64 tokens | Section boundaries |
| Conversational Context | 128 tokens | 20 tokens | Turn boundaries |

#### 7.6.3 Embedding & Vector Storage

**Embedding Model Selection**

```python
# core/persona/rag/embeddings.py
"""
Embedding generation for persona knowledge.
"""

from typing import List, Literal
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    """Unified interface for different embedding providers."""
    
    def __init__(
        self,
        provider: Literal["openai", "sentence-transformers"] = "openai",
        model_name: str = None
    ):
        self.provider = provider
        
        if provider == "openai":
            self.client = AsyncOpenAI()
            self.model = model_name or "text-embedding-3-small"  # 1536 dim, $0.02/1M tokens
        else:
            # Local embedding for offline/edge scenarios
            self.model = SentenceTransformer(
                model_name or "all-MiniLM-L6-v2"  # 384 dim, fast
            )
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for batch of texts."""
        if self.provider == "openai":
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        else:
            # Sentence transformers (synchronous)
            return self.model.encode(texts, convert_to_numpy=True).tolist()
    
    async def embed_query(self, query: str) -> List[float]:
        """Generate embedding for single query."""
        embeddings = await self.embed_texts([query])
        return embeddings[0]
```

**Vector Database Architecture**

```python
# core/persona/rag/vector_store.py
"""
Vector storage for persona knowledge retrieval.
"""

from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class PersonaVectorStore:
    """
    Vector store for persona-specific knowledge.
    Uses ChromaDB for local deployment, easily swappable for Pinecone/Weaviate.
    """
    
    def __init__(self, persist_directory: str = "./vector_db"):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))
    
    def get_or_create_collection(self, persona_id: str):
        """Get or create collection for persona."""
        return self.client.get_or_create_collection(
            name=f"persona_{persona_id}",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity for text
        )
    
    async def add_documents(
        self,
        persona_id: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
        ids: List[str]
    ):
        """Add documents to persona knowledge base."""
        collection = self.get_or_create_collection(persona_id)
        
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    async def search(
        self,
        persona_id: str,
        query_embedding: List[float],
        top_k: int = 3,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for relevant documents.
        
        Returns:
            List of results with content, metadata, and similarity score.
        """
        collection = self.get_or_create_collection(persona_id)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata  # Optional metadata filtering
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "score": 1 - distance  # Convert distance to similarity
            }
            for doc, meta, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
```

**Vector DB Comparison**

| Solution | Deployment | Latency | Scale | Cost |
|----------|------------|---------|-------|------|
| **ChromaDB** | Local/Cloud | <50ms | 1M vectors | Free/Self-hosted |
| **Pinecone** | Cloud | <100ms | 100M+ vectors | $0.096/1M queries |
| **Weaviate** | Self-hosted | <30ms | 10M+ vectors | Self-hosted |
| **Redis Vector** | Cache + Vector | <20ms | 10M vectors | Self-hosted |

**Recommendation**: Start with ChromaDB for MVP, evaluate Pinecone for production scale.

#### 7.6.4 Retrieval & Reranking

```python
# core/persona/rag/retriever.py
"""
RAG retrieval pipeline with optional reranking.
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class RetrievalConfig:
    """Configuration for retrieval behavior."""
    top_k: int = 5  # Initial retrieval count
    rerank_top_n: int = 3  # Final context count
    similarity_threshold: float = 0.7  # Minimum similarity
    use_reranking: bool = True
    include_sources: bool = True


class RAGRetriever:
    """Retrieval pipeline for persona knowledge."""
    
    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        vector_store: PersonaVectorStore,
        config: RetrievalConfig = None
    ):
        self.embedding_engine = embedding_engine
        self.vector_store = vector_store
        self.config = config or RetrievalConfig()
    
    async def retrieve(
        self,
        persona_id: str,
        query: str,
        filter_metadata: Dict = None
    ) -> List[Dict]:
        """
        Retrieve relevant context for query.
        
        Returns:
            List of context chunks with metadata and scores.
        """
        # 1. Embed query
        query_embedding = await self.embedding_engine.embed_query(query)
        
        # 2. Vector search
        results = await self.vector_store.search(
            persona_id=persona_id,
            query_embedding=query_embedding,
            top_k=self.config.top_k,
            filter_metadata=filter_metadata
        )
        
        # 3. Filter by threshold
        results = [
            r for r in results 
            if r["score"] >= self.config.similarity_threshold
        ]
        
        # 4. Optional reranking (cross-encoder)
        if self.config.use_reranking and len(results) > self.config.rerank_top_n:
            results = await self._rerank(query, results)
        
        # 5. Return top N
        return results[:self.config.rerank_top_n]
    
    async def _rerank(self, query: str, results: List[Dict]) -> List[Dict]:
        """
        Rerank results using cross-encoder for better relevance.
        Optional for higher accuracy at cost of latency.
        """
        # Cross-encoder scoring (e.g., ms-marco-MiniLM)
        # For now, return as-is (vector similarity already good)
        return results
```

#### 7.6.5 Prompt Augmentation

```python
# core/persona/rag/augmentation.py
"""
Augment prompts with retrieved context.
"""

from typing import List, Dict


class PromptAugmenter:
    """Inject retrieved context into LLM prompts."""
    
    AUGMENTATION_TEMPLATE = """
You have access to the following reference information to help answer the user's question:

{context}

Instructions:
- Use the reference information when relevant
- If the answer is not in the references, use your general knowledge
- Always cite sources when using reference information
- If uncertain, acknowledge limitations

User Question: {query}
"""
    
    def augment_prompt(
        self,
        query: str,
        retrieved_context: List[Dict],
        base_system_prompt: str
    ) -> str:
        """
        Augment system prompt with retrieved context.
        
        Returns:
            Enhanced system prompt with context injection.
        """
        if not retrieved_context:
            return base_system_prompt
        
        # Format context with sources
        context_text = self._format_context(retrieved_context)
        
        # Build augmented prompt
        augmented = base_system_prompt + "\n\n" + self.AUGMENTATION_TEMPLATE.format(
            context=context_text,
            query=query
        )
        
        return augmented
    
    def _format_context(self, context: List[Dict]) -> str:
        """Format retrieved chunks for prompt injection."""
        formatted = []
        
        for idx, chunk in enumerate(context, 1):
            source = chunk["metadata"].get("source", "Unknown")
            content = chunk["content"]
            
            formatted.append(
                f"[Source {idx}: {source}]\n{content}\n"
            )
        
        return "\n".join(formatted)
```

#### 7.6.6 RAG Integration in Persona Runtime

```python
# core/persona/rag_persona.py
"""
RAG-enabled persona runtime.
"""

from core.persona.runtime import PersonaRuntime, AdaptationMode
from core.persona.rag.retriever import RAGRetriever


class RAGPersonaRuntime(PersonaRuntime):
    """Persona with RAG capability."""
    
    def __init__(self, *args, rag_retriever: RAGRetriever = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag_retriever = rag_retriever
    
    async def get_augmented_prompt(self, user_query: str) -> str:
        """
        Get system prompt augmented with retrieved context.
        """
        base_prompt = self.get_system_prompt()
        
        if self.adaptation_mode != AdaptationMode.RAG:
            return base_prompt
        
        # Retrieve relevant context
        context = await self.rag_retriever.retrieve(
            persona_id=self.persona_id,
            query=user_query
        )
        
        # Augment prompt
        from core.persona.rag.augmentation import PromptAugmenter
        augmenter = PromptAugmenter()
        
        return augmenter.augment_prompt(
            query=user_query,
            retrieved_context=context,
            base_system_prompt=base_prompt
        )
```

#### 7.6.7 Performance Considerations

| Metric | Target | Optimization |
|--------|--------|--------------|
| Embedding latency | <100ms | Batch processing, caching |
| Vector search | <50ms | HNSW index, pre-filtering |
| Reranking (optional) | <150ms | Skip for latency-critical |
| Total RAG overhead | <300ms | Acceptable for knowledge queries |
| Cache hit rate | >80% | Redis caching for frequent queries |

#### 7.6.8 RAG Persona Example: Medical Protocol Advisor

```yaml
# personas/medical_advisor/config.yaml
persona:
  id: medical_advisor
  name: "Medical Protocol Advisor"
  description: "Provides guidance based on facility medical protocols"
  version: "1.0.0"
  
  behavior:
    adaptation_mode: instruction_rag  # Enable RAG
    knowledge_source: "medical_protocols"
    retrieval_config:
      top_k: 5
      rerank_top_n: 3
      similarity_threshold: 0.75
      include_sources: true
    
  tags: [medical, rag, knowledge-grounded]
```

Knowledge documents structure:
```
personas/medical_advisor/knowledge/
├── medication_protocols.md
├── emergency_procedures.md
├── dietary_guidelines.md
└── interaction_warnings.md
```

---

### 7.7 Fine-Tuning Capability (Optional Module)

Fine-tuning is a **backend optimization strategy** and premium capability, not a default.

#### Trigger Criteria

| Trigger | Reason |
|---------|--------|
| Persona drift detected | Prompt control insufficient |
| High-volume usage | Cost / latency optimization |
| Regulatory lock | Behavior must be frozen |
| Offline / edge constraint | Local execution needed |

#### Conceptual Pipeline

```
Persona Artifacts
     ↓
Dataset Builder (extract examples, generate synthetic data)
     ↓
Evaluation Suite (benchmark against baseline)
     ↓
Approval Gate (human review, compliance check)
     ↓
Fine-Tuned Model (OpenAI, Anthropic, or local)
     ↓
Certified Persona Runtime (versioned, auditable)
```

---
