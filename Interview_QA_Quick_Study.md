# AI Nanny Interview Q&A - Quick Study Guide
## Dell Agentic AI Developer Position - RAG Architecture Focus

**Study Time:** 6 hours  
**Purpose:** Prepare for technical interview questions about RAG, embeddings, and agentic AI

---

## Core Interview Questions & Answers

### 1. Architecture Decision Process

**Q: "Why did you choose Advanced RAG over other patterns?"**

**Answer (45 seconds):**

We evaluated 4 RAG architectures against our requirements:

- **Naive RAG** (simple retrieve-then-read): Too risky. 70-75% accuracy unacceptable for medical queries. A wrong medication retrieval could be dangerous.

- **Advanced RAG** (with reranking): Sweet spot. 85-90% accuracy, <500ms latency, manageable complexity. We can tune it persona-by-persona (medical needs high precision, companion needs conversational breadth).

- **Agentic RAG** (iterative tool use): Too slow. 1-3 second latency breaks conversational flow for elderly users. They need responsive interactions, not long pauses.

- **Hybrid RAG** (graph + vector): Too complex. Knowledge graph construction/maintenance overhead plus edge deployment constraints on Raspberry Pi made this impractical for MVP.

**Key Insight:** We chose based on the **healthcare context** - safety, latency, and edge deployment were non-negotiable. Advanced RAG gives us tunable tradeoffs.

---

### 2. Embeddings & Chunking Strategy

**Q: "How did you approach chunking and why does it matter?"**

**Answer (45 seconds):**

**Chunking Strategy:**
- **Semantic chunking** over fixed-size because medical protocols have logical boundaries. You can't split "Step 1: Check blood pressure. Step 2: Administer medication" mid-step.
- Configurable sizes: 256 tokens for medical protocols (precision), 512 tokens for conversational docs (context).
- 50-token overlap to preserve context across chunks (like a medication dosage mentioned at chunk boundary).

**Embeddings Strategy:**
- **Dual-mode**: OpenAI text-embedding-3-small (1536 dim, $0.02/1M tokens) for production accuracy.
- **Fallback**: Sentence Transformers (384 dim, free) for offline/edge mode when network fails.
- We A/B tested both - OpenAI gave 15% better retrieval accuracy, worth the cost for medical queries.

**Why it matters:** Bad chunking = broken procedures. Wrong embedding = missed critical information. Both can impact patient safety.

---

### 3. Production Challenges

**Q: "What real-world problems did you encounter and how did you solve them?"**

**Answer (60 seconds):**

**Challenge 1: Handwritten doctor notes**
- Problem: Scanned PDFs aren't searchable
- Solution: OCR preprocessing (Tesseract) + manual QA by staff. Accept that accuracy isn't 100%, but validate critical medical data.

**Challenge 2: Conflicting family updates**
- Problem: Two family members upload different info about same event
- Solution: Timestamp priority + version control + staff moderation. Most recent update wins, but staff can review conflicts.

**Challenge 3: Network outages**
- Problem: Nursing homes have spotty internet, cloud embeddings fail
- Solution: Local Sentence Transformers fallback. Slightly lower accuracy, but system stays operational.

**Challenge 4: Cost overruns**
- Problem: Embedding API bills adding up with 1000+ daily queries
- Solution: Aggressive Redis caching (7-day TTL), batch processing, achieved 83% cache hit rate. Reduced costs by 80%.

**Key Lesson:** Production RAG requires operational engineering, not just algorithm optimization.

---

### 4. Scalability & Performance

**Q: "How does your system scale and what are the performance characteristics?"**

**Answer (45 seconds):**

**Current Scale:**
- 5 pilot devices (Raspberry Pi 4)
- 50 residents monitored
- 1,200 daily interactions
- Retrieval latency: <300ms (p95)
- End-to-end: <2s response

**Scaling Strategy:**
- **Edge-first**: ChromaDB on each device for privacy + latency. No cloud round-trip needed.
- **Clear migration path**: Swap to Pinecone for 100+ devices, no code changes required. Same API interface.
- **Caching layer**: Redis for frequent queries (80% hit rate target). Reduces embedding costs and latency.
- **Monitoring**: Real-time alerts if latency >500ms, accuracy <90%, or safety incidents >0.

**Bottlenecks identified:** Embedding generation (solved with caching), vector search at scale (solved with Pinecone migration path).

---

### 5. Continuous Improvement

**Q: "How do you ensure and improve RAG quality over time?"**

**Answer (45 seconds):**

**A/B Testing Framework:**
- Compare chunk sizes (256 vs 512 tokens), with/without reranking, OpenAI vs Sentence Transformers
- Run experiments on 50% of devices for 7 days
- Statistical significance testing (p-value < 0.05)

**Monitoring Dashboard:**
- Track: retrieval latency, accuracy, cache hit rate, escalation rate, safety incidents
- Alerts: latency >500ms, accuracy <90%, any safety incident triggers immediate investigation

**Manual Review Loop:**
- Sample 100 queries/month for manual accuracy assessment
- Staff feedback on response quality
- Iterative prompt tuning based on failure patterns

**Key Metric:** Zero safety incidents. Everything else is optimization, but safety is binary.

---

## Additional Questions (Extended)

### 6. Hallucination Prevention

**Q: "How do you handle LLM hallucinations in safety-critical scenarios?"**

**Answer (45 seconds):**

**Three-layer defense:**

1. **Prompt Engineering**: Strict instruction: "Use ONLY the provided reference information. If the answer is not in the references, say 'I need to check with staff.'"

2. **Confidence Scoring**: If retrieval similarity <0.85 for medical queries, we append disclaimer: "I found some information, but please verify with nursing staff."

3. **Human Escalation**: For medical/emergency personas, if confidence <threshold OR conflicting info detected → automatic alert to human staff. We don't trust the AI for critical decisions.

**Context-specific tolerance:**
- Storyteller persona: Accept hallucinations (creativity is fine)
- Companion persona: Low-risk, allow general knowledge
- Medical/Emergency: ZERO tolerance, escalate if uncertain

**Validation:** Every retrieval logged for audit. If hallucination reported, we review and fix prompt/retrieval logic.

---

### 7. HIPAA Compliance in RAG

**Q: "How do you ensure RAG doesn't leak patient data across residents?"**

**Answer (45 seconds):**

**Multi-layer isolation:**

1. **Metadata Filtering**: Vector queries include `resident_id` filter. ChromaDB won't return chunks from other residents.

2. **Persona-based Access Control**: 
   - Companion persona CANNOT access medical data (blocked at query level)
   - Medical Nurse can't access family private notes
   - Emergency gets medical alerts only, not financial data

3. **Encryption at Rest**: Vector DB encrypted, embeddings encrypted in cache

4. **Audit Trail**: Complete log of all retrievals (who queried, what was retrieved, when). HIPAA requires this for compliance reviews.

5. **Regular Compliance Reviews**: Manual sampling of 100 queries/month to verify no cross-contamination.

**Testing:** Inject test queries trying to access wrong resident data. Should fail 100% of the time. We run this weekly.

---

### 8. Why Edge Deployment Over Cloud?

**Q: "Why deploy RAG on Raspberry Pi instead of centralized cloud?"**

**Answer (45 seconds):**

**Three compelling reasons:**

1. **Privacy**: Resident medical data stays local, never leaves facility. Critical for HIPAA compliance and family trust.

2. **Latency**: <300ms retrieval requires local vector search. Cloud round-trip adds 150-200ms minimum (often more). Elderly users expect conversational responsiveness.

3. **Reliability**: Nursing homes have spotty internet (rural areas, old buildings). If cloud goes down, residents lose companion. Edge deployment = offline capability.

**Tradeoff:** Edge limits vector DB size (~1M vectors per device). For now, sufficient. At scale, hybrid model: frequently accessed data local, full archive in cloud.

**Cost benefit:** No cloud query costs, no bandwidth costs. One-time Raspberry Pi ($75) vs ongoing cloud bills.

---

### 9. When Does RAG Become Overkill?

**Q: "Does AI Nanny actually need RAG, or could you use a simple database?"**

**Answer (60 seconds - HONEST ANSWER):**

**You're right to ask this.** For structured queries, RAG is overkill:

- "What time is my medication?" → Simple SQL query, no embeddings needed
- "Who are my grandchildren?" → Structured profile field lookup

**RAG becomes necessary when:**

1. **Unstructured document ingestion**: Facilities upload 50-page PDF protocols. We can't manually structure this into SQL. Chunking + semantic search lets us query it.

2. **Semantic search**: "What should I do if I feel dizzy after medication?" → No exact match in DB, need to retrieve side-effect protocols semantically.

3. **Personalized narratives**: Storyteller blends generic stories with resident's life events. RAG retrieves relevant biography chunks, weaves into story.

4. **Scalability**: Every facility has different protocols. RAG gives us generic ingestion pipeline vs custom schema per facility.

**Our Architecture:** Hybrid approach:
- Simple queries → Direct database lookup (fast path)
- Complex/unstructured → RAG pipeline (semantic search)

**For interview:** RAG demonstrates embeddings/chunking expertise (job requirement), and it's realistic for healthcare's unstructured document reality.

**Engineering maturity:** Use the right tool for the job, not the fanciest one.

---

### 10. Vector Database Selection Criteria

**Q: "Why ChromaDB for MVP and what would trigger Pinecone migration?"**

**Answer (45 seconds):**

**ChromaDB for MVP:**
- ✅ Runs on Raspberry Pi 4 (4GB RAM handles 1M vectors)
- ✅ Offline capability (no cloud dependency)
- ✅ <50ms search latency with HNSW index
- ✅ Free, open-source
- ✅ Persistent storage (survives device restart)

**Migration triggers to Pinecone:**
- Device count >50 (centralized management easier)
- Vectors >10M per facility (beyond Pi capacity)
- Need for global search across facilities (compliance queries)
- Budget allows cloud costs ($0.096/1M queries)

**Architecture decision:** Same Python API for both (abstract away VectorStore interface). Migration = config change, not code rewrite.

**Other options considered:**
- **Weaviate**: Great, but too heavy for edge. Would use for cloud deployment.
- **Redis Vector**: Considered for caching + vector combo, but ChromaDB simpler for MVP.

---

## Quick Reference: Key Numbers to Remember

| Metric | Value | Context |
|--------|-------|---------|
| Chunk size (medical) | 256 tokens | Precision for protocols |
| Chunk size (conversational) | 512 tokens | Context for narratives |
| Chunk overlap | 50 tokens | Preserve boundary context |
| OpenAI embedding dims | 1536 | High accuracy mode |
| Local embedding dims | 384 | Offline fallback |
| Target latency (retrieval) | <300ms (p95) | Conversational UX |
| Target latency (end-to-end) | <2s | User expectation |
| Accuracy target | >90% | Manual review |
| Cache hit rate | 83% (target 80%) | Cost optimization |
| Safety incidents | 0 | Zero tolerance |
| Embedding cost | $0.02/1M tokens | OpenAI pricing |
| Confidence threshold (medical) | 0.85 | High precision |
| Confidence threshold (companion) | 0.6 | Conversational breadth |

---

## Interview Strategy

### Opening Statement (30 seconds):
*"AI Nanny demonstrates production-grade RAG architecture in a safety-critical domain. I evaluated 4 RAG patterns, chose Advanced RAG for latency-accuracy balance, and implemented 6-stage validation to ensure zero medication errors. The system handles real-world challenges like handwritten notes and network outages while maintaining sub-300ms retrieval latency on edge devices."*

### If Asked About Limitations:
*"RAG is overkill for simple structured queries - those should use direct database lookups. RAG becomes necessary for unstructured document ingestion, semantic search, and personalized narratives. I designed a hybrid system that uses the right tool for each query type."*

### If Asked About Scale:
*"Currently 5 pilot devices, clear path to 100+ via Pinecone migration with no code changes. Edge-first architecture prioritizes privacy and latency, with cloud backup for heavy processing."*

### If Asked "What Would You Do Differently?":
*"Start even simpler - validate RAG is needed before implementing it. For MVP, structured DB would work for 80% of queries. Add RAG incrementally where semantic search provides clear value. This demonstrates engineering discipline over resume-driven development."*

---

## Practice Drill (Repeat Until Fluent)

**30-second RAG elevator pitch:**
*"Advanced RAG with semantic chunking, dual-mode embeddings, and 6-stage safety validation. Chunk sizes optimized per document type (256 for medical, 512 for conversational). OpenAI embeddings for accuracy, Sentence Transformers for offline. ChromaDB on edge for privacy, Pinecone for scale. Sub-300ms retrieval, zero safety incidents."*

**45-second challenge response:**
*"Real-world challenges: handwritten notes (OCR + QA), conflicting updates (timestamp priority), network outages (local fallback), cost overruns (83% cache hit rate). Production RAG requires operational architecture, not just algorithms. Every design decision driven by healthcare context: safety, latency, compliance."*

**60-second architecture walkthrough:**
*"Multi-persona agents: Medication Nurse uses RAG for protocols, Companion uses instruction-only for chat, Emergency pre-caches critical procedures. Each persona tuned for task: medical needs 0.85 confidence threshold, companion accepts 0.6. Six-stage validation: freshness, authority, conflicts, privacy, confidence, audit. If validation fails, escalate to human. Zero tolerance for medical errors, measured through manual review and monitoring dashboard."*

---

## Final Checklist Before Interview

- [ ] Can explain why Advanced RAG over 3 alternatives (30s)
- [ ] Can describe chunking strategy with token sizes (45s)
- [ ] Can list 4 production challenges + solutions (60s)
- [ ] Can explain embedding dual-mode rationale (30s)
- [ ] Can walk through 6-stage validation pipeline (45s)
- [ ] Can justify edge vs cloud deployment (45s)
- [ ] Can acknowledge when RAG is overkill (60s)
- [ ] Can recite key metrics (latency, accuracy, cost) (15s)
- [ ] Can describe HIPAA compliance measures (45s)
- [ ] Can explain scaling strategy ChromaDB→Pinecone (30s)

**Total prep time needed:** 6 hours (2 hours reading, 2 hours note-taking, 2 hours verbal practice)

---

**Remember:** Demonstrate **engineering maturity** - use the right tool for the job, acknowledge tradeoffs, show evidence-based decision making. The interviewer wants to see you **think like a production engineer**, not just recite RAG theory.

**Good luck! 🚀**
