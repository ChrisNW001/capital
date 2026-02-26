# Deck v7 — Extracted Data Points from Antrag v9

Reference document for deck generation. All figures sourced from Antrag_v9.pdf unless noted.

---

## Company

- **Legal entity:** Neurawork GmbH & Co. KG
- **Founded:** 2024
- **HQ:** Ampfing, Germany (PLZ 84539)
- **Website:** www.neurawork.de
- **Contact:** Christoph Knöll, kontakt@neurawork.de
- **Team size:** 15 employees (bootstrapped growth in 2 years)
- **Stage:** Pre-Seed / Seed (seeking first institutional round)

## Founders

- **Christoph Knöll** (CEO/Projektleitung): ex-PwC Senior Manager Transactions — M&A, IT- und KI-Strategie, TÜV SÜD Innovator. Led IT transformation and post-merger integration projects (Projektvolumen im zweistelligen Millionenbereich). Deep expertise in distributed KI systems and large-scale technology change management.
- **Sylvia Knöll** (COO): Transformation expertise from Allianz and Oliver Wyman.

## Team (ZIM Project Staff — 5 of 15)

| Role | Person-Months | Focus |
|------|--------------|-------|
| MA1: Senior Software Architect | 10.5 PM | Projektleitung, Architekturdesign |
| MA2: ML/AI Engineer | 10.5 PM | KI-Implementierung, RAG-Engine, PII-Detection |
| MA3: DevOps/Platform Engineer | 10.5 PM | Kubernetes-Infrastruktur, CI/CD, Observability |
| MA4: Senior NLP/ML-Spezialist | 7.5 PM | NLP-Modelle, PII-Detection, RAG-Optimierung |
| MA5: Senior Kubernetes/Security Engineer | 7.5 PM | K8s-Hardening, Penetrationstests, Service-Mesh |

**Technical competencies:** Python, PyTorch, TensorFlow, Transformer architectures, LangChain, Azure, AWS, GCP, Kubernetes, Docker, MLflow, Databricks, PostgreSQL, MongoDB. EU AI Act expertise (TÜV SÜD-certified KI training).

**CTO gap:** No dedicated platform-scale CTO. Hiring is priority #1 for the raise.

## ZIM Grant

- **Total project cost:** 527,499 EUR
- **Grant amount (45%):** 237,375 EUR
- **Company co-funding:** 290,124 EUR
- **Duration:** 12 months (01.05.2026 – 30.04.2027)
- **Total person-months:** 46.5 PM
- **Personnel costs:** 355,624 EUR
- **Overhead (40% of personnel):** 142,250 EUR
- **External audits:** ISO 27001 (15,000 EUR), ISO 42001 (12,000 EUR), Penetration test (2,625 EUR)
- **Scope:** Develop NeuraPlox from TRL 4 (lab-validated) to TRL 7 (operational prototype with 3 pilot customers)

## Traction & Customer Evidence

- **25+ KI-Projekte** im Mittelstand erfolgreich umgesetzt
- **Sectors served:** Due-Diligence-Systeme, automatisierte Auftragsabwicklung, Prozessautomatisierung (Pflegekräftevermittlung), KI-Transformation (Lagerlogistik)
- **4 pilot customer projects** validating core technology (TRL 4):
  1. **Dienstleistungsunternehmen:** Agent-Orchestrierung, Datenanbindung — validated in controlled environment
  2. **Immobilieninvestor:** Datenintegration und Agent-Logik with real investment data
  3. **Startup:** Basisarchitektur-Module im Testbetrieb
  4. **Steuerberatung:** ML-basierte Mustererkennung und Qualitätsprüfung bei Jahresabschlussbuchungen (classical ML + LLM workloads on real data)
- **Key insight from projects:** ~60% of project costs go to redundant infrastructure (Datenanbindung, API-Management, Authentifizierung) — rebuilt from scratch each time
- **Proxy metrics:** Each customer starts with 1-2 Ploxe in year 1, expands to 4-6 by year 3 (~300% expansion)
- **Consulting as R&D lab:** Every project feeds platform features; consulting funds R&D

## Consulting Revenue (Current)

- **No explicit ARR figure in Antrag v9** (it's a ZIM grant application, not a funding pitch)
- **Implied:** 25+ projects at typical 80,000-150,000 EUR each = significant cumulative revenue
- **Bootstrapped to 15 employees** = revenue sufficient to fund team without external investment
- **Consulting margin:** ~30% (per v7 design doc)

## Financial Model & Raise

- **Raise amount:** Not explicitly stated in Antrag v9. Derived estimate: **2,000,000 EUR** (seed round)
  - Rationale: CTO hire (~150-200K/year) + 2-3 engineers (~300-400K/year) + platform launch costs + 18-month runway = ~1.5-2.5M needed. Standard DACH B2B SaaS seed round.
  - **NOTE:** Confirm exact figure with founder.
- **Use of funds:** (1) CTO + engineering scale, (2) Platform launch, (3) First marketplace agents
- **Post-project hiring plan:** 3-4 new roles — Senior Platform Engineer, Customer Success Manager, Solution Architect, DevOps/SRE Engineer
- **By year 3:** Additional 2-3 hires (Sales, Partner Management)

## Revenue Trajectory (Platform)

| Phase | Timeline | Customers | Avg ACV | Target ARR |
|-------|----------|-----------|---------|------------|
| Phase 1 | Year 1 post-project | 10 | 60,000 EUR | 600,000 EUR |
| Phase 2 | Year 2 | 30-50 (target 40) | 60,000 EUR | 2,400,000 EUR |
| Phase 3 | Year 3 | 50+ | 60,000 EUR | 3,000,000 EUR + ecosystem |

**Break-even implied:** ~40-50 customers at avg 60K ACV = 2.4-3M ARR (Phase 2-3 transition)

## Pricing

| Model | Monthly | Annual | Target Customer |
|-------|---------|--------|----------------|
| Managed Service | 2,000-8,000 EUR | 24,000-96,000 EUR | KMU without cloud expertise |
| Customer Cloud | 1,500-5,000 EUR | 18,000-60,000 EUR | KMU with existing cloud strategy |
| On-Premise/Hybrid | Individual license | — | Regulated industries |

**Additional revenue streams:**
- SDK licensing for ISVs/SIs
- Revenue share on third-party Ploxe (15-25%)
- Certification fees for external Ploxe

**Pricing positioning:**
- 2x cheaper than Dataiku (from 48,000 EUR/year)
- 6x+ cheaper than Palantir Foundry (from 150,000 EUR/year)
- Typical KI project without platform: 80,000-150,000 EUR (60% = 48,000-90,000 EUR infrastructure waste)

## Market Data

### Global
- **AI Platform Market 2025:** $18.22B → $94.31B by 2030 (CAGR 38.9%, MarketsandMarkets)
- **MLOps Market 2025:** $2.33B → $25.93B by 2034 (CAGR 28.9%, Fortune Business Insights)
- **Europe MLOps share:** 29-33% (Technavio), ~$0.68-0.77B in 2025
- **Gartner 2025:** By 2026, 40%+ enterprise apps will contain embedded AI agents

### German Market
- **KMU in Germany:** ~3.4M (Destatis)
- **Core target group (50-500 employees):** ~70,000 (IfM Bonn)
- **KI adoption rate Germany 2025:** 36% (vs 20% prior year, Bitkom 2025)
- **Successful KI operationalization:** Only 23% of KMU (maximal.digital 2025)
- **Intention-action gap:** 86% recognize strategic relevance, only 23% successfully operationalized (63 percentage point gap)
- **KMU KI investment:** Only 0.35% of revenue — 30% below market average (Horvath 2025)
- **KI competency gap:** 82% of KMU report significant deficiency (maximal.digital 2025)
- **Data silos:** 76% of KMU struggle with fragmented data landscapes (maximal.digital 2025)
- **Cost overruns:** 63% report KI project cost overruns, averaging 34% over budget (maximal.digital 2025)
- **Missing resources:** 53% cite missing tech know-how, 51% missing personnel (Bitkom 2025)
- **German preference:** 93% of German companies prefer German KI providers (Bitkom 2025)

### Market Sizing (Bottom-Up)
- **SAM (DACH):** ~30,000 companies (70,000 core target × projected ~45% adoption by 2027)
- **Market potential DACH:** ~1.5 Mrd. EUR/year (SAM × avg annual revenue per customer)
- **SOM Year 3:** 50 customers × avg 60,000 EUR/year = 3 Mio. EUR ARR (Neurawork planning)

## Regulatory

- **EU AI Act:** August 2026 deadline for high-risk KI systems (verschärfte Anforderungen: Risikomanagementsysteme, Qualitätssicherung, menschliche Aufsicht)
- **DSGVO:** Ongoing requirements for personal data protection
- **AI Act compliance as differentiator:** 56% of companies see more drawbacks than benefits in AI Act (Bitkom 2025) = significant compliance demand without existing solutions
- **NeuraPlox approach:** EU AI Act-Compliance by Design (Art. 9 Risikomanagement, Art. 12 Aufzeichnungspflichten, Art. 14 menschliche Aufsicht)

## Product / Architecture

### N+M Architecture
- **Problem:** N agents × M data sources = N×M integrations (e.g., 3 agents × 5 sources = 15 integrations; 10 × 10 = 100)
- **Solution:** Unified Data Access Layer (L5) — each agent and each data source connects once to L5, reducing N×M to N+M
- **Connector priorities:** Microsoft 365 (SharePoint, Outlook, Teams), SAP (RFC/BAPI + SAP BTP), DMS (d.velop, ELO, DocuWare) — covers ~80% of typical Mittelstand data needs

### 7-Layer Architecture
1. **L1 — Deployment & Runtime:** Kubernetes-Operator, GitOps/ArgoCD, Helm Charts, Service Mesh, Multi-Tenancy
2. **L2 — MLOps & Data:** Model Registry (MLflow), Feature Store (Feast), Vector DB (pgvector/Milvus), ETL-Pipelines
3. **L3 — AI & Intelligence:** LLM-Gateway (multi-provider), RAG-Engine (Hybrid-Search: BM25 + Dense Retrieval), Embedding-Services
4. **L4 — Multi-Agent Observability:** OpenTelemetry tracing, Langfuse (LLM-native), Compliance-Dashboards
5. **L5 — Unified Data Access:** Connector-Framework (Adapter-Pattern), Schema-Mapping, PII-Detection (Presidio)
6. **L6 — Policy & Governance Engine:** 3D-Policy-Modell (Wer/Was/Welche Daten), Prompt Firewall, Output Control
7. **L7 — Agent Registry & Onboarding:** Lifecycle-Management, Berechtigungsmatrix, 3-tier Zertifizierung

### Governance (3D-Policy-Modell) — Key Differentiator
- **Dimension 1 — Wer:** Agent-Identität (welcher Plox stellt die Anfrage?)
- **Dimension 2 — Was:** Aktionen (Daten lesen, LLM aufrufen, andere Ploxe ansprechen)
- **Dimension 3 — Welche Daten:** Datenkategorien, Granularität
- Goes beyond classic RBAC — agents are autonomous, need finer-grained, context-dependent policies
- Agents treated as First-Class-Citizens with individual Berechtigungsprofile and Audit-Trail

### Showcase Agents (Intelligence Suite)
- **Market Intelligence:** Replaces market research consultants
- **Marketing Intelligence:** Replaces marketing agencies
- **Vertriebs Intelligence:** Replaces sales ops teams
- Each replaces an entire consulting function with one agent

### Prism Agent Flow
- Tax advisor workflows, accounts payable, bookkeeping — all AI-native
- "50% Tech, 50% Mensch" in action

## Competitive Landscape Summary

| Competitor | Category | Starting Price | NeuraPlox Advantage |
|-----------|----------|---------------|-------------------|
| Azure AI / AWS SageMaker | Hyperscaler | 3,000-15,000 EUR/mo | Cloud-agnostic, governance-integrated |
| Dataiku | Enterprise AI | 48,000 EUR/yr | Agent-centric, 2x cheaper |
| DataRobot | Enterprise AI | 30,000 EUR/yr | Not ML-lifecycle-focused |
| Palantir Foundry | Data Platform | 150,000 EUR/yr | Self-service, open ecosystem, 6x+ cheaper |
| LangChain/CrewAI | Agent Frameworks | Free (OSS) | Full infra + governance vs. just dev library |
| NeMo Guardrails | AI Governance | $4,500/GPU/yr | Holistic 3D-policy vs. I/O filtering |
| Aleph Alpha | Sovereign AI | Enterprise contracts | Mittelstand focus, standardized product |
| Langdock | KI-Adoption | 20 EUR/user/mo | Architecture platform vs. application layer |

## IP Strategy

- **Trademark:** "NeuraPlox" registered at DPMA
- **Trade secret:** Control Plane (L4-L7), especially Policy Engine (L6) and Agent Registry (L7)
- **Patent evaluation:** Planned post-project (agent-centric governance architecture)
- **Open source strategy:** Execution Layer (L1-L3) open source for adoption; Governance layers (L4-L7) proprietary

## Key Quotes for Deck

- "Operational AI = 50% Tech, 50% Mensch"
- "Agents need an OS, not more tools"
- "Governance is the unlock"
- "Consulting is the lab, Platform is the product, Marketplace is the multiplier"
- "The Agent OS market doesn't exist yet — we're creating it"
- "Enterprise AI is stuck between PoC and production"
