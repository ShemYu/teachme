TITLE = "Agent System Design"

SLIDES = []

def slide(section, html, *steps):
    SLIDES.append((section, html, list(steps)))

# ---------------------------------------------------------------- 0 Title
slide("", """
<div class="title-wrap">
  <div class="kicker">Senior Applied AI Engineering · Deep Dive</div>
  <h1 class="big">Agent System<br>Design</h1>
  <p class="lede">Add autonomy only where the path can't be predicted — and make every step <em>bounded, durable, and verifiable</em>.</p>
  <div class="agenda s1">
    <div><b>01</b> The prompt, and the arithmetic of long tasks</div>
    <div><b>02</b> Workflows vs agents: choosing autonomy</div>
    <div><b>03</b> Architecture and the agent loop</div>
    <div><b>04</b> Tools, context, and multi-agent</div>
    <div><b>05</b> Durability, memory, and evaluation</div>
    <div><b>06</b> Cost, tradeoffs, and the harness in code</div>
  </div>
</div>
""",
"Welcome. This lesson is about designing agent systems at the level of a senior applied A I engineer. Not prompting tricks, but the architecture decisions that decide whether an agent works in production: how much autonomy to give it, how its loop is built, how it manages context, and how you know it's getting better.",
"The thesis: add autonomy only where the path can't be predicted, and make every step bounded, durable, and verifiable. We'll work through one concrete system, starting from the requirements and the arithmetic of long tasks, then the choice between workflows and agents, the architecture, the four parts that decide quality, durability and evaluation, and finally cost and the harness in code.",
)

# ---------------------------------------------------------------- 1 Prompt
slide("01 · The prompt", """
<h2>“Design an agent that turns bug tickets into pull requests”</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Scope</div>
    <ul>
      <li>Input: a bug ticket + a repository</li>
      <li>Output: a pull request with a fix <b>and a test</b></li>
      <li>~2,000 tickets / week across ~50 repos</li>
      <li>A human reviews every PR before merge</li>
    </ul>
  </div>
  <div class="panel s1">
    <div class="label">Define success before architecture</div>
    <ul class="tight">
      <li><b>Primary:</b> PR merged without major edits</li>
      <li><b>Guardrail:</b> revert rate within 30 days</li>
      <li><b>Budget:</b> tokens and wall-clock per ticket</li>
      <li><b>Escape hatch:</b> “can't fix, here's what I found” is a valid output</li>
    </ul>
  </div>
</div>
""",
"Here's the prompt we'll design for: an agent that turns bug tickets into pull requests. The input is a ticket and a repository. The output is a pull request with a fix and a test. Volume is around two thousand tickets a week across fifty repositories, and a human reviews every pull request before merge.",
"Define success before architecture. The primary metric is pull requests merged without major edits. The guardrail is the revert rate within thirty days, so you don't optimize for merges that break things. There's a budget per ticket, in tokens and wall-clock time. And there's an escape hatch: a report that says I can't fix this, here's what I found, is a valid and valuable output. Agents without an honest failure mode fabricate success.",
)

# ---------------------------------------------------------------- 2 Arithmetic
slide("01 · The arithmetic", """
<h2>Long tasks compound error</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">P(task succeeds) = p<sup>steps</sup></div>
    <table class="math">
      <tr><td>p = 0.95, 20 steps</td><td class="num warn">0.36</td></tr>
      <tr><td>p = 0.99, 20 steps</td><td class="num">0.82</td></tr>
      <tr><td>p = 0.95, 20 steps, errors caught + retried</td><td class="num good-n">≫ 0.36</td></tr>
    </table>
    <div class="note">Independence is a simplification, but the shape is real.</div>
  </div>
  <div class="panel s1">
    <div class="label">Tokens per task</div>
    <table class="math">
      <tr><td>30 turns × ~40k-token context</td><td class="num">≈ 1.2 M in</td></tr>
      <tr><td>30 turns × ~500 tokens out</td><td class="num">≈ 15 k out</td></tr>
      <tr><td>× 2,000 tickets / week</td><td class="num warn">≈ 2.4 B in / week</td></tr>
    </table>
    <div class="note">Input dominates. Context re-reading is the bill.</div>
  </div>
</div>
<div class="thesis s2">Two design consequences: <b>detect and recover</b> instead of hoping each step is right, and treat <b>context as the cost driver</b>.</div>
""",
"Start with arithmetic, because it drives every decision. If each step succeeds with probability zero point nine five, a twenty-step task succeeds about thirty-six percent of the time. At zero point nine nine per step, it's about eighty-two percent. Independence is a simplification, but the shape is real. The escape is not a perfect model. It's catching errors and retrying, which turns a fragile chain into a self-correcting one.",
"Now tokens. An agent that takes thirty turns with an average context of forty thousand tokens reads about one point two million input tokens per task, and writes only about fifteen thousand. Across two thousand tickets a week, that's around two point four billion input tokens. Input dominates: the bill is the agent re-reading its own context every turn.",
"Two design consequences follow. Build detection and recovery into the loop instead of hoping each step is right. And treat context as the cost driver, which is why context engineering gets its own section.",
)

# ---------------------------------------------------------------- 3 Workflows vs agents
slide("02 · Choosing autonomy", """
<h2>Workflows vs agents</h2>
<div class="spectrum">
  <div class="sp-bar"></div>
  <div class="sp-item" style="left:0%"><b>Single call</b><span>one prompt, one answer</span></div>
  <div class="sp-item" style="left:20%"><b>Workflow</b><span>code decides the path</span></div>
  <div class="sp-item" style="left:48%"><b>Agent</b><span>model decides the path</span></div>
  <div class="sp-item" style="left:74%"><b>Multi-agent</b><span>models coordinate</span></div>
  <div class="sp-l">predictable · cheap · debuggable</div><div class="sp-r">flexible · expensive · opaque</div>
</div>
<div class="grid3">
  <div class="card v s1"><b>Workflow patterns</b><span class="muted">Prompt chaining · routing · parallelization · orchestrator-workers · evaluator-optimizer</span></div>
  <div class="card v s2"><b>Use an agent when</b><span class="muted">The number and order of steps can't be known in advance, and there's feedback from the environment.</span></div>
  <div class="card v s3"><b>For our ticket agent</b><span class="muted">Workflow skeleton (triage → fix → verify → PR), agentic inner loop only for “find and fix”.</span></div>
</div>
""",
"The first real decision is how much autonomy to give. Think of a spectrum. A single call is one prompt, one answer. A workflow is several model calls where code decides the path. An agent is where the model decides the path, choosing tools in a loop. And multi-agent is several models coordinating. Moving right buys flexibility and costs predictability, money, and debuggability.",
"Anthropic's Building Effective Agents post from late twenty twenty-four names the workflow patterns worth knowing: prompt chaining, routing, parallelization, orchestrator-workers, and evaluator-optimizer. Most production value lives in these, not in open-ended agents.",
"Use an agent when the number and order of steps can't be known in advance, and when the environment gives feedback the model can act on, like test results.",
"For our ticket agent, that means a hybrid. The skeleton is a workflow: triage, fix, verify, open the pull request. Only the find-and-fix stage is an agentic loop, because nobody can predict which files a bug will touch. This is the answer interviewers want to hear: autonomy where it's needed, code everywhere else.",
)

# ---------------------------------------------------------------- 4 Architecture
slide("03 · Architecture", """
<h2>Workflow skeleton, agentic core</h2>
<div class="arch">
  <div class="lane">
    <div class="lane-t">WORKFLOW (code decides)</div>
    <div class="row">
      <div class="box">Triage<br><span class="sm muted">route · reject · dedupe</span></div><div class="arrow">→</div>
      <div class="box agent">Find &amp; fix<br><span class="sm muted">agent loop</span></div><div class="arrow">→</div>
      <div class="box">Verify<br><span class="sm muted">tests · lint · reviewer model</span></div><div class="arrow">→</div>
      <div class="box">Open PR<br><span class="sm muted">or failure report</span></div><div class="arrow">→</div>
      <div class="box hlb">Human review</div>
    </div>
  </div>
  <div class="lane s1">
    <div class="lane-t accentc">RUNTIME</div>
    <div class="row">
      <div class="box sm2">Durable execution: checkpoint every step</div>
      <div class="box sm2">Sandbox per task: repo clone, test runner</div>
      <div class="box sm2">Tool layer (MCP)</div>
      <div class="box sm2">Context manager</div>
      <div class="box sm2">Traces + evals</div>
    </div>
  </div>
</div>
<div class="note s2">Verification failing sends the task back to “find &amp; fix” with the failure as input — at most N times, then a failure report.</div>
""",
"Here's the architecture: a workflow skeleton with an agentic core. Triage is a cheap classification step that routes, rejects, or deduplicates tickets. Find and fix is the agent loop. Verify runs the tests, the linter, and a reviewer model. Then the system opens a pull request, or writes a failure report, and a human reviews it.",
"Underneath is the runtime: durable execution that checkpoints every step, a sandbox per task with a clone of the repository and a test runner, a tool layer, here exposed through the Model Context Protocol, a context manager, and traces feeding evals.",
"One loop matters: when verification fails, the task goes back to find and fix with the failure as input, at most N times, then it produces a failure report. That bounded retry is the error recovery our arithmetic demanded.",
)

# ---------------------------------------------------------------- 5 Agent loop
slide("03 · The agent loop", """
<h2>Inside the loop</h2>
<div class="loop">
  <div class="node q">Context</div><div class="arrow">→</div>
  <div class="node">Model<br><span class="muted sm">think + tool calls</span></div><div class="arrow">→</div>
  <div class="node">Tools<br><span class="muted sm">parallel when independent</span></div><div class="arrow">→</div>
  <div class="node">Observe<br><span class="muted sm">trim · record</span></div><div class="arrow">→</div>
  <div class="node dec">Stop?</div>
</div>
<div class="back s1">↺ update context: append results, update plan, compact if near budget</div>
<div class="grid3 mt">
  <div class="card v s2"><b>Success criterion</b><span class="muted">Machine-checkable: the new test fails before and passes after; the full suite stays green.</span></div>
  <div class="card v s3"><b>Budget</b><span class="muted">Hard caps on turns, tokens, and wall-clock. Exhaustion produces a report, not silence.</span></div>
  <div class="card v s4"><b>No-progress detection</b><span class="muted">Same error three times, or no file changed in N turns → change strategy or escalate.</span></div>
</div>
""",
"Inside the loop. The context goes to the model, which thinks and emits tool calls. Tools run, in parallel when they're independent, like reading three files at once. Observations are trimmed and recorded. Then the harness decides whether to stop.",
"If not, it updates the context: append the results, update the plan, and compact if the context is near its budget. That update step is where most of the engineering lives.",
"Three stop conditions, and all three are required. First, a success criterion that a machine can check. For our agent: the new test fails before the fix, passes after, and the full suite stays green. Reproduce first is the single most effective instruction you can give a coding agent.",
"Second, a budget: hard caps on turns, tokens, and wall-clock time. Hitting the budget should produce a report of what was learned, not silence.",
"Third, no-progress detection. If the same error appears three times, or no file has changed in several turns, the harness forces a change of strategy or escalates. Without this, agents burn budget going in circles.",
)

# ---------------------------------------------------------------- 6 Tool design
slide("04 · Tool design", """
<h2>Tools are the agent's interface</h2>
<div class="grid2">
  <div class="panel code"><div class="label">A good tool definition</div><pre>{
  <span class="s">"name"</span>: <span class="s">"search_code"</span>,
  <span class="s">"description"</span>: <span class="s">"Regex search across the repo.</span>
<span class="s">    Returns file:line and 2 lines of context.</span>
<span class="s">    Use before opening files. Max 50 hits."</span>,
  <span class="s">"input_schema"</span>: {
    <span class="s">"pattern"</span>: <span class="s">"string"</span>,
    <span class="s">"path"</span>: <span class="s">"absolute path, default repo root"</span>
  }
}</pre></div>
  <ul class="s1 tight">
    <li><b>Few, well-scoped tools</b> — consolidate search + read; avoid overlap</li>
    <li><b>High-signal output</b> — truncate, paginate, summarize; say what was cut</li>
    <li><b>Instructive errors</b> — “path must be absolute” teaches; a stack trace doesn't</li>
    <li><b>Poka-yoke</b> — make mistakes impossible: absolute paths, validated edits</li>
    <li><b>Test tools with the model</b> — read transcripts, fix confusions</li>
  </ul>
</div>
<div class="thesis s2">Anthropic reported spending more time optimizing tools than the overall prompt for their SWE-bench agent. <b>Treat tool design as interface design</b> for a new kind of user.</div>
""",
"Tools are the agent's interface to the world, so design them the way you'd design an A P I for a new kind of user. Here's a good definition. The name says what it does. The description says what it returns, when to use it, and its limits. And the schema asks for an absolute path, for a reason we'll see in a moment.",
"The principles. Few, well-scoped tools: consolidate search and read patterns, and avoid overlapping tools the model has to choose between. High-signal output: truncate, paginate, and summarize, and always say what was cut. Instructive errors: path must be absolute teaches the model, a raw stack trace doesn't. Make mistakes impossible, which engineers call poka-yoke. And test tools with the model itself: read transcripts and fix whatever confuses it.",
"Anthropic reported that for their SWE-bench agent they spent more time optimizing tools than the overall prompt, and that switching to absolute paths removed a whole class of errors. Treat tool design as interface design. It's usually the highest-leverage work in the system.",
)

# ---------------------------------------------------------------- 7 Context engineering
slide("04 · Context engineering", """
<h2>Context is a budget, not a bucket</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Budget for a ~60k working context</div>
    <table class="math">
      <tr><td>System prompt + tool definitions</td><td class="num">~8k</td></tr>
      <tr><td>Task + repo map</td><td class="num">~5k</td></tr>
      <tr><td>Plan / notes file</td><td class="num">~2k</td></tr>
      <tr><td>Working set: open files, recent results</td><td class="num">~30k</td></tr>
      <tr><td>Compacted history</td><td class="num">~15k</td></tr>
    </table>
    <div class="note">Stable prefix first → prompt caching works.</div>
  </div>
  <div class="stack">
    <div class="card s1"><div class="ic">↓</div><div><b>Just-in-time retrieval</b><br><span class="muted">Hold paths and queries; load content when needed. Don't pre-stuff the repo.</span></div></div>
    <div class="card s2"><div class="ic">⇲</div><div><b>Compaction</b><br><span class="muted">Near the limit, summarize history into decisions, findings, and open questions; drop old tool output.</span></div></div>
    <div class="card s3"><div class="ic">✎</div><div><b>Structured notes</b><br><span class="muted">A plan / NOTES file the agent maintains survives compaction and restarts.</span></div></div>
  </div>
</div>
""",
"Context engineering: treat context as a budget, not a bucket. Here's a budget for a sixty-thousand-token working context. About eight thousand for the system prompt and tool definitions. Five thousand for the task and a repository map. Two thousand for a plan or notes file. About thirty thousand for the working set of open files and recent results. And fifteen thousand for compacted history. Put the stable parts first, so prompt caching can reuse them every turn.",
"Three techniques keep you inside the budget. First, just-in-time retrieval: the agent holds file paths and search queries, and loads content only when it needs it, instead of pre-stuffing the repository into context.",
"Second, compaction. Near the limit, the harness summarizes history into decisions, findings, and open questions, and drops old tool output. Models degrade as context fills, an effect often called context rot, so compaction improves quality, not just cost.",
"Third, structured notes. A plan or notes file that the agent maintains itself survives compaction and even restarts. It's the agent's external memory for the task.",
)

# ---------------------------------------------------------------- 8 Multi-agent
slide("04 · Multi-agent", """
<h2>Multi-agent: when it pays</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Anthropic research system (2025)</div>
    <table class="math">
      <tr><td>Multi-agent vs single agent, internal research eval</td><td class="num warn">+90.2%</td></tr>
      <tr><td>Tokens vs a chat interaction: single agent</td><td class="num">~4×</td></tr>
      <tr><td>Tokens vs a chat interaction: multi-agent</td><td class="num warn">~15×</td></tr>
      <tr><td>BrowseComp variance explained by token usage</td><td class="num">~80%</td></tr>
    </table>
  </div>
  <div class="panel s1">
    <div class="label">Cognition, “Don't build multi-agents” (2025)</div>
    <ul class="tight">
      <li>Actions carry implicit decisions</li>
      <li>Parallel agents make conflicting ones</li>
      <li>Share full context and traces, or don't split</li>
    </ul>
  </div>
</div>
<div class="thesis s2">Reconcile them: <b>parallelize reads, serialize writes.</b> Sub-agents explore and return condensed findings; one agent owns every edit.</div>
""",
"Multi-agent systems are the most debated design choice, so know both sides. Anthropic's write-up of their research system in twenty twenty-five reported that a lead agent with parallel sub-agents beat a single agent by ninety point two percent on their internal research eval. The cost: agents used about four times the tokens of a chat interaction, and the multi-agent system about fifteen times. And on the BrowseComp benchmark, token usage alone explained about eighty percent of the performance variance. Much of the gain is simply spending more compute, in parallel, with clean contexts.",
"The counterpoint is Cognition's post, Don't build multi-agents, from the same year. Their argument: every action carries implicit decisions, and parallel agents that can't see each other's reasoning make conflicting ones. Share full context and traces, or don't split.",
"The two positions reconcile with one rule: parallelize reads, serialize writes. Sub-agents are great at breadth-first exploration, like searching a codebase or reading documentation, and returning condensed findings. But one agent should own every edit. For our ticket agent: parallel sub-agents to locate candidate code, a single agent to write the fix.",
)

# ---------------------------------------------------------------- 9 Durability
slide("05 · Reliability", """
<h2>Durable, idempotent, bounded</h2>
<div class="grid2">
  <div class="stack">
    <div class="card"><div class="ic">⟳</div><div><b>Durable execution</b><br><span class="muted">Persist every step as an event; resume after a crash or deploy instead of restarting a 40-minute task.</span></div></div>
    <div class="card s1"><div class="ic">≡</div><div><b>Idempotent side effects</b><br><span class="muted">Idempotency keys on “open PR”, “comment”, “push”. A replayed step must not do it twice.</span></div></div>
  </div>
  <div class="stack">
    <div class="card s2"><div class="ic">⏱</div><div><b>Retry the right things</b><br><span class="muted">Backoff for rate limits and timeouts. Model mistakes aren't transient: feed the error back, don't blindly retry.</span></div></div>
    <div class="card s3"><div class="ic">▣</div><div><b>Snapshot the sandbox</b><br><span class="muted">Checkpoint the file system with the event log, so resume and replay see the same world.</span></div></div>
  </div>
</div>
""",
"Reliability comes from three properties: durable, idempotent, and bounded. Durable execution means persisting every step as an event, so after a crash or a deploy, a forty-minute task resumes where it was instead of restarting. Workflow engines built for this, like Temporal, fit agents well.",
"Idempotent side effects: attach idempotency keys to actions like opening a pull request, commenting, or pushing, so a replayed step never does it twice.",
"Retry the right things. Rate limits and timeouts are transient, so retry with backoff. Model mistakes aren't transient. Blindly retrying the same prompt usually repeats the mistake. Feed the error back as an observation instead.",
"And snapshot the sandbox together with the event log, so a resumed or replayed run sees the same file system. Without this, replay debugging lies to you.",
)

# ---------------------------------------------------------------- 10 Memory
slide("05 · Memory", """
<h2>Three kinds of memory</h2>
<table class="tbl">
  <tr><th>Kind</th><th>Lives in</th><th>Lifetime</th><th>Main risk</th></tr>
  <tr><td><b>Working</b></td><td>Context window</td><td>One turn → one task</td><td>Context rot, cost</td></tr>
  <tr class="s1"><td><b>Task notes</b></td><td>Plan / NOTES file in the sandbox</td><td>One task, survives compaction</td><td>Drift from reality</td></tr>
  <tr class="s2"><td><b>Long-term</b></td><td>Per-repo store: conventions, past fixes, gotchas</td><td>Weeks to months</td><td>Staleness, poisoning</td></tr>
</table>
<div class="thesis s3">Long-term memory is a <b>write path</b>: gate writes, attach provenance and dates, and evaluate with it on and off. Most teams need less of it than they think.</div>
""",
"Agents use three kinds of memory, and mixing them up causes bugs. Working memory is the context window, lasting from one turn to one task. Its risks are context rot and cost.",
"Task notes live in a plan or notes file in the sandbox. They last for one task and survive compaction. The risk is drift: the notes say a test passes when it no longer does, so the agent should re-verify claims before relying on them.",
"Long-term memory is a per-repository store of conventions, past fixes, and gotchas, lasting weeks to months. Its risks are staleness and poisoning.",
"Treat long-term memory as a write path. Gate writes, attach provenance and dates, and evaluate the system with memory on and off to prove it helps. Most teams need less long-term memory than they think. A good repository map and conventions file often beat a clever memory system.",
)

# ---------------------------------------------------------------- 11 Evaluation
slide("05 · Evaluation", """
<h2>Evaluate outcomes and trajectories</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Offline</div>
    <ul class="tight">
      <li>Mine historical bug-fix commits with tests → your own <b>SWE-bench-style</b> set</li>
      <li><b>Resolve rate</b> (pass@1), cost and time per task</li>
      <li>Trajectory metrics: tool errors, loops, turns to reproduce</li>
      <li>LLM judge for PR quality, <b>calibrated on human labels</b></li>
    </ul>
  </div>
  <div class="panel s1">
    <div class="label">Online</div>
    <ul class="tight">
      <li>Merge rate without major edits</li>
      <li>Human edit distance on merged PRs</li>
      <li>30-day revert rate (guardrail)</li>
      <li>Honest-failure rate: reports vs bad PRs</li>
    </ul>
  </div>
</div>
<div class="thesis s2">Run the offline suite on every prompt, tool, and model change. <b>Variance is high</b>: report means over several runs, not one lucky pass.</div>
""",
"Evaluate both outcomes and trajectories. Offline, mine historical bug-fix commits that came with tests, and turn them into your own SWE-bench-style set. SWE-bench Verified, five hundred human-validated tasks, is a useful public reference, but your own repositories are what matter. Track resolve rate at pass at one, plus cost and time per task. Add trajectory metrics: tool errors, loops, and turns needed to reproduce the bug. And use an L L M judge for pull request quality, but only after calibrating it against human labels.",
"Online, track merge rate without major edits, human edit distance on merged pull requests, the thirty-day revert rate as a guardrail, and the honest-failure rate: how often the agent writes a report instead of a bad pull request. A rising honest-failure rate can be a good sign.",
"Run the offline suite on every prompt, tool, and model change. And remember that agent runs are high-variance. Report means over several runs, not one lucky pass, or you'll ship regressions that looked like wins.",
)

# ---------------------------------------------------------------- 12 Cost
slide("06 · Cost and latency", """
<h2>Where the money goes, and the levers</h2>
<div class="formula">C<sub>task</sub> ≈ Σ<sub>turns</sub> ( ctx<sub>uncached</sub> + r · ctx<sub>cached</sub> ) · p<sub>in</sub> + out · p<sub>out</sub></div>
<div class="grid3 mt">
  <div class="card v s1"><b>Prompt caching</b><span class="muted">Stable prefix; cache reads are a fraction of input price. Often the single biggest saving for agent loops.</span></div>
  <div class="card v s2"><b>Model routing</b><span class="muted">Small model for triage, search summaries, sub-agents; frontier model for planning and edits.</span></div>
  <div class="card v s3"><b>Smaller contexts</b><span class="muted">Compaction and just-in-time retrieval shrink every future turn, not just this one.</span></div>
  <div class="card v s4"><b>Parallel tool calls</b><span class="muted">Latency tracks the depth of the plan, not its width.</span></div>
  <div class="card v s4"><b>Early exit</b><span class="muted">Triage rejects unfixable tickets before the expensive loop starts.</span></div>
  <div class="card v s4"><b>Budget per ticket</b><span class="muted">Spend more on high-value tickets; cap the long tail.</span></div>
</div>
""",
"Cost follows from the arithmetic. The cost of a task is roughly the sum over turns of uncached context plus a discount factor r times cached context, all at the input price, plus output tokens at the output price. Every lever acts on a term in this formula.",
"Prompt caching is often the single biggest saving for agent loops, because the prefix is re-read every turn and cache reads cost a fraction of normal input. Keep the prefix stable to get it.",
"Model routing: a small model for triage, search summaries, and sub-agents, and a frontier model for planning and edits.",
"Smaller contexts: compaction and just-in-time retrieval shrink every future turn, not just the current one, so they compound.",
"Three more levers. Parallel tool calls, so latency tracks the depth of the plan, not its width. Early exit, where triage rejects tickets the agent can't fix before the expensive loop starts. And a budget per ticket, spending more on high-value work and capping the long tail.",
)

# ---------------------------------------------------------------- 13 Tradeoffs
slide("06 · Tradeoffs", """
<h2>Choosing the level of autonomy</h2>
<table class="tbl rate-tbl">
  <tr><th>Design</th><th>Predictability</th><th>Open-ended tasks</th><th>Cost</th><th>Latency</th><th>Debuggability</th></tr>
  <tr><td><b>Single call</b></td><td class="g">high</td><td class="b">weak</td><td class="g">low</td><td class="g">low</td><td class="g">easy</td></tr>
  <tr class="s1"><td><b>Workflow</b></td><td class="g">high</td><td class="m">medium</td><td class="g">low–med</td><td class="g">low–med</td><td class="g">easy</td></tr>
  <tr class="s2 hlrow"><td><b>Workflow + agentic core</b></td><td class="m">medium</td><td class="g">strong</td><td class="m">medium</td><td class="m">medium</td><td class="m">traces needed</td></tr>
  <tr class="s3"><td><b>Single agent</b></td><td class="m">medium</td><td class="g">strong</td><td class="m">medium–high</td><td class="m">medium</td><td class="m">traces needed</td></tr>
  <tr class="s4"><td><b>Multi-agent</b></td><td class="b">low</td><td class="g">strongest on breadth</td><td class="b">high (~15× chat)</td><td class="m">parallel helps</td><td class="b">hard</td></tr>
</table>
<div class="note s5">Qualitative ratings. Default: the least autonomy that meets the success metric; move right only when evals show the simpler design failing.</div>
""",
"Here's the tradeoff table for choosing autonomy. A single call is predictable, cheap, fast, and easy to debug, and weak on open-ended tasks.",
"A workflow keeps high predictability and debuggability, with medium capability on open-ended work.",
"The hybrid we designed, a workflow with an agentic core, is strong on open-ended tasks with medium cost and latency. It needs good traces to debug, which is the price of any autonomy.",
"A single free-running agent has similar capability, higher cost, and less structure around it.",
"Multi-agent systems are strongest on breadth, at high cost, around fifteen times a chat interaction by Anthropic's numbers. Parallelism helps latency, but debugging is hard and predictability is low.",
"These are qualitative ratings. My default: choose the least autonomy that meets the success metric, and move right only when your evals show the simpler design failing.",
)

# ---------------------------------------------------------------- 14 Harness code
slide("06 · Putting it together", """
<h2>The harness, in ~25 lines</h2>
<div class="panel code wide tight-code"><pre><span class="k">def</span> <span class="f">fix_ticket</span>(ticket, repo, budget):
    run = durable.<span class="f">resume_or_start</span>(ticket.id)              <span class="c"># checkpointed event log</span>
    box = sandbox.<span class="f">restore_or_clone</span>(run, repo)
    ctx = Context(prefix=[SYSTEM, TOOLS, repo.map()], notes=box.file(<span class="s">"NOTES.md"</span>))
    ctx.<span class="f">add</span>(ticket, <span class="s">"First write a failing test that reproduces the bug."</span>)
    <span class="k">while</span> budget.<span class="f">ok</span>():
        step = llm.<span class="f">step</span>(ctx)                                  <span class="c"># prefix cached</span>
        <span class="k">if</span> step.done:
            report = <span class="f">verify</span>(box)                              <span class="c"># new test red→green, suite green</span>
            <span class="k">if</span> report.ok: <span class="k">return</span> <span class="f">open_pr</span>(box, key=ticket.id)   <span class="c"># idempotent</span>
            ctx.<span class="f">add</span>(report.failures); <span class="k">continue</span>
        results = <span class="f">run_parallel</span>(step.tool_calls, box)         <span class="c"># bounded, instructive errors</span>
        ctx.<span class="f">add</span>(<span class="f">trim</span>(results)); run.<span class="f">record</span>(step, results)
        budget.<span class="f">charge</span>(step.usage)
        <span class="k">if</span> <span class="f">no_progress</span>(run):                              <span class="c"># same error ×3, no diff</span>
            ctx.<span class="f">add</span>(<span class="s">"Stuck. Re-read NOTES.md and try a different approach."</span>)
        <span class="k">if</span> ctx.tokens &gt; <span class="n">0.8</span> * ctx.limit:
            ctx.<span class="f">compact</span>()                                     <span class="c"># keep decisions, drop old output</span>
    <span class="k">return</span> <span class="f">failure_report</span>(run, box)                        <span class="c"># honest failure is an output</span></pre></div>
""",
"Here's the harness in about twenty-five lines. Resume or start a durable run keyed by the ticket, and restore or clone the sandbox. Build the context with a stable prefix of system prompt, tools, and repository map, plus the notes file. Tell the agent to write a failing test first. Then loop while the budget allows. Each step calls the model with a cached prefix. When the model says it's done, verify: the new test must go from red to green and the suite must stay green. If it passes, open the pull request idempotently. If not, feed the failures back and continue. Otherwise run tool calls in parallel, trim and add results, record the step, and charge the budget. If there's no progress, nudge the agent to re-read its notes and change approach. If context passes eighty percent of the limit, compact. And when the budget runs out, return an honest failure report. Every principle in this lesson is one line of this loop.",
)

# ---------------------------------------------------------------- 15 Recap
slide("Recap", """
<h2>Five things to take into your next design review</h2>
<ol class="recap">
  <li class="s1"><b>Least autonomy that works.</b> Workflow skeleton, agentic core only where paths are unpredictable.</li>
  <li class="s2"><b>Close the loop.</b> Machine-checkable success, budgets, no-progress detection, bounded retries.</li>
  <li class="s3"><b>Tools and context are the product.</b> Design tools as interfaces; treat context as a budget.</li>
  <li class="s4"><b>Parallelize reads, serialize writes.</b> Multi-agent buys breadth with tokens.</li>
  <li class="s5"><b>Durable, idempotent, evaluated.</b> Resume, never double-act, measure over many runs.</li>
</ol>
<div class="exercise s6"><b>Exercise:</b> take 30 past bug-fix commits with tests from one repo. Build the harness with 4 tools, run each task 3 times, and report resolve rate, cost per task, and the top 3 failure patterns from the traces.</div>
""",
"Let's recap with five things to take into your next design review.",
"One. Least autonomy that works: a workflow skeleton, with an agentic core only where the path is unpredictable.",
"Two. Close the loop: a machine-checkable success criterion, budgets, no-progress detection, and bounded retries.",
"Three. Tools and context are the product. Design tools as interfaces, and treat context as a budget.",
"Four. Parallelize reads, serialize writes. Multi-agent systems buy breadth with tokens.",
"Five. Durable, idempotent, and evaluated. Resume after failures, never act twice, and measure over many runs.",
"Your exercise: take thirty past bug-fix commits with tests from one repository. Build the harness with four tools, run each task three times, and report the resolve rate, cost per task, and the top three failure patterns you find in the traces. Those failure patterns are your roadmap. Thanks for watching.",
)
