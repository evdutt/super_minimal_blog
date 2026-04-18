# A Framework for Agentic Systems

Software systems in the "agentic era" can be characterized by what controls the **orchestrator** (the layer that drives control flow and decides what happens next) and what does the work as the **executor** (the layer that carries out each step). Each axis is either **Probabilistic** or **Deterministic**.

In practice today, probabilistic means an LLM — a model that reasons flexibly but not reliably. That may broaden over time, but for now the two terms are nearly synonymous.

---

## The Punnett Square

|  | **Deterministic Executor** | **Probabilistic Executor** |
|---|---|---|
| **Probabilistic Orchestrator** | Agents with Tools | Autonomous Multi-Agent / Chatbot |
| **Deterministic Orchestrator** | Standard Software | LLM in the Pipeline |

---

## The Four Patterns

### Quadrant 1: Probabilistic Orchestrator, Deterministic Executor — *Agents with Tools*

A probabilistic model (an LLM) orchestrates a workflow by deciding which tools to call and when. The tools themselves behave deterministically; the orchestrator's decisions about how and when to invoke them do not. You control the action space, not the path through it.

**Examples:** Coding agents, research agents, autonomous task runners

**Trade-off:** High flexibility, low predictability. The agent may reach the right destination via an unexpected route — or not at all.

---

### Quadrant 2: Deterministic Orchestrator, Probabilistic Executor — *LLM in the Pipeline*

Deterministic code drives the workflow — iterating, branching, and managing state — while a probabilistic model handles the fuzzy parts: understanding, summarizing, classifying, or generating content at each step. The LLM is a capability, not a decision-maker.

**Examples:** Web scrapers with LLM-powered content extraction, batch document analysis pipelines

**Trade-off:** High predictability at the system level, with probabilistic flexibility scoped to well-defined subtasks.

---

### Quadrant 3: Probabilistic Orchestrator, Probabilistic Executor — *Two flavors*

Both layers are probabilistic. But this quadrant contains two meaningfully different architectures:

**Intentionally unscaffolded — Raw chatbots.** A single model handles everything through conversation, with no deterministic scaffolding and no sub-agents. Suited for open-ended interaction where consistent, auditable performance doesn't matter. The "architecture" is essentially just a prompt.

**Fully AI-scaffolded — Autonomous multi-agent systems.** An LLM orchestrator dynamically spins up, delegates to, and synthesizes results from other LLM executors. Early AutoGPT-style systems are the archetype. The scaffolding exists, but it's probabilistic all the way down.

**Trade-off for both:** Maximum flexibility, minimal control. The difference is whether the lack of control is a feature (chatbots) or an unsolved problem (autonomous agents).

---

### Quadrant 4: Deterministic Orchestrator, Deterministic Executor — *Standard Software*

No probabilistic components. Coded logic throughout.

**Examples:** Everything built before ~2022. Even systems with a random number generator behaved within known, bounded parameters.

**Trade-off:** Fully predictable and auditable, but only handles what was explicitly anticipated at build time.

---

## The Punnett Square Describes Nodes. Real Systems Are Graphs.

The 2×2 above is useful for characterizing individual components, but real architectures are rarely a single quadrant. They are **graphs of nodes**, where each node can be placed somewhere on the grid — and the interesting engineering decisions happen at the edges between nodes.

Consider this pipeline:

```
[Deterministic] Iterate over a list of domains
  → [Probabilistic] LLM receives sitemap, selects 10 pages to analyze
    → [Deterministic] Route each page to the right scraper (image, text, structured data)
      → [Probabilistic] LLM analyzes and synthesizes scraped content
        → [Deterministic] Write structured results to disk
```

Read as a whole, this system alternates between quadrants 2 and 1 depending on which node is active. The outer shell is deterministic; the decision-making inside it is probabilistic; and the final write is deterministic again.

This nesting pattern has a practical implication: **you can add predictability to any probabilistic node by wrapping it in a deterministic one.** Want your LLM orchestrator to be more reliable? Constrain its action space with deterministic guards. Want your deterministic pipeline to handle messier inputs? Insert a probabilistic executor at the ingestion step.

The Punnett square doesn't tell you what your system is. It gives you a vocabulary for describing what each node is — and for reasoning about where the risk, flexibility, and control live.
