# A Framework for Agentic Systems

In this post, we'll go over a mental framing I've been using recently, drawing on my knowledge of 9th grade biology. I propose that software in the "agentic era" can be fully characterized by what controls the **orchestrator** (the layer that drives control flow and decides what happens next) and what does the work as the **executor** (the layer that carries out each step). Each axis is either **probabilistic** or **deterministic**.

In practice today (and in this post), probabilistic means an LLM. Technically, a slot machine RNG on a gambling website would also fit into this definition, but I don't think people are confused about how those work.

---

## The Punnett Square

|  | **Deterministic Executor** | **Probabilistic Executor** |
|---|---|---|
| **Probabilistic Orchestrator** | Agents with Tools | Autonomous Multi-Agent / Chatbot |
| **Deterministic Orchestrator** | Standard Software | LLM in a Call |

---

## The Four Patterns

### Quadrant 1: Probabilistic Orchestrator, Deterministic Executor — *Agents with Tools*

A probabilistic model (an LLM) orchestrates a workflow by deciding which tools to call and when. The tools themselves behave deterministically, while the orchestrator's decisions about how and when to invoke them do not.

**Examples:** Coding agents, research agents, autonomous task runners

**Trade-off:** High flexibility, but low predictability (though this is getting better as LLMs become "smarter"). The agent may reach the right destination via an unexpected route, or it may not get there at all.

---

### Quadrant 2: Deterministic Orchestrator, Probabilistic Executor — *LLM in a Call*

Deterministic code drives the workflow (iterating, branching, and managing state) while a probabilistic model handles the fuzzy parts, such as understanding, summarizing, classifying, or generating content at each step. This is especially useful when you can't enumerate in code all of the possible inputs and outputs. You're trusting an LLM to get it mostly right (which is fine for many use cases).

**Examples:** Web scrapers with LLM-powered content extraction, batch document analysis pipelines

**Trade-off:** High predictability at the system level, with probabilistic flexibility scoped to well-defined subtasks.

---

### Quadrant 3: Probabilistic Orchestrator, Probabilistic Executor — *Two flavors*

Both layers are probabilistic, but this quadrant contains two meaningfully different architectures:

**Unscaffolded — Raw chatbots.** A single model handles everything through conversation, with no deterministic scaffolding and no sub-agents (though with "thinking" now being common, this is getting rarer). Suited for open-ended interaction where consistent, auditable performance doesn't matter. The "architecture" is basically just a prompt.

**Fully AI-scaffolded — Autonomous multi-agent systems.** An LLM orchestrator dynamically spins up, delegates to, and synthesizes results from other LLM executors. This is how a lot of LLMs themselves work now, with a "Mixture of Experts". People are also building even larger systems in this manner.

**Trade-off for both:** Maximum flexibility (you don't need to specifically program how you want data to flow), minimal control. The difference is whether the lack of control is a feature (chatbots) or an unsolved problem (autonomous agents).

---

### Quadrant 4: Deterministic Orchestrator, Deterministic Executor — *Standard Software*

No probabilistic components. Coded logic throughout. If-this-then-that, while, for, etc.

**Examples:** Pretty much everything built before ~2022. Even systems with a random number generator behaved within known, bounded parameters.

**Trade-off:** Fully predictable and auditable (well, there are always bugs), but only handles what was explicitly anticipated at build time. In a way, these are the "Waterfall" to Quadrant 3's "Agile".

---

## Real Systems Are Composed of Multiple Nested Quadrants Calling Other Quadrants

The 2×2 above is useful for characterizing individual components, but real architectures are rarely a single quadrant. They are instead graphs of nodes, where each node can be placed somewhere on the Punnet Square. The interesting engineering decisions happen at the edges between nodes, and when mixing directions of which nodes can call which other nodes.

Consider this pipeline:

```
[Deterministic] Iterate over a list of domains
  → [Probabilistic] LLM receives sitemap, selects 10 pages to analyze
    → [Deterministic] Route each page to the right scraper (image, text, structured data)
      → [Probabilistic] LLM analyzes and synthesizes scraped content
        → [Deterministic] Write structured results to disk
```

Read as a whole, this system alternates between quadrants 2 and 1 depending on which node is active. The outer shell is deterministic, the decision-making inside it is probabilistic, and the final write is deterministic again.

You can add some predictability to any probabilistic node by wrapping it in a deterministic one. Want your LLM orchestrator to be more reliable? Constrain its action space with deterministic guards. You can also add flexibility (less brittleness) to your deterministic nodes. Want your pipeline to handle messier inputs? Insert a probabilistic executor at the ingestion step.

I think that overall, the Punnet Square framing gives a good vocabulary for describing what each node of a system is. I haven't thought too much about the next layer of the analogy, which would be talking about inheritance and dominance and recessiveness. My intuition says that probabilistic is dominant, and deterministic is recessive. If a system is even a little bit proabilistic, then the whole system is proabilistic.
