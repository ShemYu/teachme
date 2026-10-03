# Lesson content: list of slides. Each slide = (section, html, [narration per step]).
# Elements with class "sN" appear at step N (1-based). Step 0 = base content only.

SLIDES = []

def slide(section, html, *steps):
    SLIDES.append((section, html, list(steps)))

# ---------------------------------------------------------------- 0 Title
slide("", """
<div class="title-wrap">
  <div class="kicker">Senior Applied AI Engineering · Deep Dive</div>
  <h1 class="big">Agentic Video<br>Understanding</h1>
  <p class="lede">From stuffing frames into a prompt, to an agent that <em>searches</em> video like an investigator.</p>
  <div class="agenda s1">
    <div><b>01</b> Why video breaks naive VLM pipelines</div>
    <div><b>02</b> Three system designs, one thesis</div>
    <div><b>03</b> Architecture: index offline, reason online</div>
    <div><b>04</b> Tools, search strategy, context engineering</div>
    <div><b>05</b> Grounding, verification, failure modes</div>
    <div><b>06</b> Evaluation and production economics</div>
  </div>
</div>
""",
"Welcome. This is a deep dive on agentic video understanding, pitched at the level of a senior applied A I engineer. The goal is not to tour papers. The goal is that by the end, you can design, evaluate, and ship a system that answers questions over hours of video, with timestamped evidence, at a cost you can defend in a design review.",
"Here's the plan. First, why video breaks the naive approach. Then three system designs and the one idea that separates them. Then the architecture: index offline, reason online. Then the parts that actually decide quality: tool design, search strategy, and context engineering. Then grounding and failure modes. And finally, evaluation and production economics.",
)

# ---------------------------------------------------------------- 1 Problem
slide("01 · The problem", """
<h2>Video is a token firehose</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">One hour of video, sampled at 1 fps</div>
    <table class="math">
      <tr><td>Frames</td><td class="num">3,600</td></tr>
      <tr><td>× ~258 tokens <span class="muted">(low-res frame)</span></td><td class="num">≈ 0.9 M</td></tr>
      <tr><td>× ~1,500 tokens <span class="muted">(~1 MP frame)</span></td><td class="num warn">≈ 5.4 M</td></tr>
      <tr><td>+ transcript <span class="muted">(~150 wpm)</span></td><td class="num">≈ 12 K</td></tr>
    </table>
    <div class="note">Speech is ~0.3% of the tokens — and often carries most of the answer.</div>
  </div>
  <div class="stack">
    <div class="card s1"><div class="ic red">$</div><div><b>Cost &amp; latency</b><br><span class="muted">Every question re-pays for the whole video.</span></div></div>
    <div class="card s2"><div class="ic red">≈</div><div><b>Attention dilution</b><br><span class="muted">Relevant evidence is a few seconds in an hour. Long-context recall degrades.</span></div></div>
    <div class="card s3"><div class="ic red">⌖</div><div><b>Sampling blindness</b><br><span class="muted">64 uniform frames over 1 h = one frame every 56 s.<br>A 2-second event is seen with probability <b class="warn">≈ 3.6%</b>.</span></div></div>
  </div>
</div>
""",
"Start with the arithmetic, because it drives every design decision. One hour of video at one frame per second is thirty-six hundred frames. At a low-resolution setting of roughly two hundred and fifty tokens per frame, that's close to a million tokens. At a megapixel per frame, which you need for reading text or small objects, it's over five million. Meanwhile the entire spoken transcript is about twelve thousand tokens. Notice that asymmetry: speech is a fraction of a percent of the tokens, and it often contains most of the answer.",
"So the first problem is cost and latency. If you put the video in the prompt, every single question pays for the entire hour again.",
"The second problem is attention dilution. The evidence for a typical question lives in a few seconds of an hour. Even models with million-token context windows show degraded recall when the needle is visual and the haystack is huge.",
"The third problem is the one people underestimate: sampling blindness. The common workaround is to sample a fixed number of frames uniformly, say sixty-four. Over an hour that's one frame every fifty-six seconds. A two-second event gets captured with probability around three and a half percent. The model isn't wrong about what it saw. It simply never saw the moment that matters.",
)

# ---------------------------------------------------------------- 2 Designs
slide("02 · Design space", """
<h2>Three designs, one thesis</h2>
<div class="cols3">
  <div class="panel col">
    <div class="tag">A · Single pass</div>
    <div class="flow">Uniform sample → VLM → answer</div>
    <ul><li class="good">Trivial to build</li><li class="good">Great for short clips</li><li class="bad">Blind to short events</li><li class="bad">Cost ∝ video length, per query</li></ul>
  </div>
  <div class="panel col s1">
    <div class="tag">B · Index + retrieve</div>
    <div class="flow">Caption everything offline → text RAG → LLM</div>
    <ul><li class="good">Cheap per query</li><li class="good">Scales to large libraries</li><li class="bad">Captions written <i>before</i> the question is known</li><li class="bad">Lossy: details never captioned are gone</li></ul>
  </div>
  <div class="panel col s2 hl">
    <div class="tag accent">C · Agentic</div>
    <div class="flow">Plan → call tools over index <b>and pixels</b> → verify → answer</div>
    <ul><li class="good">Question-conditioned perception</li><li class="good">Cost ∝ difficulty, not length</li><li class="good">Timestamped evidence</li><li class="bad">More moving parts; needs evals</li></ul>
  </div>
</div>
<div class="thesis s3">Thesis: <b>perception should be conditioned on the question.</b> An index finds <i>where</i> to look; the model then looks <i>closely</i>, for a reason.</div>
""",
"There are three broad designs. Design A is single pass: sample frames uniformly, send them to a vision language model, get an answer. It's trivial to build and genuinely excellent for clips under a few minutes. But it's blind to short events, and cost scales with video length on every query.",
"Design B is index and retrieve. You caption every segment offline, embed the captions, and at query time you do text retrieval augmented generation. It's cheap per query and scales to large libraries. The fatal flaw is subtle: the captions were written before anyone knew the question. If the captioner didn't mention the color of the second car, that information is gone forever.",
"Design C is agentic. A language model plans, calls tools that search the index, and critically, can go back to the raw pixels at a chosen time, frame rate, and resolution, with a specific question in mind. It verifies, then answers with timestamps. Cost scales with the difficulty of the question, not the length of the video. The price is more moving parts, which means you need real evaluation.",
"If you remember one sentence from this video, make it this one. Perception should be conditioned on the question. The index tells you where to look. The model then looks closely, for a reason. Everything else in this lesson is engineering in service of that idea.",
)

# ---------------------------------------------------------------- 3 Core loop
slide("02 · The core loop", """
<h2>The agent loop</h2>
<div class="loop">
  <div class="node q">Question</div>
  <div class="arrow">→</div>
  <div class="node s1">Plan<br><span class="muted sm">hypothesis + next probe</span></div>
  <div class="arrow s1">→</div>
  <div class="node s1">Act<br><span class="muted sm">tool call</span></div>
  <div class="arrow s1">→</div>
  <div class="node s2">Observe<br><span class="muted sm">write to evidence ledger</span></div>
  <div class="arrow s2">→</div>
  <div class="node s3 dec">Enough evidence?<br><span class="muted sm">calibrated, budget-aware</span></div>
  <div class="arrow s3">→</div>
  <div class="node a s3">Answer<br><span class="muted sm">+ timestamps</span></div>
</div>
<div class="back s3">↺ &nbsp;no → refine hypothesis, narrow window, raise fps / resolution</div>
<div class="grid2 mt s4">
  <div class="panel"><div class="label">State the agent carries</div><ul><li>Question + decomposition</li><li>Evidence ledger: claims ↔ (t₀, t₁, source)</li><li>Coverage map: which spans were inspected, at what fidelity</li><li>Budget remaining: tokens, seconds, tool calls</li></ul></div>
  <div class="panel"><div class="label">Precedent in the literature</div><ul><li><b>VideoAgent</b> — iterative frame selection gated by self-evaluated confidence</li><li><b>VideoTree</b> — adaptive, query-driven tree over clustered segments</li><li><b>Deep Video Discovery</b>-style agents — tool-based search over a segmented video database</li></ul></div>
</div>
""",
"Here's the core loop. A question comes in.",
"The agent plans: it forms a hypothesis about where the answer might be and picks the next probe. Then it acts, by calling a tool.",
"It observes the result, and this is important, it writes what it learned into an explicit evidence ledger rather than just letting raw tool output pile up in context.",
"Then it decides whether it has enough evidence. That decision must be calibrated and budget-aware. If yes, it answers, citing timestamps. If not, it loops: refine the hypothesis, narrow the time window, raise the frame rate or resolution.",
"The state the agent carries is worth making explicit in your implementation: the question and its decomposition, the evidence ledger linking each claim to a time span and a source, a coverage map of what's been inspected and at what fidelity, and the remaining budget. This pattern is well established. VideoAgent showed iterative frame selection gated by the model's own confidence, reaching strong accuracy with only a handful of frames. VideoTree built adaptive, query-driven trees over clustered segments. And more recent deep-video-discovery style agents treat the video as a database the agent searches with tools. The shared idea is adaptive, question-driven allocation of perception.",
)

# ---------------------------------------------------------------- 4 Architecture
slide("03 · Architecture", """
<h2>Index offline. Reason online.</h2>
<div class="arch">
  <div class="lane">
    <div class="lane-t">OFFLINE · once per video</div>
    <div class="row">
      <div class="box">Raw video<br><span class="sm muted">normalize → PTS clock</span></div>
      <div class="arrow">→</div>
      <div class="col-boxes">
        <div class="box sm2">Shot / scene detection</div>
        <div class="box sm2">ASR + diarization (word timestamps)</div>
        <div class="box sm2">OCR on keyframes</div>
        <div class="box sm2">Clip captions (VLM)</div>
        <div class="box sm2">Visual + text embeddings</div>
        <div class="box sm2">Entities / tracks (optional)</div>
      </div>
      <div class="arrow">→</div>
      <div class="box store">Multi-granular index<br><span class="sm muted">keyed by time span</span></div>
    </div>
  </div>
  <div class="lane s1">
    <div class="lane-t accentc">ONLINE · per question</div>
    <div class="row">
      <div class="box">Question</div>
      <div class="arrow">→</div>
      <div class="box agent">Agent (LLM)<br><span class="sm muted">plan · call tools · verify</span></div>
      <div class="arrow">⇄</div>
      <div class="col-boxes">
        <div class="box sm2">search / overview → <b>index</b></div>
        <div class="box sm2 hlb">look(t₀, t₁, fps, res) → <b>raw pixels</b></div>
      </div>
      <div class="arrow">→</div>
      <div class="box">Answer<br><span class="sm muted">+ cited spans</span></div>
    </div>
  </div>
</div>
""",
"The architecture has two phases. Offline, once per video, you normalize the file onto a single presentation-timestamp clock, and then run a set of extractors: shot or scene detection, speech recognition with word-level timestamps and speaker diarization, O C R on keyframes, short clip captions from a vision language model, visual and text embeddings, and optionally entity tracks. All of it lands in a multi-granular index keyed by time span.",
"Online, per question, the agent calls tools. Most tools read from the index: search, overview, transcripts. But one tool is different, and it's the reason this design beats pure retrieval. The look tool goes back to the raw pixels, for a chosen span, at a chosen frame rate and resolution. The index is a map. It is not the territory. Always keep the territory reachable.",
)

# ---------------------------------------------------------------- 5 Indexing
slide("03 · Indexing", """
<h2>Build a multi-granular memory</h2>
<div class="grid2">
  <div class="pyramid">
    <div class="lvl l1">Video summary <span class="muted">· 1</span></div>
    <div class="lvl l2">Scenes <span class="muted">· ~30–80</span></div>
    <div class="lvl l3">Clips, 4–10 s <span class="muted">· ~500–900</span></div>
    <div class="lvl l4">Frames <span class="muted">· on demand, never pre-captioned</span></div>
  </div>
  <div>
    <div class="panel code s1"><pre><span class="k">clip</span> = {
  <span class="s">"span"</span>:     [<span class="n">1843.2</span>, <span class="n">1851.0</span>],   <span class="c"># PTS seconds</span>
  <span class="s">"scene"</span>:    <span class="n">27</span>,
  <span class="s">"caption"</span>:  <span class="s">"person opens laptop at desk"</span>,
  <span class="s">"speech"</span>:   [{<span class="s">"spk"</span>: <span class="s">"S2"</span>, <span class="s">"text"</span>: ...}],
  <span class="s">"ocr"</span>:      [<span class="s">"Q3 REVENUE"</span>, ...],
  <span class="s">"v_emb"</span>:    <span class="c"># image-text space</span>,
  <span class="s">"t_emb"</span>:    <span class="c"># caption+speech+ocr</span>,
  <span class="s">"idx_ver"</span>:  <span class="s">"cap-v3/asr-v2"</span>
}</pre></div>
    <ul class="s2 tight">
      <li>Segment on <b>shot boundaries</b>, with a max length cap</li>
      <li><b>Time span is the join key</b> across every modality</li>
      <li>Keep captions <b>short and literal</b> — they are for recall, not answers</li>
      <li><b>Version the index</b>; re-index is a migration</li>
    </ul>
  </div>
</div>
""",
"Let's zoom into the index. Think of it as a pyramid. One summary for the whole video. Dozens of scenes. Hundreds of short clips of four to ten seconds. And frames at the bottom, which you do not pre-caption. Frames are fetched on demand, at query time, because only the question tells you what's worth describing.",
"Each clip record carries its time span in presentation-timestamp seconds, its scene, a short caption, the speech in that span with speaker labels, any on-screen text, a visual embedding in a shared image-text space, a text embedding over caption plus speech plus O C R, and an index version.",
"A few senior-level rules. Segment on shot boundaries, with a maximum length cap, instead of fixed windows that cut actions in half. Treat the time span as the universal join key: every modality aligns through it. Keep captions short and literal, because their job is recall, not answering. And version the index. When you upgrade the captioner, re-indexing is a data migration, and your eval numbers need to know which version they were measured on.",
)

# ---------------------------------------------------------------- 6 Tools
slide("04 · Tool design", """
<h2>Tools are the agent's senses</h2>
<div class="panel code wide"><pre><span class="k">search</span>(query, modality=[<span class="s">"visual"</span>,<span class="s">"speech"</span>,<span class="s">"ocr"</span>], k=<span class="n">8</span>)   <span class="c">→ [(t0, t1, score, snippet)]</span>
<span class="k">overview</span>(level=<span class="s">"scene"</span>, span=<span class="k">None</span>)                     <span class="c">→ hierarchical summaries</span>
<span class="k">transcript</span>(t0, t1)                                   <span class="c">→ diarized words</span>
<span class="k">look</span>(t0, t1, question, fps=<span class="n">1</span>, res=<span class="s">"low"</span>, crop=<span class="k">None</span>)   <span class="c">→ answer + frame refs  ← pixels</span>
<span class="k">read_text</span>(t, region=<span class="k">None</span>)                           <span class="c">→ OCR at full resolution</span></pre></div>
<div class="grid3 mt">
  <div class="card v s1"><b>Always return time spans</b><span class="muted">Every observation must be citable and re-inspectable.</span></div>
  <div class="card v s2"><b>Expose fidelity knobs</b><span class="muted">fps, resolution, crop. Let the agent trade cost for detail explicitly.</span></div>
  <div class="card v s3"><b>Make <i>look</i> question-conditioned</b><span class="muted">The VLM receives a sub-question, not "describe this".</span></div>
  <div class="card v s4"><b>Bound every output</b><span class="muted">Hard caps on k, span length, frames. Return cost in the result.</span></div>
  <div class="card v s4"><b>Deterministic + cached</b><span class="muted">Key on (video, span, fps, res, prompt hash).</span></div>
  <div class="card v s4"><b>Errors are observations</b><span class="muted">"Span too long, max 120 s" teaches the agent.</span></div>
</div>
""",
"Tools are the agent's senses, so tool design is where most of your quality comes from. A solid starting set is five tools. Search, over visual, speech and O C R modalities, returning time spans with scores and snippets. Overview, for hierarchical summaries. Transcript, for diarized speech in a span. Look, which sends raw frames from a span to a vision model along with a specific question. And read text, for full-resolution O C R when small text matters.",
"Design principles. First: always return time spans. Every observation must be citable and re-inspectable.",
"Second: expose fidelity knobs. Frame rate, resolution, and crop let the agent trade cost for detail explicitly, instead of you hard-coding one tradeoff for all questions.",
"Third: make look question-conditioned. The vision model should receive a precise sub-question, like, what number is on the jersey of the player holding the ball, not, describe this clip. This is the thesis, implemented.",
"And finally, the hygiene rules. Bound every output with hard caps, and return the cost of the call in the result so the agent can reason about budget. Make tools deterministic and cache them by video, span, frame rate, resolution, and prompt hash. And return errors as instructive observations. An error that says, span too long, maximum one hundred twenty seconds, teaches the agent how to use the tool.",
)

# ---------------------------------------------------------------- 7 Search strategy
slide("04 · Search strategy", """
<h2>Coarse-to-fine search</h2>
<div class="timeline-wrap">
  <div class="tl-row"><div class="tl-label">1 · Skim</div><div class="tl"><div class="seg all"></div></div><div class="tl-note">overview + transcript · text only · cheap</div></div>
  <div class="tl-row s1"><div class="tl-label">2 · Retrieve</div><div class="tl"><div class="seg c" style="left:12%;width:4%"></div><div class="seg c" style="left:41%;width:5%"></div><div class="seg c" style="left:63%;width:3%"></div><div class="seg c" style="left:84%;width:4%"></div></div><div class="tl-note">multi-query search → candidate spans</div></div>
  <div class="tl-row s2"><div class="tl-label">3 · Sparse look</div><div class="tl"><div class="seg d" style="left:41%;width:5%"></div><div class="seg d" style="left:63%;width:3%"></div><div class="seg x" style="left:12%;width:4%"></div><div class="seg x" style="left:84%;width:4%"></div></div><div class="tl-note">1 fps, low-res · prune candidates</div></div>
  <div class="tl-row s3"><div class="tl-label">4 · Dense look</div><div class="tl"><div class="seg e" style="left:42.5%;width:1.2%"></div></div><div class="tl-note">4–8 fps, high-res, crop · extract</div></div>
  <div class="tl-row s4"><div class="tl-label">5 · Verify</div><div class="tl"><div class="seg v" style="left:42.5%;width:1.2%"></div></div><div class="tl-note">fresh, neutral prompt · confirm or abstain</div></div>
</div>
<div class="note s4">Also: <b>anchor-then-relative</b> for temporal questions — find “after the speaker mentions pricing” first, then search the window after it.</div>
""",
"The default search strategy is coarse to fine. Step one, skim. Read the overview and transcript. It's text only, so it's cheap, and it often localizes the answer on its own.",
"Step two, retrieve. Issue several reformulated queries across modalities, and collect candidate spans. Multiple phrasings matter, because visual embeddings are brittle to wording.",
"Step three, a sparse look at each candidate: one frame per second, low resolution. The goal here is pruning, not answering. Two of our four candidates are ruled out, and two survive.",
"Step four, dense look at the most promising survivor: several frames per second, high resolution, and a crop if the detail is small. Now you extract the answer.",
"Step five, verify, with a fresh, neutral prompt, and either confirm or abstain. A related pattern for temporal questions is anchor then relative: if the question says, after the speaker mentions pricing, find that anchor first, then search the window that follows it. Notice the budget shape: most spend lands on a few seconds of video, which is exactly where the answer is.",
)

# ---------------------------------------------------------------- 8 Question routing
slide("04 · Routing", """
<h2>The question type decides the plan</h2>
<table class="tbl">
  <tr><th>Question type</th><th>Example</th><th>Strategy</th></tr>
  <tr><td><b>Needle</b></td><td class="muted">“What brand was the laptop?”</td><td>retrieve → sparse → dense look</td></tr>
  <tr class="s1 warnrow"><td><b>Counting / aggregation</b></td><td class="muted">“How many times does she refill the cup?”</td><td><b>exhaustive map-reduce scan</b>, not top-k retrieval</td></tr>
  <tr class="s2"><td><b>Temporal order</b></td><td class="muted">“What happens right after the alarm?”</td><td>anchor → relative window</td></tr>
  <tr class="s2"><td><b>Causal / why</b></td><td class="muted">“Why did the demo fail?”</td><td>event + preceding context + transcript</td></tr>
  <tr class="s2"><td><b>Summary / gist</b></td><td class="muted">“What were the main decisions?”</td><td>hierarchical overview, little pixel work</td></tr>
</table>
<div class="thesis s1">Top-k retrieval <b>systematically undercounts</b>. If k=8 and the event happens 11 times, the agent is guaranteed to be wrong — confidently.</div>
""",
"A single strategy won't serve all questions, so route on question type. A needle question, like what brand was the laptop, is the coarse to fine search we just saw.",
"Counting and aggregation questions are where retrieval-based agents quietly fail. How many times does she refill the cup? If your search returns the top eight spans and the event happens eleven times, the agent is guaranteed to be wrong, and it will be confident about it. Counting needs exhaustive coverage: a map-reduce scan over every segment, often with parallel sub-agents, then a deduplication step, because the same event can straddle two clips.",
"Temporal order questions use anchor then relative. Causal questions need the event plus the context before it, and usually the transcript. And summary questions are mostly served by the hierarchical overview with very little pixel work. In practice, have the planner classify the question first, and make that classification visible in your traces so you can evaluate routing separately from answering.",
)

# ---------------------------------------------------------------- 9 Context engineering
slide("04 · Context engineering", """
<h2>Context engineering: pixels in, notes out</h2>
<div class="grid2">
  <div>
    <div class="card s0"><div class="ic">1</div><div><b>Frames are the expensive tokens</b><br><span class="muted">Resolution × count is the real budget. Few sharp frames often beat many blurry ones.</span></div></div>
    <div class="card s1"><div class="ic">2</div><div><b>Read once, then compress</b><br><span class="muted">Raw frames live inside the <i>look</i> call. The main agent sees only the textual finding.</span></div></div>
    <div class="card s2"><div class="ic">3</div><div><b>Sub-agents for breadth</b><br><span class="muted">Parallel scanners over segments; orchestrator reduces. Isolates context, cuts latency.</span></div></div>
    <div class="card s3"><div class="ic">4</div><div><b>Stable prefix, cached</b><br><span class="muted">System prompt + tool schemas + video overview first; prompt-cache them.</span></div></div>
  </div>
  <div class="panel code s1"><div class="label">Evidence ledger (what stays in context)</div><pre>[
 {<span class="s">"claim"</span>: <span class="s">"laptop logo is a silver apple"</span>,
  <span class="s">"span"</span>: [<span class="n">1843.2</span>, <span class="n">1845.0</span>],
  <span class="s">"via"</span>: <span class="s">"look@6fps,high,crop"</span>,
  <span class="s">"conf"</span>: <span class="n">0.86</span>},
 {<span class="s">"claim"</span>: <span class="s">"no laptop visible 1200–1800s"</span>,
  <span class="s">"span"</span>: [<span class="n">1200</span>, <span class="n">1800</span>],
  <span class="s">"via"</span>: <span class="s">"look@0.5fps,low"</span>,
  <span class="s">"conf"</span>: <span class="n">0.6</span>}   <span class="c"># negative evidence</span>
]</pre></div>
</div>
""",
"Now context engineering, which is where agentic video systems usually win or lose. Principle one: frames are the expensive tokens. Resolution times count is the real budget, and a few sharp frames often beat many blurry ones.",
"Principle two: read once, then compress. Raw frames should live inside the look call. The main agent should only see the textual finding, written into the evidence ledger. Notice the ledger records negative evidence too, like no laptop visible in this span at low fidelity, with its confidence. That's what stops the agent from re-searching ground it already covered, and it tells the agent when a negative might be worth re-checking at higher fidelity.",
"Principle three: use sub-agents for breadth. For exhaustive scans, fan out parallel scanners over segments, each with its own clean context, and let an orchestrator reduce their findings. This isolates context and cuts wall-clock latency.",
"Principle four: keep a stable prefix. System prompt, tool schemas, and the video overview go first and get prompt-cached, so repeated questions over the same video don't re-pay for them.",
)

# ---------------------------------------------------------------- 10 Grounding
slide("05 · Grounding & failure modes", """
<h2>Grounding, verification, and how it breaks</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Verification pass</div>
    <ul>
      <li>Every claim in the answer cites a span from the ledger</li>
      <li>Re-look cited spans with a <b>neutral</b> prompt:<br><span class="muted">“What is on the laptop lid?” — not “Confirm it's an Apple logo.”</span></li>
      <li>Disagreement → one more probe, or <b>abstain</b></li>
      <li>Abstention is a feature; measure it</li>
    </ul>
  </div>
  <div class="stack s1">
    <div class="card"><div class="ic red">⏱</div><div><b>Timestamp drift</b><br><span class="muted">VFR video, container offsets, audio/video skew. Normalize to PTS at ingest.</span></div></div>
    <div class="card s2"><div class="ic red">⇆</div><div><b>Modality conflict</b><br><span class="muted">Speech says “red”, pixels show blue. Decide a policy; surface the conflict.</span></div></div>
    <div class="card s3"><div class="ic red">◎</div><div><b>Confirmation bias</b><br><span class="muted">Leading prompts to <i>look</i> make VLMs agree. Keep sub-questions neutral.</span></div></div>
    <div class="card s4"><div class="ic red">∞</div><div><b>Looping &amp; early stops</b><br><span class="muted">Coverage map + budget caps; calibrate the stop decision on evals.</span></div></div>
  </div>
</div>
""",
"Grounding is what makes the system trustworthy. Every claim in the final answer must cite a span from the ledger. Then run a verification pass: re-look at the cited spans with a neutral prompt. Ask, what is on the laptop lid, not, confirm it's an Apple logo. If verification disagrees, spend one more probe or abstain. Abstention is a feature, and you should measure its rate.",
"Now the failure modes you will actually hit. Timestamp drift: variable frame rate video, container offsets, and audio-video skew will make your citations off by seconds. Normalize everything to presentation timestamps at ingest, and test it.",
"Modality conflict: the speaker says red, the pixels show blue. Decide a policy per domain, and surface the conflict rather than silently picking one.",
"Confirmation bias: vision models are agreeable. A leading sub-question makes them see what you asked about. Keep look prompts neutral, especially during verification.",
"And looping and early stops: agents re-search the same span, or stop after one plausible hit. The coverage map plus hard budget caps fix looping. The early-stop threshold must be calibrated against your evals, not guessed.",
)

# ---------------------------------------------------------------- 11 Evaluation
slide("06 · Evaluation", """
<h2>Evaluate like you mean it</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Public benchmarks (orientation, not truth)</div>
    <ul class="tight">
      <li><b>QA, long-form:</b> EgoSchema, Video-MME, MLVU, LongVideoBench, LVBench</li>
      <li><b>Temporal grounding:</b> Charades-STA, QVHighlights</li>
    </ul>
    <div class="label mt">Baselines you must run</div>
    <ul class="tight s1">
      <li><b>Blind</b>: question only, no video → measures language-prior leakage</li>
      <li><b>Single frame</b> → is temporal reasoning even needed?</li>
      <li><b>Uniform sampling at equal token budget</b> → does agency pay?</li>
    </ul>
  </div>
  <div class="panel s2">
    <div class="label">Metrics per run</div>
    <ul class="tight">
      <li>Accuracy, split by question type</li>
      <li>Evidence recall / temporal IoU vs gold spans</li>
      <li>Tokens and $ per query · p50 / p95 latency</li>
      <li>Tool calls, frames inspected, abstain rate</li>
    </ul>
    <div class="pareto s3">
      <svg viewBox="0 0 420 170" width="100%"><line x1="40" y1="140" x2="410" y2="140" stroke="var(--muted)"/><line x1="40" y1="140" x2="40" y2="10" stroke="var(--muted)"/>
      <text x="220" y="165" fill="var(--muted)" font-size="13" text-anchor="middle">$ per query →</text><text x="14" y="80" fill="var(--muted)" font-size="13" transform="rotate(-90 14 80)" text-anchor="middle">accuracy →</text>
      <polyline points="70,118 150,82 250,62 380,55" fill="none" stroke="var(--accent)" stroke-width="3"/>
      <circle cx="70" cy="118" r="6" fill="var(--accent)"/><circle cx="150" cy="82" r="6" fill="var(--accent)"/><circle cx="250" cy="62" r="6" fill="var(--accent)"/><circle cx="380" cy="55" r="6" fill="var(--accent)"/>
      <circle cx="330" cy="100" r="6" fill="var(--red)"/><text x="340" y="104" fill="var(--red)" font-size="13">uniform</text>
      <text x="175" y="112" fill="var(--accent)" font-size="13">agent configs</text></svg>
    </div>
  </div>
</div>
""",
"Evaluation. Public benchmarks are useful for orientation: EgoSchema, Video M M E, M L V U, LongVideoBench and L V Bench for long-form question answering, and Charades S T A and Q V Highlights for temporal grounding. But they are not your product's truth. Build an in-domain set, even thirty to fifty questions on your own videos, with gold answers and gold evidence spans.",
"Then run three baselines that most teams skip. The blind baseline: question only, no video at all. On many benchmarks this scores far above chance, which tells you how much of your accuracy is language prior rather than seeing. The single-frame baseline, which tells you whether temporal reasoning is even required. And uniform sampling at an equal token budget, which is the honest test of whether agency is paying for itself.",
"For metrics, track accuracy split by question type, evidence recall or temporal I o U against the gold spans, tokens and dollars per query, median and tail latency, tool calls, frames inspected, and abstain rate. A correct answer with the wrong evidence span is a lucky guess, and it will not survive distribution shift.",
"Finally, plot accuracy against cost. Each agent configuration, budget cap, model choice, fidelity policy, is a point, and what you ship is a point on the Pareto frontier that matches your product's constraints. If uniform sampling sits on or above your frontier, your agent isn't earning its complexity yet.",
)

# ---------------------------------------------------------------- 12 Production
slide("06 · Production", """
<h2>Production economics</h2>
<div class="formula">C<sub>query</sub> = C<sub>index</sub> / N<sub>queries per video</sub> + Σ C<sub>tool calls</sub> + C<sub>reasoning</sub></div>
<div class="grid3 mt">
  <div class="card v s1"><b>Amortize the index</b><span class="muted">Index once, ask many. If N is ~1, index lazily: only the spans the agent touches.</span></div>
  <div class="card v s2"><b>Model cascade</b><span class="muted">Small, cheap VLM for skim and prune; strong model for dense look, reasoning, and verify.</span></div>
  <div class="card v s2"><b>Parallelism</b><span class="muted">Fan out candidate looks concurrently; latency ≈ depth of the plan, not its width.</span></div>
  <div class="card v s3"><b>Cache everything</b><span class="muted">Tool results keyed by span + fidelity + prompt hash; prompt-cache the stable prefix.</span></div>
  <div class="card v s4"><b>Streaming video</b><span class="muted">Sliding windows, event triggers, rolling summaries as memory; latency SLO per event.</span></div>
  <div class="card v s4"><b>Trust &amp; safety</b><span class="muted">Faces, screens, PII in frames and speech. Retention policy on the index, not just the video.</span></div>
</div>
""",
"Production economics come down to one formula. The cost per query is the indexing cost divided by the number of queries per video, plus the sum of tool-call costs, plus reasoning.",
"So first, amortize the index. If each video gets many questions, index eagerly. If each video gets roughly one question, index lazily, only the spans the agent actually touches, because eager indexing would dominate your bill.",
"Second, use a model cascade: a small, cheap vision model for skimming and pruning, and a strong model for dense looks, reasoning, and verification. Third, parallelize. Fan out candidate looks concurrently, so latency tracks the depth of the plan, not its width.",
"Fourth, cache everything: tool results keyed by span, fidelity, and prompt hash, and prompt-cache the stable prefix.",
"Two more. For live, streaming video, the pattern shifts to sliding windows, event triggers, and rolling summaries as memory, with a latency objective per event. And trust and safety: video is dense with faces, screens, and personal data, in both pixels and speech. Your retention policy must cover the index and its captions, not just the original file.",
)

# ---------------------------------------------------------------- 13 Code
slide("06 · Putting it together", """
<h2>The loop, in ~25 lines</h2>
<div class="panel code wide tight-code"><pre><span class="k">def</span> <span class="f">answer</span>(video, question, budget):
    idx    = index.<span class="f">get_or_build</span>(video)                <span class="c"># offline, cached</span>
    route  = <span class="f">classify</span>(question)                       <span class="c"># needle | count | temporal | causal | summary</span>
    ledger, coverage = Ledger(), Coverage(video.duration)
    ctx = [SYSTEM, TOOL_SCHEMAS, idx.overview(), question, route]   <span class="c"># cached prefix</span>

    <span class="k">while</span> budget.ok():
        step = llm.<span class="f">next_action</span>(ctx, ledger.summary(), coverage.summary(), budget)
        <span class="k">if</span> step.kind == <span class="s">"answer"</span>:
            draft = step.answer
            <span class="k">if</span> <span class="f">verify</span>(draft, ledger, idx, neutral=<span class="k">True</span>):   <span class="c"># re-look cited spans</span>
                <span class="k">return</span> draft.with_citations()
            ctx.append(<span class="s">"verification failed: "</span> + draft.conflicts)
            <span class="k">continue</span>
        results = <span class="f">run_parallel</span>(step.tool_calls, cache=True)  <span class="c"># bounded, cost-reported</span>
        <span class="k">for</span> r <span class="k">in</span> results:
            ledger.<span class="f">add</span>(r.claims)                         <span class="c"># text notes, not frames</span>
            coverage.<span class="f">mark</span>(r.span, r.fidelity)
            budget.<span class="f">charge</span>(r.cost)

    <span class="k">return</span> <span class="f">abstain_or_best_effort</span>(ledger)                <span class="c"># explicit, measured</span></pre></div>
""",
"Here's the whole design as roughly twenty-five lines of pseudocode. Get or build the index, which is cached. Classify the question to pick a route. Initialize the ledger and coverage map, and build a context whose prefix, system prompt, tool schemas, and video overview, is stable and cached. Then loop while budget remains. The model picks the next action given the ledger summary, coverage summary, and remaining budget. If it wants to answer, verify first by re-looking at cited spans with neutral prompts, and only return on success. Otherwise, run the tool calls in parallel with caching, and write claims, not frames, into the ledger, mark coverage with fidelity, and charge the budget. When the budget runs out, abstain or return a clearly labeled best effort. Every line here corresponds to a principle from earlier in the lesson.",
)

# ---------------------------------------------------------------- 14 Recap
slide("Recap", """
<h2>Five things to take into your next design review</h2>
<ol class="recap">
  <li class="s1"><b>Condition perception on the question.</b> Index to find <i>where</i>; look at pixels to learn <i>what</i>.</li>
  <li class="s2"><b>Time spans are the universal key</b> — for joins, citations, caching, and coverage.</li>
  <li class="s3"><b>Route by question type.</b> Retrieval for needles; exhaustive map-reduce for counting.</li>
  <li class="s4"><b>Pixels in, notes out.</b> An evidence ledger with negative evidence is your context strategy.</li>
  <li class="s5"><b>Prove agency pays</b> against blind and equal-budget uniform baselines, on a Pareto plot.</li>
</ol>
<div class="exercise s6"><b>Exercise:</b> take one 1-hour video. Build the index and the five tools. Write 30 questions with gold spans across all five types. Beat uniform sampling at equal cost — and find which question type your agent still fails.</div>
""",
"Let's recap with five things to bring into your next design review.",
"One. Condition perception on the question. The index finds where. The pixels tell you what.",
"Two. Time spans are the universal key: for joining modalities, for citations, for caching, and for coverage.",
"Three. Route by question type. Retrieval for needles. Exhaustive map-reduce for counting.",
"Four. Pixels in, notes out. An evidence ledger, including negative evidence, is your context strategy.",
"Five. Prove that agency pays, against the blind baseline and against uniform sampling at an equal budget, on a Pareto plot.",
"Your exercise: take one hour-long video. Build the index and the five tools. Write thirty questions with gold evidence spans, covering all five question types. Beat uniform sampling at equal cost, and then find the question type your agent still fails on. That failure is your next design iteration. Thanks for watching.",
)
