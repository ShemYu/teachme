TITLE = "HybridRAG vs WikiRAG"

SLIDES = []

def slide(section, html, *steps):
    SLIDES.append((section, html, list(steps)))

# ---------------------------------------------------------------- 0 Title
slide("", """
<div class="title-wrap">
  <div class="kicker">Senior Applied AI Engineering · Deep Dive</div>
  <h1 class="big">HybridRAG<br>vs WikiRAG</h1>
  <p class="lede">Fuse many retrievers at query time, or <em>compile</em> knowledge ahead of time? Where each wins, what it costs, and how to choose.</p>
  <div class="agenda s1">
    <div><b>01</b> Why plain vector RAG fails, precisely</div>
    <div><b>02</b> HybridRAG: two meanings, one idea</div>
    <div><b>03</b> WikiRAG: compile, then navigate</div>
    <div><b>04</b> Tradeoffs against every other option</div>
    <div><b>05</b> A decision framework and a layered design</div>
    <div><b>06</b> Evaluation that doesn't lie to you</div>
  </div>
</div>
""",
"Welcome. This lesson compares two retrieval architectures, HybridRAG and WikiRAG, at the level a senior applied A I engineer needs to make a design decision. We'll also put them side by side with the alternatives: long context, plain vector search, knowledge graphs, and GraphRAG.",
"Here's the plan. First, exactly how plain vector RAG fails, because each failure motivates a different fix. Then HybridRAG, which has two meanings worth separating. Then WikiRAG, which compiles knowledge ahead of time and lets an agent navigate it. Then the tradeoffs, a decision framework, and how to evaluate without fooling yourself.",
)

# ---------------------------------------------------------------- 1 Failure modes
slide("01 · The problem", """
<h2>Four ways vector RAG fails</h2>
<div class="grid2">
  <div class="stack">
    <div class="card"><div class="ic red">#</div><div><b>Exact-match misses</b><br><span class="muted">“ERR_4012”, “SKU-88A”, a person's name. Embeddings blur rare tokens.</span></div></div>
    <div class="card s1"><div class="ic red">⤳</div><div><b>Multi-hop gaps</b><br><span class="muted">“Who audits the supplier of our top vendor?” No single chunk holds the answer.</span></div></div>
    <div class="card s2"><div class="ic red">∑</div><div><b>Global questions</b><br><span class="muted">“What are the recurring themes across 400 reports?” Top-k is the wrong shape.</span></div></div>
    <div class="card s3"><div class="ic red">✂</div><div><b>Chunking destroys context</b><br><span class="muted">Pronouns, tables, and definitions get cut away from what they refer to.</span></div></div>
  </div>
  <div class="panel s4">
    <div class="label">Failure → fix family</div>
    <table class="tbl">
      <tr><th>Failure</th><th>Typical fix</th></tr>
      <tr><td>Exact match</td><td><b>Hybrid search</b> (BM25 + dense)</td></tr>
      <tr><td>Multi-hop</td><td><b>Graph</b> or <b>wiki</b> links</td></tr>
      <tr><td>Global</td><td><b>Pre-built summaries</b> (GraphRAG, wiki index pages)</td></tr>
      <tr><td>Chunk context</td><td><b>Compilation</b> or contextual chunks</td></tr>
    </table>
  </div>
</div>
""",
"Let's be precise about how plain vector RAG fails. First, exact-match misses. Error codes, product I Ds, and names are rare tokens, and dense embeddings blur them. The query for error forty twelve retrieves chunks about errors in general.",
"Second, multi-hop gaps. Who audits the supplier of our top vendor? The answer needs three facts from three documents, and no single chunk is similar to the whole question.",
"Third, global questions. What are the recurring themes across four hundred reports? Retrieving the top eight chunks is simply the wrong shape of operation for a question about the whole corpus.",
"Fourth, chunking destroys context. A chunk that says, it was discontinued in March, has lost what it refers to. Tables and definitions get separated from the text that explains them.",
"Map each failure to its fix family. Exact match is fixed by hybrid search. Multi-hop is fixed by explicit links, either a graph or a wiki. Global questions need summaries built ahead of time. And chunk context is fixed by compiling knowledge into self-contained units. Hold on to this table, because HybridRAG and WikiRAG sit in different rows of it.",
)

# ---------------------------------------------------------------- 2 Two meanings
slide("02 · HybridRAG", """
<h2>HybridRAG means two things</h2>
<div class="grid2">
  <div class="panel">
    <div class="tag" style="font-size:28px;font-weight:700;margin-bottom:14px">A · Hybrid <i>search</i></div>
    <div class="flow">BM25 (lexical) + dense (semantic) → fuse → rerank</div>
    <ul><li class="good">Fixes exact-match misses</li><li class="good">Cheap, well understood, incremental</li><li class="bad">Still chunk-shaped; no multi-hop</li></ul>
  </div>
  <div class="panel s1">
    <div class="tag" style="font-size:28px;font-weight:700;margin-bottom:14px">B · Graph + vector</div>
    <div class="flow">Knowledge-graph triples + vector chunks → merged context<br><span class="muted">Sarmah et al., “HybridRAG”, 2024 (financial filings)</span></div>
    <ul><li class="good">Relations enable multi-hop</li><li class="good">Beat vector-only and graph-only in the paper</li><li class="bad">Extraction + entity resolution cost</li></ul>
  </div>
</div>
<div class="thesis s2">Common idea: <b>no single retrieval signal is sufficient</b> — combine signals whose failures are uncorrelated.</div>
""",
"HybridRAG is used for two different designs, and conflating them causes bad decisions. Meaning A is hybrid search: run lexical B M 25 and dense vector retrieval in parallel, fuse the ranked lists, and rerank. It fixes exact-match misses, it's cheap, well understood, and updates incrementally. But it's still chunk-shaped, so it doesn't solve multi-hop.",
"Meaning B comes from the HybridRAG paper by Sarmah and colleagues in twenty twenty-four, on financial earnings-call transcripts. It retrieves from a knowledge graph of extracted triples and from a vector index, and merges both into the context. In their evaluation it beat both vector-only and graph-only retrieval. The cost is extraction and entity resolution, which we'll come back to.",
"The common idea is worth stating as a principle. No single retrieval signal is sufficient, so combine signals whose failures are uncorrelated. Lexical fails on paraphrase, dense fails on rare tokens, and graphs fail on anything that wasn't extracted.",
)

# ---------------------------------------------------------------- 3 Hybrid search mechanics
slide("02 · Hybrid search", """
<h2>Hybrid search, done properly</h2>
<div class="loop">
  <div class="node q">Query</div><div class="arrow">→</div>
  <div class="node">BM25<br><span class="muted sm">top 50–100</span></div>
  <div class="node">Dense<br><span class="muted sm">top 50–100</span></div><div class="arrow">→</div>
  <div class="node dec">RRF fuse</div><div class="arrow">→</div>
  <div class="node s1">Cross-encoder<br><span class="muted sm">rerank → top 5–10</span></div><div class="arrow s1">→</div>
  <div class="node a s1">LLM</div>
</div>
<div class="grid2 mt">
  <div class="panel code s2"><div class="label">Reciprocal rank fusion</div><pre><span class="k">def</span> <span class="f">rrf</span>(rankings, k=<span class="n">60</span>):
    score = defaultdict(float)
    <span class="k">for</span> ranked <span class="k">in</span> rankings:            <span class="c"># bm25, dense, ...</span>
        <span class="k">for</span> rank, doc <span class="k">in</span> enumerate(ranked, <span class="n">1</span>):
            score[doc] += <span class="n">1</span> / (k + rank)    <span class="c"># ranks, not scores</span>
    <span class="k">return</span> sorted(score, key=score.get, reverse=<span class="k">True</span>)</pre></div>
  <ul class="s3 tight">
    <li><b>Fuse ranks, not raw scores</b> — BM25 and cosine live on different scales</li>
    <li><b>Recall first, precision second</b> — wide candidate pools, then rerank</li>
    <li><b>Tokenize for the language</b> — BM25 on Chinese or Japanese needs a real segmenter</li>
    <li><b>Contextual chunks</b> — prepend doc title / section to each chunk before indexing</li>
    <li><b>Ablate</b> each retriever; keep only those that add recall</li>
  </ul>
</div>
""",
"Here's hybrid search done properly. The query goes to B M 25 and to dense retrieval in parallel, each returning a wide pool of fifty to a hundred candidates. The lists are fused with reciprocal rank fusion.",
"Then a cross-encoder reranker scores query and passage together and keeps the top five to ten for the model. Rerankers are where much of the precision comes from, and also much of the latency.",
"Reciprocal rank fusion is five lines. Each document scores one over k plus its rank, summed across retrievers, with k commonly sixty. The key design choice is that it fuses ranks, not raw scores.",
"That's the first senior rule: B M 25 scores and cosine similarities live on different scales, so weighted score averaging is fragile, and rank fusion is robust. Second, optimize recall first with wide pools, then precision with the reranker. Third, tokenize for the language: B M 25 over Chinese or Japanese without a proper segmenter quietly fails. Fourth, contextual chunks: prepend the document title and section heading to each chunk before indexing, which recovers much of the lost context cheaply. And fifth, ablate. Keep a retriever only if it measurably adds recall.",
)

# ---------------------------------------------------------------- 4 KG + vector
slide("02 · Graph + vector", """
<h2>Graph + vector HybridRAG</h2>
<div class="arch">
  <div class="lane">
    <div class="lane-t">INDEX TIME</div>
    <div class="row">
      <div class="box">Documents</div><div class="arrow">→</div>
      <div class="col-boxes"><div class="box sm2">LLM extracts (entity, relation, entity) triples</div><div class="box sm2 hlb">Entity resolution: “Apple Inc.” = “Apple” ≠ apple</div></div>
      <div class="arrow">→</div>
      <div class="box store">Knowledge graph<br><span class="sm muted">+ vector index of chunks</span></div>
    </div>
  </div>
  <div class="lane s1">
    <div class="lane-t accentc">QUERY TIME</div>
    <div class="row">
      <div class="box">Query</div><div class="arrow">→</div>
      <div class="col-boxes"><div class="box sm2">Link entities in the query → expand 1–2 hops</div><div class="box sm2">Vector search for supporting chunks</div></div>
      <div class="arrow">→</div>
      <div class="box agent">Merged context<br><span class="sm muted">triples + passages</span></div>
    </div>
  </div>
</div>
<div class="grid2 mt s2">
  <div class="card"><div class="ic">+</div><div><b>Wins</b><br><span class="muted">Relational multi-hop, aggregation over typed edges, auditable paths.</span></div></div>
  <div class="card"><div class="ic red">−</div><div><b>Costs</b><br><span class="muted">Schema design, extraction errors, entity resolution drift, graph goes stale.</span></div></div>
</div>
""",
"Now the graph plus vector variant. At index time, a language model extracts entity, relation, entity triples from each document. The step that decides quality is entity resolution: Apple Incorporated and Apple must merge into one node, and the fruit must not. Everything lands in a knowledge graph alongside an ordinary vector index of chunks.",
"At query time, you link the entities mentioned in the query to graph nodes, expand one or two hops to collect relevant triples, and run vector search for supporting passages. Both go into the context.",
"The wins are relational multi-hop, aggregation over typed edges, like count suppliers in Vietnam, and auditable reasoning paths. The costs are real: schema design, extraction errors, entity resolution drift as the corpus grows, and a graph that goes stale unless extraction runs on every update. Use this when your domain is genuinely relational and schema-able, like finance, compliance, or supply chains.",
)

# ---------------------------------------------------------------- 5 WikiRAG concept
slide("03 · WikiRAG", """
<h2>WikiRAG: compile, then navigate</h2>
<div class="arch">
  <div class="lane">
    <div class="lane-t">COMPILE · when sources change</div>
    <div class="row">
      <div class="box">Raw sources<br><span class="sm muted">immutable</span></div><div class="arrow">→</div>
      <div class="box agent">LLM compiler</div><div class="arrow">→</div>
      <div class="col-boxes"><div class="box sm2">One page per entity / concept</div><div class="box sm2">Aliases · facts with citations · [[wikilinks]]</div><div class="box sm2">Index pages · overviews · backlinks</div></div>
    </div>
  </div>
  <div class="lane s1">
    <div class="lane-t accentc">NAVIGATE · per question</div>
    <div class="row">
      <div class="box">Question</div><div class="arrow">→</div>
      <div class="box agent">Agent</div><div class="arrow">⇄</div>
      <div class="col-boxes"><div class="box sm2">wiki_search: names, aliases, tags first</div><div class="box sm2">wiki_read: pages + index; links are next moves</div><div class="box sm2 hlb">read_source: verify against the raw text</div></div>
    </div>
  </div>
</div>
<div class="note s2">Popularized as the “LLM Wiki” pattern (Karpathy, 2026). Not to be confused with plain RAG over Wikipedia, which is also sometimes called WikiRAG.</div>
""",
"WikiRAG takes the opposite stance from hybrid search. Instead of fusing retrievers at query time, it compiles knowledge ahead of time. A language model reads the immutable raw sources and writes a wiki: one page per entity or concept, each with aliases, facts with citations back to the sources, wiki links to related pages, plus index and overview pages and backlinks.",
"At query time an agent navigates rather than retrieves. It searches page names, aliases, and tags first, reads pages, and treats links as its next moves, the way you'd browse Wikipedia. And in a well-built system it can read the raw source to verify a fact before relying on it.",
"This was popularized in twenty twenty-six as the L L M wiki pattern, attributed to Andrej Karpathy. One naming caution: WikiRAG is also used for plain RAG over Wikipedia articles. That's ordinary vector RAG with a particular corpus. In this lesson, WikiRAG means compile, then navigate.",
)

# ---------------------------------------------------------------- 6 Wiki mechanics
slide("03 · Keeping a wiki honest", """
<h2>The hard part is maintenance</h2>
<div class="grid2">
  <div class="panel code"><div class="label">A compiled page</div><pre><span class="c">---</span>
<span class="s">title</span>: Acme Logistics
<span class="s">aliases</span>: [Acme, ACME Freight]
<span class="s">tags</span>: [supplier, tier-1]
<span class="s">updated</span>: <span class="n">2026-09-12</span>
<span class="c">---</span>
Tier-1 freight supplier for [[Northwind]].
- Audited by [[Baker &amp; Co]] <span class="c">[src: audit-2026.pdf p4]</span>
- Contract renews <span class="n">2027-03</span> <span class="c">[src: msa.docx §9]</span>
- <span class="n">CONFLICT</span>: HQ city differs <span class="c">[src: a.pdf, b.pdf]</span></pre></div>
  <div class="stack">
    <div class="card s1"><div class="ic">1</div><div><b>Incremental ingest</b><br><span class="muted">New source → find affected pages → update them → refresh backlinks and indexes.</span></div></div>
    <div class="card s2"><div class="ic">2</div><div><b>Lint continuously</b><br><span class="muted">Dangling links, uncited facts, contradictions, duplicate entities, orphan pages.</span></div></div>
    <div class="card s3"><div class="ic red">!</div><div><b>Compile errors persist</b><br><span class="muted">A hallucination written into a page becomes “truth” for every later question. Citations + source verification are mandatory.</span></div></div>
  </div>
</div>
""",
"Building the wiki is easy. Keeping it honest is the hard part. Here's a compiled page: front matter with title, aliases, tags, and an updated date. Then short facts, each linking to other pages and citing a source location. Notice the explicit conflict line: when two sources disagree, the page should say so rather than silently pick one.",
"Maintenance starts with incremental ingest. A new source arrives, the compiler finds which pages it affects, updates them, and refreshes backlinks and indexes. This is where compile cost recurs, so the affected-page search needs to be precise.",
"Next, lint continuously: dangling links, facts without citations, contradictions across pages, duplicate entities under different names, and orphan pages nobody links to. The LLM-Wiki paper formalized this as an error book that records error patterns and feeds constraints back into future compilation.",
"The biggest risk is that compile errors persist. In query-time RAG, a hallucination affects one answer. In a wiki, a hallucination written into a page becomes truth for every later question. That's why every fact needs a citation, and why the agent should verify against raw sources for anything consequential.",
)

# ---------------------------------------------------------------- 7 Evidence
slide("03 · Evidence", """
<h2>What the evidence says (and doesn't)</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">LLM-Wiki paper (arXiv 2605.25480) · F1, 500 Qs each</div>
    <table class="math">
      <tr><td>HotpotQA</td><td class="num">0.839 <span class="muted">(+2.0)</span></td></tr>
      <tr><td>MuSiQue</td><td class="num">0.739 <span class="warn">(+8.1)</span></td></tr>
      <tr><td>2WikiMultiHopQA</td><td class="num">0.911 <span class="warn">(+6.4)</span></td></tr>
      <tr><td>4-hop questions</td><td class="num"><span class="warn">+8.3</span></td></tr>
    </table>
    <div class="note">Gains in parentheses are vs LightRAG, a strong graph-based baseline. Baselines also included BM25, dense, RAPTOR, GraphRAG, HippoRAG 2.</div>
  </div>
  <div class="stack">
    <div class="card s1"><div class="ic">$</div><div><b>Costs they report</b><br><span class="muted">Compile cost above chunk-and-embed; query latency ~15–27 s; scaling pain at tens of thousands of pages.</span></div></div>
    <div class="card s2"><div class="ic red">?</div><div><b>Read it critically</b><br><span class="muted">One paper. Benchmarks are Wikipedia-derived: entity-centric, and heavily memorized by LLMs. That structure favors a wiki.</span></div></div>
  </div>
</div>
""",
"What does the evidence say? The most concrete study so far is the LLM-Wiki paper, arXiv twenty-six oh five point two five four eight oh. On five hundred questions each, it reports F1 of zero point eight four on HotpotQA, zero point seven four on MuSiQue, and zero point nine one on Two Wiki Multi Hop Q A. Against LightRAG, a strong graph-based baseline, that's plus two, plus eight, and plus six points, and the gains grow with hop count: plus eight on four-hop questions. Baselines also included B M 25, dense retrieval, RAPTOR, GraphRAG, and HippoRAG two.",
"They also report the costs honestly: compilation is more expensive than chunk-and-embed, query latency is roughly fifteen to twenty-seven seconds because the agent reads and follows links, and scaling gets hard at tens of thousands of pages.",
"Now read it critically, as you would in a design review. It's one paper. All three benchmarks are derived from Wikipedia, which is entity-centric by construction and heavily memorized by language models. A wiki structure is naturally favored there. Before you adopt WikiRAG for support tickets or code, measure on your own corpus.",
)

# ---------------------------------------------------------------- 8 Tradeoff matrix
slide("04 · Tradeoffs", """
<h2>Every option, side by side</h2>
<table class="tbl rate-tbl">
  <tr><th>Option</th><th>Index cost</th><th>Query latency</th><th>Freshness</th><th>Exact match</th><th>Multi-hop</th><th>Global Qs</th><th>Provenance</th></tr>
  <tr><td><b>Long context</b> <span class="muted">(no retrieval)</span></td><td class="g">none</td><td class="b">high</td><td class="g">instant</td><td class="m">ok</td><td class="m">ok, small corpora</td><td class="m">small only</td><td class="b">weak</td></tr>
  <tr class="s1"><td><b>Dense RAG</b></td><td class="g">low</td><td class="g">low</td><td class="g">easy</td><td class="b">weak</td><td class="b">weak</td><td class="b">weak</td><td class="g">chunk cites</td></tr>
  <tr class="s2"><td><b>Hybrid search</b></td><td class="g">low</td><td class="g">low–med</td><td class="g">easy</td><td class="g">strong</td><td class="b">weak</td><td class="b">weak</td><td class="g">chunk cites</td></tr>
  <tr class="s3"><td><b>Graph + vector</b></td><td class="b">high</td><td class="m">medium</td><td class="m">re-extract</td><td class="m">ok</td><td class="g">strong</td><td class="m">typed only</td><td class="g">paths</td></tr>
  <tr class="s3"><td><b>GraphRAG</b> <span class="muted">(communities)</span></td><td class="b">very high</td><td class="m">medium</td><td class="b">rebuild</td><td class="b">weak</td><td class="m">ok</td><td class="g">strong</td><td class="m">summaries</td></tr>
  <tr class="s4 hlrow"><td><b>WikiRAG</b></td><td class="b">high</td><td class="b">high (agent)</td><td class="m">recompile pages</td><td class="g">names/aliases</td><td class="g">strong</td><td class="g">index pages</td><td class="m">if cited</td></tr>
</table>
<div class="note s5">Qualitative, typical-case ratings. Your corpus and question mix decide the real numbers — measure.</div>
""",
"Here's every option side by side. Start with long context and no retrieval. There's no index cost and freshness is instant, but every query pays for the whole corpus, it only works when the corpus fits, and provenance is weak because the model rarely tells you which passage it used.",
"Dense RAG is cheap and easy to keep fresh, with citable chunks, but weak on exact match, multi-hop, and global questions.",
"Hybrid search keeps the same cost profile and fixes exact match. That's why it should be your default floor. It's still weak on multi-hop and global questions.",
"Graph plus vector and GraphRAG move serious work to index time. Graph plus vector is strong on multi-hop over typed relations, with auditable paths, but needs re-extraction to stay fresh. GraphRAG's community summaries are the strongest option for global questions, like recurring themes, but indexing is the most expensive, and updates often mean rebuilding communities.",
"WikiRAG sits in an interesting spot. Index cost is high and query latency is high, because an agent navigates. But it's strong on multi-hop via links, handles global questions through index and overview pages, and handles exact names through aliases. Freshness costs a recompile of affected pages, and provenance is only as good as the citations the compiler wrote.",
"These are qualitative, typical-case ratings, not benchmark numbers. Your corpus and your question mix decide the real ones.",
)

# ---------------------------------------------------------------- 9 Where the cost goes
slide("04 · The core tradeoff", """
<h2>You're choosing <em>when</em> to think</h2>
<div class="spectrum">
  <div class="sp-bar"></div>
  <div class="sp-item" style="left:2%"><b>Long context</b><span>all work at query time</span></div>
  <div class="sp-item" style="left:22%"><b>Dense / Hybrid</b><span>embed once, cheap</span></div>
  <div class="sp-item" style="left:48%"><b>Graph + vector</b><span>extract relations</span></div>
  <div class="sp-item" style="left:74%"><b>GraphRAG · WikiRAG</b><span>compile understanding</span></div>
  <div class="sp-l">query-time compute</div><div class="sp-r">index-time compute</div>
</div>
<div class="formula s1">C<sub>per query</sub> = C<sub>compile</sub> × (updates) / N<sub>queries</sub> + C<sub>retrieve</sub> + C<sub>generate</sub></div>
<div class="grid3 mt">
  <div class="card v s2"><b>Many queries, stable corpus</b><span class="muted">Compile-heavy wins: cost amortizes, answers get faster and better.</span></div>
  <div class="card v s3"><b>High churn</b><span class="muted">Every change triggers recompiles of dependent pages or communities. Query-time methods win.</span></div>
  <div class="card v s4"><b>Few queries per doc</b><span class="muted">You'd compile knowledge nobody asks about. Compile lazily, on first touch.</span></div>
</div>
""",
"Step back and there's one tradeoff underneath the whole table. You're choosing when to think. At one end, long context does all the work at query time. Dense and hybrid search do a little work at index time, embedding once. Graph methods extract relations. And GraphRAG and WikiRAG compile understanding ahead of time.",
"The cost per query is the compile cost, multiplied by how often the corpus changes, divided by how many queries you serve, plus retrieval and generation. Every design decision here moves a term in this formula.",
"With many queries over a stable corpus, compile-heavy approaches win. Their cost amortizes to almost nothing and answers get faster and better.",
"With high churn, the picture flips. Every source change triggers recompiles of dependent wiki pages or graph communities, and query-time methods win.",
"And with few queries per document, compiling everything means paying to understand knowledge nobody asks about. The fix is lazy compilation: build or refresh a wiki page the first time a question touches that entity, and cache it.",
)

# ---------------------------------------------------------------- 10 Failure modes
slide("04 · Failure modes", """
<h2>How each option breaks</h2>
<div class="grid2">
  <div class="stack">
    <div class="card"><div class="ic red">H</div><div><b>Hybrid search</b><br><span class="muted">Fusion dilutes a strong single signal; reranker latency; bad tokenization for CJK; chunk context still lost.</span></div></div>
    <div class="card s1"><div class="ic red">G</div><div><b>Graph + vector</b><br><span class="muted">Entity resolution errors merge or split nodes; schema can't express new facts; stale edges answer confidently.</span></div></div>
  </div>
  <div class="stack">
    <div class="card s2"><div class="ic red">W</div><div><b>WikiRAG</b><br><span class="muted">Compile hallucinations persist; contradictions merged silently; page bloat and link rot; agent wanders or stops early.</span></div></div>
    <div class="card s3"><div class="ic red">L</div><div><b>Long context</b><br><span class="muted">Cost per query; recall drops mid-context; no audit trail; breaks the day the corpus outgrows the window.</span></div></div>
  </div>
</div>
<div class="thesis s4">Pattern: <b>the more you compile, the more your errors persist.</b> Mitigate with citations, linting, and verification against raw sources.</div>
""",
"How does each option break? Hybrid search: fusion can dilute a strong single signal, for example when one exact B M 25 hit gets outvoted. Rerankers add latency. Bad tokenization quietly breaks lexical search for Chinese, Japanese, and Korean. And chunk context is still lost.",
"Graph plus vector: entity resolution errors merge different things or split one thing into several nodes. The schema can't express facts it didn't anticipate. And stale edges answer confidently.",
"WikiRAG: compile hallucinations persist, contradictions get merged silently into one confident sentence, pages bloat and links rot, and the navigating agent can wander or stop too early.",
"Long context: cost on every query, recall that drops for material in the middle of the context, no audit trail, and a hard failure the day the corpus outgrows the window.",
"There's a pattern here. The more you compile, the more your errors persist. Query-time methods make fresh mistakes, and compile-time methods make durable ones. Mitigate with citations, linting, and verification against raw sources.",
)

# ---------------------------------------------------------------- 11 Decision framework
slide("05 · Decision framework", """
<h2>Choosing, in five questions</h2>
<table class="tbl">
  <tr><th>Ask</th><th>If yes</th></tr>
  <tr><td><b>1.</b> Does the whole corpus fit in context, with few queries?</td><td>Long context. Skip retrieval entirely.</td></tr>
  <tr class="s1"><td><b>2.</b> Do users query exact IDs, codes, names?</td><td><b>Hybrid search</b> as the floor — almost always yes.</td></tr>
  <tr class="s2"><td><b>3.</b> Is the domain relational and schema-able?</td><td>Add a <b>knowledge graph</b> (graph + vector HybridRAG).</td></tr>
  <tr class="s3"><td><b>4.</b> Entity-centric, multi-hop, stable, ≲10k pages?</td><td><b>WikiRAG</b>, compiled lazily for hot entities.</td></tr>
  <tr class="s4"><td><b>5.</b> Many “themes across everything” questions?</td><td>Pre-built summaries: <b>GraphRAG</b> or wiki overview pages.</td></tr>
</table>
<div class="thesis s5">My default: <b>hybrid search first</b>, measure, then add a compiled layer only where your eval shows multi-hop or global failures.</div>
""",
"Here's a decision framework in five questions. One: does the whole corpus fit in context, with few queries? Then use long context and skip retrieval entirely. It's the simplest system that works.",
"Two: do users query exact I Ds, codes, or names? Almost always yes, so hybrid search is your floor.",
"Three: is the domain relational and schema-able, like ownership, contracts, or supply chains? Add a knowledge graph, the graph plus vector flavor of HybridRAG.",
"Four: are questions entity-centric and multi-hop, over a fairly stable corpus of up to roughly ten thousand pages? That's WikiRAG's sweet spot. Compile lazily, starting with the entities people actually ask about.",
"Five: do users ask themes-across-everything questions? Then you need pre-built summaries, either GraphRAG communities or wiki overview pages.",
"My default recommendation: start with hybrid search, build an eval, and add a compiled layer only where the eval shows multi-hop or global failures. Complexity should be purchased with measured failures.",
)

# ---------------------------------------------------------------- 12 Layered architecture
slide("05 · Layered design", """
<h2>Don't choose one: layer them</h2>
<div class="pyramid">
  <div class="lvl l1">Wiki pages <span class="muted">· navigation layer for hot entities</span></div>
  <div class="lvl l2 s1">Knowledge graph <span class="muted">· only if relations are the product</span></div>
  <div class="lvl l3 s2">Hybrid search over chunks <span class="muted">· the floor, always on</span></div>
  <div class="lvl l4 s3">Raw sources <span class="muted">· the source of truth, for verification</span></div>
</div>
<div class="thesis s4">An agent routes: <b>wiki first</b> for entities, <b>hybrid search</b> for everything else, <b>raw sources</b> before asserting anything that matters. The wiki is a <i>cache of understanding</i>, not the truth.</div>
""",
"In practice the best systems don't choose one. They layer. At the top, wiki pages act as a navigation layer for the entities people ask about most.",
"Below that, a knowledge graph, but only if relations are the product, not just a nice-to-have.",
"The floor is hybrid search over chunks, always on, because it covers everything the compiled layers haven't reached yet.",
"And at the bottom, the raw sources, which remain the source of truth and exist for verification.",
"An agent routes across the layers: wiki first for entity questions, hybrid search for everything else, and raw sources before asserting anything that matters. The mental model to keep: the wiki is a cache of understanding, not the truth. Like any cache, it needs invalidation, and it must never be the only copy.",
)

# ---------------------------------------------------------------- 13 Evaluation
slide("06 · Evaluation", """
<h2>Evaluation that doesn't lie</h2>
<div class="grid2">
  <div class="panel">
    <div class="label">Golden set, split by question type</div>
    <ul class="tight">
      <li><b>Lookup / exact</b> — IDs, names, codes</li>
      <li><b>Multi-hop</b> — 2, 3, 4 hops, labeled</li>
      <li><b>Global</b> — themes, counts, comparisons</li>
      <li><b>Freshness</b> — facts that changed recently</li>
      <li><b>Unanswerable</b> — should abstain</li>
    </ul>
  </div>
  <div class="panel s1">
    <div class="label">Measure</div>
    <ul class="tight">
      <li>Retrieval recall@k vs gold evidence</li>
      <li>Answer accuracy + <b>citation support rate</b></li>
      <li>$ and p95 latency per query</li>
      <li><b>Time-to-correct</b>: edit a source, how long until answers change?</li>
      <li>Wiki lint: contradiction + uncited-fact rate</li>
    </ul>
  </div>
</div>
<div class="thesis s2">Always run a <b>closed-book baseline</b>. On Wikipedia-derived benchmarks the model already knows many answers — on your private corpus it doesn't.</div>
""",
"Finally, evaluation that doesn't lie. Build a golden set split by question type: lookups with exact I Ds and names, multi-hop questions labeled by hop count, global questions, freshness questions about facts that changed recently, and unanswerable questions where the right behavior is to abstain. Different architectures win different rows, so an aggregate score hides the decision.",
"Measure retrieval recall at k against gold evidence, answer accuracy together with citation support rate, cost and tail latency per query, and a metric most teams skip: time to correct. Edit a source document and measure how long until answers change. That number exposes the real freshness cost of compile-heavy designs. For WikiRAG, also track lint metrics: contradiction rate and uncited-fact rate.",
"And always run a closed-book baseline with no retrieval at all. On Wikipedia-derived benchmarks, the model already knows many of the answers, which inflates every method. On your private corpus it knows nothing, and that's the number that matters.",
)

# ---------------------------------------------------------------- 14 Recap
slide("Recap", """
<h2>Five things to take into your next design review</h2>
<ol class="recap">
  <li class="s1"><b>Name the failure first.</b> Exact match, multi-hop, global, or chunk context — each has a different fix.</li>
  <li class="s2"><b>Hybrid search is the floor.</b> Fuse ranks with RRF, rerank, tokenize for the language.</li>
  <li class="s3"><b>WikiRAG compiles understanding</b> — great for stable, entity-centric, multi-hop corpora.</li>
  <li class="s4"><b>You're choosing when to think.</b> Churn and query volume decide whether compiling pays.</li>
  <li class="s5"><b>Compiled errors persist.</b> Cite everything, lint, verify against raw sources.</li>
</ol>
<div class="exercise s6"><b>Exercise:</b> take 200 of your own documents. Build hybrid search, then a lazily compiled wiki for the top 20 entities. Evaluate 50 typed questions plus a closed-book baseline, and measure time-to-correct after editing three sources.</div>
""",
"Let's recap with five things to take into your next design review.",
"One. Name the failure first. Exact match, multi-hop, global, or chunk context. Each has a different fix.",
"Two. Hybrid search is the floor. Fuse ranks with reciprocal rank fusion, rerank, and tokenize for the language.",
"Three. WikiRAG compiles understanding. It's great for stable, entity-centric, multi-hop corpora.",
"Four. You're choosing when to think. Churn and query volume decide whether compiling pays for itself.",
"Five. Compiled errors persist. Cite everything, lint the wiki, and verify against raw sources.",
"Your exercise: take two hundred of your own documents. Build hybrid search, then a lazily compiled wiki for the top twenty entities. Evaluate fifty typed questions plus a closed-book baseline, and measure time to correct after editing three sources. The comparison will tell you more than any benchmark. Thanks for watching.",
)
