# What should a long-running agent remember?

The code behind the blog post **[Memory for Long-Running Agents: What to Keep and What to Forget](https://medium.com/@hiranipreet20/memory-for-long-running-agents-what-to-keep-and-what-to-forget-2400ba675078)**.

One model and one eight-week job, with five ways to give the agent a memory. Each strategy sees the same messages, in the same order, and gets the same tasks. Only the memory changes.

## The job

The agent is the operations assistant for *Fern & Flour*, a small online shop selling baking supplies. Each working day for eight weeks (40 sessions), it sees owner notes, customer and supplier emails, and tool outputs (order exports, inventory, web analytics). By the last day that's about 90,000 tokens of history, and most of it is routine noise.

Hidden in that history are the facts it will need later. Some of them change over the eight weeks:

| Kind of task | Example | What memory has to do |
|---|---|---|
| **Recall** | "What's our wholesale account number?" (said once, on day 2) | keep a fact for weeks |
| **Update** | "Which carrier do we use?" (changed twice) | keep only the newest value |
| **Expired** | "What's the free-shipping threshold?" (a one-week promo ended) | drop what has ended |
| **Deleted** | "What's this customer's phone number?" (they asked us to delete it) | forget on request |

There are 22 tasks per run. Each one is graded against an exact expected value, and every wrong answer is labelled: **outdated** (a value that used to be right), **not-forgotten** (the deleted number), **missing** (it said it didn't know), **mixed-up** (another customer's details), or **wrong**.

Seeds 1–3 use the same timeline with different names and values.

## The five memories

All of them work within the same budget of about 6,000 tokens per task, except the first.

| Strategy | What the model sees for each task | Used in the wild by |
|---|---|---|
| **keep-everything** | the full history | the default when you just append to the conversation |
| **recent-window** | only the newest messages that fit the budget | chat apps that truncate history |
| **rolling-summary** | a running summary the model rewrites each day, plus recent messages | "compaction" in coding agents and chat apps |
| **vector-retrieval** | the past messages most similar to the task (embeddings), plus recent messages | RAG-style memory, vector databases |
| **curated-memory** | a list of facts the model sets, replaces and deletes each day, plus recent messages | memory tools and memory files in today's agents (key-value "core memory") |

The summary and the curated memory get the **same written rules** about what to keep and what to forget ([`POLICY` in strategies.py](memlab/strategies.py)), so the only difference between them is the shape of the memory.

As a fairness check, an `oracle` run sees only the messages that answer each task. If it can't solve a task, the task is broken. It solves 22/22.

At the end, an audit checks whether the deleted phone number still exists anywhere in what each strategy has stored.

## Run it yourself

New to Python or API keys? The [GUIDE](../GUIDE.md) from part 1 covers every setup step; the commands here are the same, just in this folder.

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # macOS/Linux: cp .env.example .env, then add your key
python selftest.py                # checks the scenario, grader and strategies, no key needed
python run.py --seeds 1 --strategies oracle   # 22 cheap calls: are the tasks answerable?
python run.py                     # five strategies x seeds 1-3
python report.py                  # results.md and report.html
```

It runs on a free Gemini key (Gemini 3.5 Flash-Lite for the agent, `gemini-embedding-2` for retrieval). Any OpenAI-compatible API works. Every result is saved as it is graded, and every memory-upkeep call is cached, so an interrupted run picks up where it left off.

## Results

Gemini 3.5 Flash-Lite, temperature 0, 3 seeds × 22 tasks per strategy. Full tables are in [`results/gemini-3.5-flash-lite/results.md`](results/gemini-3.5-flash-lite/results.md).

| Strategy | Tasks right | Recall | Update | Expired | Deleted | Tokens per seed | Deleted number gone from memory |
|---|---|---|---|---|---|---|---|
| keep-everything | 97% | 100% | 100% | 83% | 67% | 1,150,580 | 0 of 3 seeds |
| recent-window | 17% | 6% | 12% | 50% | 100% | 206,345 | 3 of 3 |
| rolling-summary | 92% | 88% | 96% | 100% | 100% | 389,925 | 3 of 3 |
| vector-retrieval | 95% | 94% | 96% | 100% | 100% | 188,855 | 0 of 3 |
| curated-memory | 71% | 67% | 75% | 67% | 100% | 212,826 | 3 of 3 |

What stood out:

- **Keeping everything was the most accurate and the most expensive**, at about 6× the tokens of retrieval. It also gave the deleted phone number back to the courier in one seed, and used an expired promo threshold in another.
- **Vector retrieval was nearly as accurate at the lowest cost**, and it always answered the deletion task correctly. But the deleted number was still in its store at the end of every seed. Answering correctly isn't the same as forgetting.
- **The rolling summary forgot what it was told to forget**, but it lost old facts as it was rewritten (75% recall on facts older than 20 days), and it dropped a one-off customer's postcode in all three seeds. Rewriting the summary cost more tokens than answering.
- **Curated memory had the same rules as the summary and did worse.** The model kept policies and settings and mostly skipped customer details and prices, so it often had nothing to answer with.
- **A recent window can't do this job.** It forgot almost everything older than a week.

## Limits

- The scenario is synthetic and I wrote it, knowing what each strategy is for. Every task is checked by the oracle run, and the seeds change every value, but the timeline is the same.
- 22 tasks × 3 seeds is small. Treat the numbers as a demonstration, not a benchmark.
- The agent's own answers are not added back into its memory; each task is a probe.
- Token counts for the budget are estimated (characters ÷ 4); the reported token counts come from the API.
