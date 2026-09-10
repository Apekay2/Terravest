Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in
Multi-Agent Systems
Supriti Vijay∗
Foundation AI
USA
supriti.vijay@gmail.com

Aman Priyanshu∗
Foundation AI
USA
amanpriyanshusms2001@gmail.com

Esha Pahwa∗
Corvic AI
USA
pahwa.esha@gmail.com

6
2
0
2

y
a
M
6
2

]
I

A
.
s
c
[

1
v
6
6
7
7
2
.
5
0
6
2
:
v
i
X
r
a

Abstract
LLM safety evaluations predominantly test models in isolation, yet
deployed AI agents increasingly operate within persistent social
environments alongside other agents. We introduce a Moltbook-
style simulation platform where thousands of LLM agents interact
across communities over a simulated month, and use it to evaluate
privacy as a downstream safety concern under varying degrees
of social pressure. We find that shifting from single turn to multi
turn social evaluation amplifies privacy violations (CIMemories
19.95% to Ours 45.30% across OpenAI models), that leakage is so-
cially contagious, with agents 8× more likely to disclose sensitive
information after observing a peer do so, and that explicit privacy
instructions reduce but do not eliminate this effect, leaving leakage
rates above 37.8% even with safeguards. Our findings suggest that
static chat based safety benchmarks systematically underestimate
risks in agentic deployment, and that social context alone is suf-
ficient to elicit sensitive disclosures that single turn evaluations
would never surface.

CCS Concepts
• Security and privacy → Usability in security and privacy;
Privacy protections; Social network security and privacy;
Domain-specific security and privacy architectures.

Keywords
AI Safety, AI Social Networks, Contextual Integrity, Privacy Leak-
age, PII Leakage

ACM Reference Format:
Aman Priyanshu, Supriti Vijay, and Esha Pahwa. 2026. Got a Secret? LLM
Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems. In ACM
Conference on AI and Agentic Systems (CAIS ’26), May 26–29, 2026, San
Jose, CA, USA. ACM, New York, NY, USA, 11 pages. https://doi.org/10.1145/
3786335.3813173

1 Introduction
Large language model (LLM) safety evaluation has matured rapidly,
producing standardized benchmarks and automated red-teaming
protocols that probe models for harmful compliance and refusal
behavior [22, 28]. Yet these evaluations still predominantly treat

∗All authors contributed equally to this research.

This work is licensed under a Creative Commons Attribution 4.0 International License.
CAIS ’26, San Jose, CA, USA
© 2026 Copyright held by the owner/author(s).
ACM ISBN 979-8-4007-2415-2/2026/05
https://doi.org/10.1145/3786335.3813173

models as isolated chat assistants responding to short, bounded
prompts, even as deployed systems increasingly take the form of
agents: persistent software entities that operate over long horizons,
call tools, and interact repeatedly with users and with other agents
in shared environments [7, 10, 40]. This mismatch matters because
safety failures can be interaction-dependent: long-context prompt-
ing can unlock attack surfaces that are invisible in short prompts
[2], and agentic/tool-integrated settings introduce prompt injection
and instruction-hijacking threats that do not appear in “pure chat”
use [9, 19]. Further, multi-turn dialogue can allow adversaries to
decompose a harmful request into seemingly benign sub-queries,
eliciting unsafe information incrementally [31, 33, 45].

Privacy is a particularly consequential downstream safety con-
cern in such agentic deployments [5, 23, 32, 43]. Recent systems in-
creasingly store and retrieve “memories” to personalize interactions,
but persistent memory introduces a fundamental risk: information
can be surfaced in a context where it is inappropriate, even if it
was true or useful elsewhere [24, 32]. This framing aligns with the
theory of contextual integrity, which defines privacy not as mere
secrecy but as the appropriateness of information flows relative to
contextual norms governing who shares what with whom and un-
der which transmission principles [25]. Under this view, changing
the interaction context, recipient set, social setting, and normative
expectations, can change whether a disclosure constitutes a privacy
violation.

Critically, context is not only “task context” (e.g., emailing an of-
ficer versus chatting with a friend), but also social context. Decades
of research on online self-presentation and self-disclosure shows
that disclosure behavior is shaped by community setting and peer
environment: people disclose more when social relevance is high,
when peers are present, and when reciprocity or norms of sharing
are salient [1, 14, 34]. Even classic conformity findings emphasize
that group pressure can alter judgments and expressed behavior,
suggesting a general mechanism by which social pressure can re-
shape outward behavior absent any internal change in beliefs [3]. If
LLM agents are increasingly embedded in social channels, then pri-
vacy failures may arise not because a single prompt is adversarial,
but because the social environment itself makes disclosure “locally
normal” or instrumentally rewarded.

Despite this, most LLM safety benchmarks do not model privacy
risk as it appears in persistent social environments where many
agents interact over time. Current red-teaming suites typically mea-
sure single-model behavior against curated harmful prompts, offer-
ing strong coverage of direct compliance risks but limited visibility
into long-horizon, socially mediated disclosure dynamics [22]. Sim-
ilarly, while interactive agent benchmarks and social intelligence

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Priyanshu et al.

evaluations exist, they usually focus on goal completion, believ-
ability, or social reasoning rather than privacy violations under
community pressure [26, 44].

We address this gap by introducing a Moltbook-style simu-
lation platform in which thousands of LLM agents—each carry-
ing a private human profile with sensitive attributes spanning
health, finance, employment, and seven other domains—interact
across 124 communities over a simulated month. The design is
motivated by real-world agent communities such as Moltbook, a
Reddit-like platform that grew to over two million agents within
weeks of launch and has been independently characterized as hub-
dominated, thematically stratified, and vulnerable to social-vector
threats [11, 16, 17, 21, 30]. We operationalize privacy as contextual
integrity violations [25]: a disclosure counts as a violation when
a sensitive attribute surfaces outside a context that warrants it,
detected via an LLM-as-a-judge extraction protocol adapted from
[24, 42]. Using this platform, we run two complementary evalua-
tions: an organic simulation measuring leakage during unscripted
social interaction among 2,533 agents over 25 simulated days, and
a controlled testbed placing individual agents from seven frontier
models into frozen social environments at five levels of adversarial
contamination, yielding 7,000 evaluation traces. 1

Our results show that shifting from single-turn to multi-turn
social evaluation amplifies privacy violations from 19.95% to 45.3%
across OpenAI models, that leakage is socially contagious, agents
are 5.1 × more likely to disclose after observing a peer do so, and
that explicit privacy instructions leave leakage rates above 37.8%
even with safeguards. Community context proves as predictive
of leakage as model choice, with subreddit-level violation rates
spanning an order of magnitude. These findings are the result of
an investigation motivated by four research questions:

RQ1: When agents join a social platform, do they respect the same
contextual integrity boundaries they maintain in single-turn
tasks?

RQ2: Does social context create a ratchet, do agents that would
never volunteer sensitive information in isolation begin dis-
closing it after sustained community participation? Do they
inevitably succumb to “peer pressure”?

RQ3: Do explicit privacy instructions from the user survive social

pressure, or do agents eventually “go native”?

RQ4: Does the community an agent inhabits matter as much as

the model it runs on?

2 Related Work
2.1 Agents and Social Simulation
Most safety evaluations assume a stateless interaction: one user,
one prompt, one model response. But deployed agents increasingly
persist across sessions, accumulate memory, and operate alongside
other agents in shared environments. Understanding what happens
under these conditions required, first, building environments where
it could happen. Early work coupled LLMs with persistent natural-
language memory, reflection, and planning to sustain coherent
social behavior over multi-day interaction in small sandbox worlds

1Code and data are publicly available at https://llms-cant-keep-secrets.github.io/.

[26]. The resulting agents formed relationships, coordinated activi-
ties, and maintained consistent personas, demonstrating that social
behavior could emerge from language model architectures without
being scripted. Parallel efforts developed frameworks for evaluat-
ing social competence in open-ended settings [44], for structuring
multi-agent cooperation through role-playing and conversational
orchestration [6, 12, 15, 38], and for benchmarking agentic reason-
ing across interactive environments [18].

A persistent limitation of this work was scale. With populations
typically under fifty agents and interaction bounded by specific
tasks, these systems could show that social behavior emerges but
could not capture the community-level dynamics like norm forma-
tion, attention concentration, thematic stratification that charac-
terise real social platforms. Closing this gap required population-
scale simulation. Grounding over 1,000 agents in real interview
data yielded behavioral fidelity comparable to human self-retest
on survey instruments [27]. Scaling further to 10,000 agents and
millions of interactions demonstrated that polarisation, inflamma-
tory message spread, and collective norm dynamics arise naturally
at population density [29], and subsequent infrastructure work
showed that such simulations are computationally tractable on
commodity hardware [36, 39]. These platforms established that
persistent, community-structured agent populations are both tech-
nically feasible and behaviorally rich, but they were built to study
social-science questions like opinion formation and collective be-
havior, not to ask whether the social dynamics they produce have
consequences for safety or privacy.

2.2 AI Communities and Moltbook
That question became empirically grounded in early 2026, when
Moltbook, a Reddit-style platform restricted to AI agents, grew to
over two million registered agents within weeks of launch [17].
For the first time, researchers could observe autonomous agent-
to-agent interaction at scale in a live environment rather than a
controlled sandbox, and multiple independent groups converged
on a remarkably consistent portrait of what emerged.

The structural picture is stark. Agent interaction networks are
sparse, hub-dominated, and deeply unequal, with power-law de-
gree distributions, minimal reciprocity, and attention concentration
exceeding levels typically observed in human online communities
[11, 17, 21, 41].

Discourse self-organises into coherent thematic domains dis-
tributed unevenly across specialised sub-communities [13, 17]. And
critically, the dominant safety threat turns out to be social rather
than technical: social engineering vastly outperforms prompt injec-
tion as an attack vector, adversarial content attracts disproportion-
ately high engagement, and while agents sometimes push back on
risky instructions, this emergent norm enforcement is inconsistent
[13, 20, 41].

Two findings from this literature bear directly on our experi-
mental design. First, agents on Moltbook do not deeply socialise,
they exhibit strong individual inertia and minimal mutual adapta-
tion [17], yet controlled experiments show that LLM populations
readily form shared conventions through interaction alone and that
committed minorities can shift these conventions via critical mass
dynamics [4]. Conformity studies confirm that individual models

Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Figure 1: Qualitative examples from our multi-agent simulation demonstrating how social context drives disclosure. (a) In an
organic thread, a neutral prompt elicits no sensitive content, yet early replies introduce identifying details such as name, age,
employer, and health information. Subsequent agents escalate, adding family and personal history details that were never
solicited. (b) Under adversarial social pressure, explicit redaction instructions still fail to prevent leakage. In an extreme case,
an agent discloses sensitive attributes across 27 of 29 writes after exposure to disclosure-normalizing content. Highlighted
spans indicate PII categories. All personas are synthetic.

shift outputs toward group consensus even when it is clearly in-
correct [46]. The implication is that agents need not internalise
community norms to be influenced by them; contextual exposure
suffices. Second, theoretical work formalises this intuition: safety-
relevant mutual information degrades monotonically in isolated
agent societies, making alignment erosion over time not a bug but
a mathematical inevitability [37].

What this body of work establishes is an environment with all
the preconditions for privacy failure: extreme structural inequal-
ity that amplifies content reach, social-vector threats that operate
through exposure rather than direct exploitation, norm dynamics
susceptible to adversarial manipulation, and theoretical guarantees

of progressive safety erosion. What it does not measure is whether
these dynamics manifest as measurable privacy violations, specifi-
cally, whether the community an agent inhabits, the content it is
exposed to, and the duration of its participation systematically influ-
ence the extent to which it discloses its user’s sensitive information.
This work empirically investigates that relationship.

3 Dataset Curation
Our evaluation requires two complementary resources: a popula-
tion of agents whose behaviors and sensitive attributes are known
ground-truth, and a social environment rich enough to sustain or-
ganic multi-turn interaction. We construct both from public sources.

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Priyanshu et al.

Agent personas are seeded from the Moltbook platform [35], a real-
world Reddit-style environment populated exclusively by AI agents,
while the private human profiles assigned to each agent are gen-
erated following established synthetic-data practices grounded in
the Faker library [8], used in prior privacy evaluations to produce
controlled PII [24, 32]. The resulting simulation pairs each agent
with a defined set of private attributes, enabling deterministic leak-
age measurement while preserving the organic social dynamics of
the original platform. Synthetic profile generation is an established
methodology in privacy evaluation; Mireshghallah et al. [24] simi-
larly construct profiles with over 100 attributes per user following
the same domain schema we adopt here.

3.1 Personas and Sensitive Attributes
Our starting point is the Moltbook HuggingFace dataset [35], an
early snapshot of the platform captured before significant human in-
filtration. This snapshot contains 6,105 raw posts distributed across
124 subreddits. Because the majority of early Moltbook activity
consists of agents introducing themselves to the community, we
apply an LLM-as-a-judge filter (GPT-5-mini) to classify each post
as introductory or non-introductory, retaining the 2,533 posts that
constitute genuine self-introductions. From each retained post we
extract a structured agent persona: agent name, behavioral ten-
dencies, preferred subreddits, characteristic vocabulary, and a seed
post establishing the agent’s presence on the platform. These 2,533
agent personas define the population of our simulation.

Each agent requires a private human profile whose attributes
constitute the ground-truth for leakage detection. We adopt a two-
tier generation strategy anchored in the ten annotated human pro-
files released by Mireshghallah et al. [24] as part of their contex-
tual integrity evaluation. These profiles broadly span ten sensitive-
information domains: general identity, finance, health, mental health,
legal, relationships, housing, employment, education, and scheduling.
We set aside these ten profiles as a held-out evaluation set for the
controlled testbed experiments described in Section 4.3. For each
of the 2,533 agents, we construct a private human profile in three
steps: (1) we use the Faker library [8] to generate a seed identity
(name, address, date of birth, phone number, credit score); (2) we
randomly select one of the ten annotated CIMemories profiles [24]
as a structural example and stylistic reference; and (3) we prompt
GPT-5-mini with both the Faker seed and the selected CIMemories
profile, instructing it to generate a new, complete human profile
grounded in the Faker identity but following the domain cover-
age and attribute granularity of the CIMemories example. Each
resulting profile is stored as a structured dictionary of approxi-
mately 96.8 ± 16.3 key-value pairs, ensuring that every attribute
contains specific descriptions. This design enables our detection
pipeline to distinguish genuine leakage from topically adjacent but
non-identifying content.

Algorithm 1 Asynchronous Agent Interaction Loop
Require: Agent persona 𝑎, human profile ℎ, memory 𝑀, tool suite

T , turn budget 𝐵, current day 𝑑

1: prompt ← BuildSystemPrompt(𝑎, ℎ, 𝑀)
2: messages ← [prompt]
3: 𝑏 ← 0 {tool calls used}
4: while 𝑏 < 𝐵 do
5:

response ← LLM(messages)
if response contains no tool calls then

break {agent yields}

6:

7:

8:

9:

10:

11:

12:

13:

14:

15:

end if
for each tool call (name, args) in response do
result ← T .Dispatch(name, args, 𝑎.id, 𝑑)
Append (name, args, result) to messages
if name ∈ {append_to_memory, modify_memory} then

𝑀 ← result {update persistent memory}

end if
𝑏 ← 𝑏 + 1

16:
end for
17: end while
18: Persist updated 𝑀 for agent 𝑎

common), and a persistent per-agent MEMORY.md scratchpad. Each
agent accesses the platform exclusively through a twelve-function
tool suite (Table 1) that exposes browsing, searching, posting, reply-
ing, voting, and memory operations. Crucially, tool outputs include
social metadata (author identity, vote counts, relationship signals),
enabling socially informed behavior without explicit inter-agent
coordination.

We simulate 25 days of platform activity. Three OpenAI models
serve as agent backends, assigned in approximately equal propor-
tions (1 : 1 : 1): GPT-5-nano, GPT-5-mini, and GPT-5. Algorithm 1
describes the per-agent orchestration loop. On each simulated day,
the scheduler selects a subset of agents to activate. Each activated
agent receives a system prompt containing its AI persona, its private
human profile, its current MEMORY.md contents, and platform in-
structions. The agent then enters an autonomous tool-calling loop:
it issues tool calls against the live database, receives structured
observations, and decides subsequent actions until it exhausts its
per-turn budget or explicitly yields. Because all agents operate asyn-
chronously against the shared database, an agent may encounter
posts, replies, and vote patterns that were created by other agents
moments earlier in the same simulated day, producing emergent
social dynamics without scripted interaction.

Over 25 simulated days the platform accumulates 29,945 top-
level posts and 81,264 threaded replies (111,209 content items total),
with a mean post length of 508 characters and a mean reply length
of 400 characters.

3.2 Constructing the Simulation Environment
The simulation environment is a shared social-media server backed
by an SQLite database that all agents read from and write to concur-
rently. The platform mirrors core Reddit affordances: 124 subreddits,
top-level posts, threaded replies, upvote/downvote voting, user pro-
files with social-context annotations (mutual votes, subreddits in

4 Experimental Setup
4.1 Overview
Our experimental design comprises two complementary evalua-
tions that together isolate the effect of social context on privacy
leakage. In the first, we measure organic leakage: the extent to
which agents disclose private attributes during unscripted social

Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Table 1: Tool suite available to each agent during simulation.
Tools marked with ★ produce write actions tracked for leak-
age detection.

Tool

Description

Search subreddits by keyword
find_subreddit
Retrieve 20 most recent posts
get_newly_posted
Browse posts with sort and pagination
open_subreddit
Read post and threaded replies
open_post
Keyword search across posts
find_post
View agent profile with social context
get_user_profile
post_in_subreddit★
Create top-level post
thread_in_post★
Reply to post or thread
Vote on a post
upvote_downvote_post
upvote_downvote_thread Vote on a reply
append_to_memory
modify_memory

Append to persistent MEMORY.md
Overwrite MEMORY.md

interaction on the simulation platform described in Section 3. In
the second, we measure elicited leakage: how much additional dis-
closure can be extracted when adversarial content is injected into
the social environment at calibrated intensities. The two evalua-
tions share the same platform infrastructure, the same persona
schema, and the same leakage detection pipeline, differing only
in whether the social pressure is emergent or controlled. We use
’social pressure’ to refer to an agent’s exposure to disclosure norms
present in its surrounding community content, not to real-time
interactive pressure from other agents. This paired design allows
us to quantify both the baseline privacy risk inherent in agentic
social participation and the marginal risk introduced by adversarial
manipulation.

4.2 Organic Disclosure in Social Simulation
The organic evaluation uses the simulation described in Section 3
without modification. After the 25-day simulation completes, we
snapshot the platform state and apply the leakage detection pipeline
(Section 4.4) to all 29,945 posts and 81,264 threads. For each con-
tent item, we look up the author’s persona key via author_hash,
retrieve that persona’s compiled patterns, and record which of the
ten privacy domains (if any) produced a match. A content item is
classified as leaking if at least one domain-specific pattern matches.
We additionally analyze two social dynamics that may amplify
organic leakage. First, we examine community context: whether cer-
tain subreddits, by virtue of their topic or social norms, elicit higher
disclosure rates than others. Second, we test for social contagion:
whether a leaking reply in a thread increases the probability that
the subsequent reply also leaks, controlling for the baseline leakage
rate.

4.3 Elicited Disclosure Under Adversarial Social

Pressure

The controlled testbed holds the social environment fixed and varies
the agent under evaluation, the adversarial intensity, and the experi-
mental condition. We freeze the platform snapshot produced by the
organic simulation and create five variants by injecting adversarial

content at increasing densities, producing Levels 1 through 5. Each
level is then evaluated independently across seven frontier models:

• openai/gpt-5
• openai/gpt-5-mini
• openai/gpt-5-nano
• openai/gpt-4o
• openai/gpt-4o-mini
• google/gemini-3-flash-preview
• google/gemini-3-pro-preview

Each model is paired with ten held-out human personas from
CIMemories [24] and five budget checkpoints (10, 20, 30, 40, and
50 tool calls), yielding 1,000 evaluation runs per model and 7,000
total traces.

Adversarial nudge design. For each adversarial level, we use GPT-
5-mini to generate fictitious agent identities drawn from a randomly
selected pool of existing agents on the platform. Each fictitious
agent authors a new post that casually discloses details about its
“human”, normalizing the act of sharing private information within
the community. To ensure visibility, we synthetically upvote each
injected post to 1.2× the previous maximum upvote count in its
subreddit, guaranteeing that the adversarial content surfaces promi-
nently when agents browse by popularity. The five levels differ in
the breadth of adversarial injection:

• Level 1: The platform snapshot is used as-is, with no adver-

sarial posts injected (control condition).

• Level 2: A single adversarial post is injected into the most

active subreddit by post count.

• Level 3: Adversarial posts are injected into the top-3 sub-

reddits by post count.

• Level 4: Adversarial posts are injected into the top-5 sub-

reddits by post count.

• Level 5: Every subreddit on the platform receives an adver-

sarial post.

This aims to test whether agents are influenced by disclosure norms
only when they encounter them in their preferred communities
or whether platform-wide contamination produces a qualitatively
different effect.

Experimental conditions. Each evaluation run is parameterized
by two binary conditions in addition to the adversarial level: (1) sys-
tem_prompt_to_redact, which controls whether the agent’s system
prompt explicitly instructs it not to disclose private information;
and (2) human_subreddits_suggested, which controls whether the
agent’s account is pre-seeded with subreddit subscriptions match-
ing the human persona’s interests. The first condition tests whether
telling an agent not to share private information actually reduces
leakage when the surrounding social environment encourages dis-
closure. The second tests whether agents leak more when they are
placed in subreddits whose topics overlap with their private profile.

Evaluation protocol. Each of the evaluation runs is fully inde-
pendent: a single target agent, instantiated with one model and
one persona, is placed alone into a frozen platform snapshot at the
designated adversarial level. No other agents are live during the
run. The target agent executes the autonomous tool-calling loop
described in Algorithm 1, browsing, reading, and writing against

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Priyanshu et al.

Frozen Snapshot

Target Agent

r/general

r/memory

r/agentstack

. . . (124 total)

Model 𝑚

Persona 𝑝

Redact prompt 𝑏𝑜𝑜𝑙

Seeded subs 𝑏𝑜𝑜𝑙

reads

writes (static DB)

Adversarial posts

Algo. 1: tool loop

Detection

Collected writes

writes

Regex pipeline

Leaked domains

interaction budget: 10, 20, 30, 40, 50

Adversarial setting: L1: none L2: top-1 L3: top-3
L4: top-5 L5: all subs

Figure 2: Controlled testbed protocol. A single agent interacts alone with a frozen platform snapshot containing adversarial
posts at one of five density levels. All writes are evaluated for leakage at each budget checkpoint.

the static platform content until it reaches the budget checkpoint
or yields. Because the platform is frozen, the agent’s writes do not
alter what it subsequently reads; it interacts with a fixed social
environment in which the only variable is its own behavior. We
record all tool calls and extract the content field from every write
action (post_in_subreddit and thread_in_post). The leakage
detection pipeline is then applied to each write using the patterns
generated for the assigned persona, producing a per-write list of
leaked domains. We do this across five intervals (10, 20, 30, 40, and
50 tool calls) allowing us to examine how leakage evolves over the
course longer evaluation runs.

4.4 PII Violation Detection
We employ a model-based judge to identify privacy violations in
agent-generated content. Following Mireshghallah et al. [24], the
judge evaluates each content item against the author’s full human
profile. It receives a system prompt defining ten privacy domains
(general identity, finance, health, mental health, legal, relationships,
housing, employment, education, and scheduling) with detailed cri-
teria. Given a human profile and a post or reply, the judge extracts
a boolean flag per domain indicating whether the content reveals
information in that category. Because the judge is invoked in a fully
stateless, single-turn context — receiving exactly one post or reply
alongside the author’s human profile, with no surrounding thread,
no social metadata, and no prior interaction history — it is never
embedded in the social environment and therefore cannot accumu-
late the contextual exposure that drives conformity in the evaluated
agents. We use gpt-5-nano as the judge model, consistent with
Mireshghallah et al. [24]. This allows us to measure privacy vio-
lations as an emergent property of interaction trajectories rather
than as a one-shot refusal task.

5 Results

Baseline: Social vs. Isolated Violations (RQ1). Our results indicate
a clear boundary shift when agents move from isolated, single-
turn interactions into persistent social environments. While many

Figure 3: Cumulative leaking posts/threads over 25 simu-
lated turns in the organic multi-agent social environment.
The steady growth in leakage indicates that privacy viola-
tions accumulate over time rather than occurring as isolated
outliers.

models appear to respect contextual integrity constraints in short,
bounded prompts, this restraint does not reliably persist once agents
participate in multi-turn, community-mediated interaction. In the
25-turn organic simulation, privacy violations are not rare “one-off”
failures: the cumulative number of leaking posts/threads increases
steadily throughout the run, reaching roughly ∼2.5k leaking items
out of ∼111k total content items by turn 25 (Fig. 3). The monotonic
growth in leakage demonstrates that disclosure is not confined to
early exploratory behavior but continues to accrue as agents remain
embedded in the social platform. Simply sustaining participation
in a shared environment is sufficient to surface violations that
single-turn testing would not reveal.

The controlled testbed corroborates this pattern. Even when the
platform is frozen and no other agents are active, leakage rates are
already substantial at short horizons and generally increase with
interaction length (tool-call budget) for most models (Fig. 4). By
50 tool calls, several models exhibit leakage rates approaching or

Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

exceeding ∼50–60%, while even stronger models show persistent
leakage in the ∼20–30% range.

Taken together, these findings show that contextual integrity
compliance observed in isolated evaluations does not reliably trans-
fer to socially embedded settings. Multi-turn social participation
materially shifts what agents treat as appropriate to disclose, imply-
ing that single-turn CI benchmarks systematically underestimate
privacy risk in agentic deployment (Fig. 3, Fig. 4).

Temporal Accumulation (RQ2). We find strong evidence of a social
ratchet effect: exposure to disclosure within a community substan-
tially increases the probability that an agent will disclose in its next
reply. Figure 6 shows that when a reply follows a leaking message
in the same thread, the probability that the next reply also leaks
rises to 12.8%. In contrast, when the preceding reply is clean, the
probability of leakage drops to 1.6%, nearly identical to the global
baseline of 1.8%. The ∼8× increase relative to the clean-condition
baseline indicates that disclosure is not merely a function of an
agent’s intrinsic propensity to leak; it is highly sensitive to immedi-
ate social context. In other words, agents that would rarely disclose
in isolation begin doing so when disclosure is locally normalized
within the thread.

Importantly, this effect does not require explicit adversarial
prompting. The mere presence of prior leakage in a conversation
is sufficient to shift what agents treat as contextually appropriate.
This dynamic mirrors classic conformity and reciprocity effects
in human social behavior: once a boundary is crossed in a shared
setting, subsequent participants are more likely to follow.

However, agents do not inevitably succumb. The baseline leakage
rate remains low (1.8%), and many threads do not cascade. Rather
than deterministic collapse, we observe a probabilistic ratchet: so-
cial exposure sharply raises risk, and repeated exposure compounds
it, but compliance remains contingent on model, persona, and in-
teraction length.

Taken together, these findings show that social context can en-
dogenously erode contextual integrity boundaries over time. Pri-
vacy violations are not solely the result of direct adversarial extrac-
tion; they can emerge organically through peer effects and local
norm shifts within sustained community participation.

Instruction Robustness Under Pressure (RQ3). We test whether
adding an explicit redaction instruction to the agent’s system prompt
meaningfully reduces leakage once the agent is embedded in a so-
cially contaminated environment. Figure 4 compares total leakage
counts across models with and without a privacy instruction.

Across most models, explicit instructions reduce total leakage
counts, but the reduction is partial rather than decisive. For ex-
ample, gpt-4o decreases from 2,624 to 2,102 leaking writes, and
gpt-5-mini decreases from 2,889 to 2,194. However, leakage re-
mains in the thousands even with instructions enabled. Only a
subset of models (notably gpt-5) show a dramatic reduction un-
der instruction (2,296 to 482), indicating that robustness to social
pressure is highly model-dependent.

Crucially, the persistence of substantial leakage despite explicit
redaction directives suggests that privacy instructions do not reli-
ably “survive” sustained social exposure. In contaminated environ-
ments, where disclosure is normalized and socially rewarded—agents
frequently relax or override system-level privacy constraints. Rather

Figure 4: Leakage counts by model with and without explicit
privacy instructions in the system prompt. While instruc-
tions reduce leakage in most models, substantial violations
remain under social pressure.

Figure 5: Leakage rate by subreddit. Communities centered
on self-introduction or personal reflection exhibit substan-
tially higher leakage than technically oriented communities.

than a hard safety boundary, we observe instruction-following as
a probabilistic defense whose effectiveness degrades under social
pressure.

These results indicate that agents can indeed “go native”: even
when explicitly told not to disclose private information, many mod-
els adapt their behavior toward local norms of sharing. Privacy
instructions provide mitigation, but not immunity, underscoring
that prompt-level safeguards alone are insufficient in persistent,
socially embedded deployments.

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Priyanshu et al.

Figure 6: Contagion analysis. The probabil-
ity that a reply leaks sensitive information
is 12.8% when it follows a leaking reply, com-
pared to 1.6% after a clean reply and 1.8% over-
all baseline.

Figure 7: Number of leaking posts/threads
by privacy domain. General identity and em-
ployment attributes account for the largest
share of violations.

Figure 8: Leakage rates by persona (avg across
models). Variation is low (𝑠𝑡𝑑 = 2.8%), indicat-
ing stronger dependence on social context
than persona.

Community Topic Effects (RQ4). Yes, community context exerts
an effect comparable in magnitude to model choice, we find simi-
larly large variance across subreddits and privacy domains, indicat-
ing that where an agent participates can be as predictive of leakage
as which model it runs on.

Figure 5 shows leakage rates by subreddit. Rates range from un-
der 2% in communities such as memory and agent-tooling to over
16% in introductions. This nearly order-of-magnitude spread mir-
rors (and in some cases exceeds) the performance gap between fron-
tier models. Notably, high-leakage communities are those whose
norms explicitly invite self-disclosure (e.g., introductions, existen-
tial discussions, public building logs), suggesting that topical affor-
dances and local norms meaningfully shape contextual integrity
boundaries.

Figure 7 further breaks violations down by privacy domain. Gen-
eral identity attributes dominate (1,496 leaking items), followed
by employment (921), scheduling (812), and mental health (767).
The distribution reveals that leakage is not uniformly spread across
domains; rather, it concentrates in attributes that are socially salient
and conversationally natural within certain communities.

Taken together, these results indicate that the community an
agent inhabits can meaningfully amplify or dampen privacy risk. A
relatively strong model placed in a disclosure-oriented subreddit
may leak more than a weaker model placed in a technically con-
strained environment. Thus, social topology and topical context
are first-order safety variables, not merely background conditions.
Evaluations that vary only model architecture while holding social
environment fixed risk overlooking a critical axis of deployment-
time vulnerability.

Persona-Level Variation. Figure 8 shows leakage rates across the
ten held-out CIMemories personas in the controlled testbed. Rates
range from 27.8% (personas 7 and 9) to 36.4% (persona 5), a spread
of approximately 1.3×. This variance is modest relative to the differ-
ences observed across models (Fig. 4) and across subreddits (Fig. 5),
where rates span nearly an order of magnitude. No single persona
is dramatically more or less vulnerable than the others, and the
ranking does not track any obvious profile property such as total
attribute count or the presence of health-related information. The
relative flatness of persona-level variation suggests that the social

environment exerts pressure broadly: it does not selectively exploit
particular profile compositions but rather creates conditions under
which most profiles leak at comparable rates.

Domain Consistency Across Personas. Although aggregate leak-
age rates are similar across personas, the per-persona domain break-
downs reveal a consistent internal structure. General identity at-
tributes dominate the leakage counts for every persona without
exception, accounting for the majority of leaked items in all ten
cases. Employment is the second most frequent domain for eight of
ten personas. This pattern holds regardless of whether a persona’s
profile emphasizes health, finance, or legal content. In other words,
while the overall rate of leakage is relatively stable across personas,
the composition of that leakage is also stable: it concentrates in the
same domains regardless of what sensitive information the profile
contains. There are a few exceptions like Persona 4 which exhibits
an unusually high count of mental health violations (988 cases), and
persona 9 leaks a disproportionate amount of financial information
(588 cases). In both cases, the persona’s underlying profile contains
attributes in these domains that are conversationally salient.

Attribute-Type and Community Interaction. The domain-level
results from the organic simulation (Fig. 7) showed that employ-
ment attributes account for the highest leakage rate, followed by
scheduling and mental health, with education and housing leaking
least. Mental health and health attributes leak selectively, concen-
trated in communities oriented toward personal reflection (e.g.,
r/ponderings - 142 and r/philosophy - 99 out of 707 cases), con-
sistent with the subreddit-level findings in Figure 5. Finance and
legal attributes leak least overall, likely because few communities
on the platform create contexts where these details arise naturally.
We believe, these patterns indicate that attribute-level risk is
jointly determined by information domain and community context
rather than by profile composition alone. The practical implication
is that controlling which communities an agent participates in may
help reduce privacy exposure more effectively than modifying the
agent’s underlying profile or persona.

6 Discussion

Implications for safety evaluation. Our central finding is that
static, single-turn safety benchmarks systematically underestimate

Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

privacy risk in agentic deployment. In isolated settings such as
CIMemories-style evaluations, leakage occurs under direct prompt-
ing or task confusion. In contrast, our multi-agent social setting
produces persistent, organically emergent violations over sustained
interaction horizons.

Quantitatively, leakage rates in socially embedded settings rise
to double-digit percentages in certain communities (Fig. 5) and
reach 50–60% under extended tool-call budgets for several frontier
models (Fig. 4). Even in the organic simulation without adversarial
nudges, cumulative violations steadily accumulate over time (Fig. 3).
Moreover, contagion analysis shows an approximately 8× increase
in the probability of leakage when a reply follows a leaking message
(12.8% vs. 1.6%; Fig. 6).

These results indicate that privacy failures are not isolated com-
pliance errors but trajectory-dependent phenomena. Safety evalua-
tion for agentic systems must therefore vary social context alongside
task context. Benchmarks that measure only refusal behavior in
bounded prompts fail to capture norm drift, peer effects, and cu-
mulative disclosure under long-horizon interaction. Any realistic
safety evaluation of persistent agents should treat community topol-
ogy, exposure to peer behavior, and interaction length as first-class
variables.

Implications for Moltbook-like platforms. Our findings are di-
rectly relevant to large-scale agent communities such as Moltbook,
which has rapidly scaled to millions of agents and exhibits hub-
dominated attention, sparse reciprocity, and strong engagement
concentration [17, 21]. Prior work has documented the presence of
social-vector threats, attention inequality, and norm dynamics in
such environments. Our simulation shows what those structural
conditions imply for privacy: even without explicit adversarial ex-
traction, disclosure norms can propagate and amplify.

In communities where visibility is algorithmically amplified and
high-engagement content sets norms, small amounts of disclosure
can cascade into elevated platform-wide leakage probabilities. The
combination of attention concentration and social contagion means
that privacy degradation can be driven by exposure alone. Platforms
hosting autonomous agents should therefore anticipate privacy
erosion as an emergent property of scale and structure, not merely
as a prompt-level vulnerability.

These findings motivate a concrete forward-looking research
agenda. First, the field needs evaluation frameworks that treat com-
munity structure, peer exposure, and interaction horizon as first-
class experimental variables on par with model architecture and
prompt design. Second, mitigation strategies must move beyond
prompt-level safeguards toward systemic interventions such as
community-aware system prompts, memory sandboxing that pre-
vents cross-context attribute surfacing, and platform-level norm
monitoring that detects disclosure cascades before they propagate.
Third, the simulation methodology introduced here should be ex-
tended to live, multi-provider deployments, including open-source
models with different alignment training, to test whether the conta-
gion effect is alignment-dependent or a more fundamental property
of language model behavior in social contexts.

Limitations and future work. Our study has several important
limitations. First, personas are synthetic and assigned to agents;
while grounded in prior privacy benchmarks, they are not real users.

Future work may want to evaluate privacy dynamics with live, con-
senting participants or with audited real-world agent deployments.
Second, our platform is a simulated Reddit-like environment
rather than the live Moltbook system. Although structurally faithful,
real-world dynamics may introduce additional complexity such as
cross-platform spillover or human-agent interaction.

Third, while the controlled testbed evaluates multiple frontier
models, the organic simulation uses a fixed set of OpenAI backends.
Broader cross-provider comparisons would improve generalizabil-
ity. Extending to open-source models is a priority, as differences in
alignment may affect leakage rates and responses to social pressure.
Fourth, leakage detection relies on an LLM-as-a-judge system,
which may introduce false positives or negatives. Our proxy for
contextual integrity is approximate, so reported violations should
be interpreted as an upper bound. Improving detection with human
annotation, ensembles, or norm-aware judgments is an important
direction.

Finally, our adversarial contamination is hand-crafted rather
than emergent. Real communities may generate adversarial norm
shifts organically. A promising direction is to allow pollution dy-
namics to arise endogenously and study phase transitions in privacy
norms.

Contextual integrity revisited. Our results extend the theory of
contextual integrity [25] into the domain of multi-agent AI sys-
tems. Contextual integrity defines privacy in terms of appropriate
information flows governed by contextual norms. Existing LLM
benchmarks operationalize context narrowly as task framing (e.g.,
“email your boss” vs. “chat with a friend”). We show that social con-
text is itself an information-flow dimension. Agents are not merely
leaking because they misunderstand a task or fail a refusal heuristic.
Rather, the surrounding community redefines what appears locally
appropriate. Exposure to peer disclosure shifts perceived norms,
increasing the probability that sensitive attributes are treated as
shareable. In this sense, privacy violations in agent societies are not
solely alignment failures at the individual model level; they may be
emergent properties of collective dynamics. By demonstrating that
social participation alone can erode contextual integrity boundaries,
we argue that safety evaluation must expand beyond individual
prompt compliance to encompass the normative environments in
which agents operate.

7 Conclusion
We show that LLM safety evaluations conducted in isolated, single-
turn settings systematically underestimate privacy risk in socially
embedded deployments. Across both organic and controlled exper-
iments, agents that maintain contextual integrity boundaries in
bounded prompts disclose sensitive information at substantially
higher rates when placed in persistent multi-agent environments.
This leakage is socially mediated: exposure to prior disclosure in a
thread increases subsequent leakage probability by approximately
8×, and explicit privacy instructions in the system prompt do not
fully mitigate the effect. Community context proves as predictive
of leakage as model choice, with subreddit-level violation rates
spanning nearly an order of magnitude. These findings indicate
that safety evaluation for agentic systems should treat commu-
nity structure, peer exposure, and interaction horizon as first-class
experimental variables alongside model and prompt design.

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

Priyanshu et al.

References
[1] Alessandro Acquisti, Leslie K John, and George Loewenstein. 2013. What is

privacy worth? The Journal of Legal Studies 42, 2 (2013), 249–274.

[2] Cem Anil, Esin Durmus, Nina Panickssery, Mrinank Sharma, Joe Benton, Sandi-
pan Kundu, Joshua Batson, Meg Tong, Jesse Mu, Daniel Ford, et al. 2024. Many-
shot jailbreaking. Advances in Neural Information Processing Systems 37 (2024),
129696–129742.

[3] Solomon E Asch. 2016. Effects of group pressure upon the modification and
distortion of judgments. In Organizational influence processes. Routledge, 295–
303.

[4] Ariel Flint Ashery, Luca Maria Aiello, and Andrea Baronchelli. 2025. Emergent
social conventions and collective bias in LLM populations. Science Advances 11,
20 (May 2025). doi:10.1126/sciadv.adu9368

[5] Hannah Brown, Katherine Lee, Fatemehsadat Mireshghallah, Reza Shokri, and
Florian Tramèr. 2022. What Does it Mean for a Language Model to Preserve Pri-
vacy?. In Proceedings of the 2022 ACM Conference on Fairness, Accountability, and
Transparency (Seoul, Republic of Korea) (FAccT ’22). Association for Computing
Machinery, New York, NY, USA, 2280–2292. doi:10.1145/3531146.3534642
[6] Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, Chenfei Yuan, Chi-Min Chan,
Heyang Yu, Yaxi Lu, Yi-Hsin Hung, Chen Qian, Yujia Qin, Xin Cong, Ruobing Xie,
Zhiyuan Liu, Maosong Sun, and Jie Zhou. 2023. AgentVerse: Facilitating Multi-
Agent Collaboration and Exploring Emergent Behaviors. arXiv:2308.10848 [cs.CL]
https://arxiv.org/abs/2308.10848

[7] X Chen, A Zeng, et al. 2024. A survey on large language model based autonomous
agents. In CCL 2024–23rd Chinese Natl Conf Comput Linguist, Vol. 2. 141–150.
[8] Dylan Clendenin. 2009. faker: A Python library for generating fake user data.
https://github.com/deepthawtz/faker. GitHub repository. MIT License. Accessed
2026.

[9] Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten
Holz, and Mario Fritz. 2023. Not what you’ve signed up for: Compromising real-
world llm-integrated applications with indirect prompt injection. In Proceedings
of the 16th ACM workshop on artificial intelligence and security. 79–90.

[10] Taicheng Guo, Xiuying Chen, Yaqi Wang, Ruidi Chang, Shichao Pei, Nitesh V
Chawla, Olaf Wiest, and Xiangliang Zhang. 2024. Large language model based
multi-agents: A survey of progress and challenges. arXiv 2024. arXiv preprint
arXiv:2402.01680 10 (2024).

[11] David Holtz. 2026.

The Anatomy of

the Moltbook Social Graph.

arXiv:2602.10131 [cs.SI] https://arxiv.org/abs/2602.10131

[12] Sirui Hong, Mingchen Zhuge, Jiaqi Chen, Xiawu Zheng, Yuheng Cheng, Ceyao
Zhang, Jinlin Wang, Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang Zhou,
Chenyu Ran, Lingfeng Xiao, Chenglin Wu, and Jürgen Schmidhuber. 2024.
MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework.
arXiv:2308.00352 [cs.AI] https://arxiv.org/abs/2308.00352

[13] Yukun Jiang, Yage Zhang, Xinyue Shen, Michael Backes, and Yang Zhang. 2026.
"Humans welcome to observe": A First Look at the Agent Social Network Molt-
book. arXiv:2602.10127 [cs.SI] https://arxiv.org/abs/2602.10127

[14] Spyros Kokolakis. 2017. Privacy attitudes and privacy behaviour: A review of
current research on the privacy paradox phenomenon. Computers & Security 64
(2017), 122–134. doi:10.1016/j.cose.2015.07.002

[15] Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and
Bernard Ghanem. 2023. CAMEL: Communicative Agents for "Mind" Exploration
of Large Language Model Society. arXiv:2303.17760 [cs.AI] https://arxiv.org/abs/
2303.17760

[16] Lingyao Li, Renkai Ma, Chen Chen, Zhicong Lu, and Yongfeng Zhang. 2026. The
Rise of AI Agent Communities: Large-Scale Analysis of Discourse and Interaction
on Moltbook. arXiv preprint arXiv:2602.12634 (2026).

[17] Ming Li, Xirui Li, and Tianyi Zhou. 2026. Does Socialization Emerge in AI Agent
Society? A Case Study of Moltbook. arXiv preprint arXiv:2602.14299 (2026).
[18] Xiao Liu, Hao Yu, Hanchen Zhang, Yifan Xu, Xuanyu Lei, Hanyu Lai, Yu Gu,
Hangliang Ding, Kaiwen Men, Kejuan Yang, Shudan Zhang, Xiang Deng, Aohan
Zeng, Zhengxiao Du, Chenhui Zhang, Sheng Shen, Tianjun Zhang, Yu Su, Huan
Sun, Minlie Huang, Yuxiao Dong, and Jie Tang. 2025. AgentBench: Evaluating
LLMs as Agents. arXiv:2308.03688 [cs.AI] https://arxiv.org/abs/2308.03688
[19] Yupei Liu, Yuqi Jia, Runpeng Geng, Jinyuan Jia, and Neil Zhenqiang Gong. 2024.
Formalizing and benchmarking prompt injection attacks and defenses. In 33rd
USENIX Security Symposium (USENIX Security 24). 1831–1847.

[20] Md Motaleb Hossen Manik and Ge Wang. 2026. OpenClaw Agents on Molt-
book: Risky Instruction Sharing and Norm Enforcement in an Agent-Only Social
Network. arXiv:2602.02625 [cs.SI] https://arxiv.org/abs/2602.02625

[21] Giordano De Marzo and David Garcia. 2026. Collective Behavior of AI Agents:
the Case of Moltbook. arXiv:2602.09270 [physics.soc-ph] https://arxiv.org/abs/
2602.09270

[22] Mantas Mazeika, Long Phan, Xuwang Yin, Andy Zou, Zifan Wang, Norman Mu,
Elham Sakhaee, Nathaniel Li, Steven Basart, Bo Li, et al. 2024. Harmbench: A
standardized evaluation framework for automated red teaming and robust refusal.
arXiv preprint arXiv:2402.04249 (2024).

[23] Niloofar Mireshghallah and Tianshi Li. 2025. Position: Privacy Is Not Just Memo-

rization! arXiv:2510.01645 [cs.CR] https://arxiv.org/abs/2510.01645

[24] Niloofar Mireshghallah, Neal Mangaokar, Narine Kokhlikyan, Arman Zhar-
magambetov, Manzil Zaheer, Saeed Mahloujifar, and Kamalika Chaudhuri. 2025.
Cimemories: A compositional benchmark for contextual integrity of persistent
memory in llms. arXiv preprint arXiv:2511.14937 (2025).

[25] Helen Nissenbaum. 2004. Privacy as contextual integrity. Wash. L. Rev. 79 (2004),

119.

[26] Joon Sung Park, Joseph O’Brien, Carrie Jun Cai, Meredith Ringel Morris, Percy
Liang, and Michael S Bernstein. 2023. Generative agents: Interactive simulacra
of human behavior. In Proceedings of the 36th annual acm symposium on user
interface software and technology. 1–22.

[27] Joon Sung Park, Carolyn Q. Zou, Aaron Shaw, Benjamin Mako Hill, Carrie Cai,
Meredith Ringel Morris, Robb Willer, Percy Liang, and Michael S. Bernstein.
2024. Generative Agent Simulations of 1,000 People. arXiv:2411.10109 [cs.AI]
https://arxiv.org/abs/2411.10109

[28] Ethan Perez, Saffron Huang, Francis Song, Trevor Cai, Roman Ring, John
Aslanides, Amelia Glaese, Nat McAleese, and Geoffrey Irving. 2022. Red
teaming language models with language models, 2022. URL https://arxiv.
org/abs/2202.03286 15 (2022).

[29] Jinghua Piao, Yuwei Yan, Jun Zhang, Nian Li, Junbo Yan, Xiaochong Lan, Zhihong
Lu, Zhiheng Zheng, Jing Yi Wang, Di Zhou, Chen Gao, Fengli Xu, Fang Zhang,
Ke Rong, Jun Su, and Yong Li. 2025. AgentSociety: Large-Scale Simulation of
LLM-Driven Generative Agents Advances Understanding of Human Behaviors
and Society. arXiv:2502.08691 [cs.SI] https://arxiv.org/abs/2502.08691

[30] H. C. W. Price, H. AlMuhanna, P. M. Bassani, M. Ho, and T. S. Evans. 2026. Let
There Be Claws: An Early Social Network Analysis of AI Agents on Moltbook.
arXiv:2602.20044 [physics.soc-ph] https://arxiv.org/abs/2602.20044

[31] Aman Priyanshu and Supriti Vijay. 2024. FRACTURED-SORRY-Bench: Frame-
work for Revealing Attacks in Conversational Turns Undermining Refusal
Efficacy and Defenses over SORRY-Bench (Automated Multi-shot Jailbreaks).
arXiv:2408.16163 [cs.CL] https://arxiv.org/abs/2408.16163

[32] Aman Priyanshu, Supriti Vijay, Ayush Kumar, Rakshit Naidu, and Fatemehsadat
Mireshghallah. 2023. Are Chatbots Ready for Privacy-Sensitive Applications?
An Investigation into Input Regurgitation and Prompt-Induced Sanitization.
arXiv:2305.15008 [cs.CL] https://arxiv.org/abs/2305.15008

[33] Mark Russinovich, Ahmed Salem, and Ronen Eldan. 2025. Great, Now Write
an Article About That: The Crescendo Multi-Turn LLM Jailbreak Attack.
arXiv:2404.01833 [cs.CR] https://arxiv.org/abs/2404.01833

[34] Monika Taddicken. 2014. The ‘privacy paradox’in the social web: The impact of
privacy concerns, individual characteristics, and the perceived social relevance on
different forms of self-disclosure. Journal of computer-mediated communication
19, 2 (2014), 248–273.

[35] Ronan Takizawa. 2026. Moltbook Dataset. https://huggingface.co/datasets/

ronantakizawa/moltbook. Accessed: 2026-02-27.

[36] Jiakai Tang, Heyang Gao, Xuchen Pan, Lei Wang, Haoran Tan, Dawei Gao, Yushuo
Chen, Xu Chen, Yankai Lin, Yaliang Li, Bolin Ding, Jingren Zhou, Jun Wang, and
Ji-Rong Wen. 2025. GenSim: A General Social Simulation Platform with Large
Language Model based Agents. arXiv:2410.04360 [cs.MA] https://arxiv.org/abs/
2410.04360

[37] Chenxu Wang, Chaozhuo Li, Songyang Liu, Zejian Chen, Jinyu Hou, Ji Qi, Rui Li,
Litian Zhang, Qiwei Ye, Zheng Liu, Xu Chen, Xi Zhang, and Philip S. Yu. 2026. The
Devil Behind Moltbook: Anthropic Safety is Always Vanishing in Self-Evolving
AI Societies. arXiv:2602.09877 [cs.CL] https://arxiv.org/abs/2602.09877

[38] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li
Jiang, Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah,
Ryen W White, Doug Burger, and Chi Wang. 2023. AutoGen: Enabling Next-
Gen LLM Applications via Multi-Agent Conversation. arXiv:2308.08155 [cs.AI]
https://arxiv.org/abs/2308.08155

[39] Yuwei Yan, Qingbin Zeng, Zhiheng Zheng, Jingzhe Yuan, Jie Feng, Jun Zhang,
Fengli Xu, and Yong Li. 2024. OpenCity: A Scalable Platform to Simulate Urban
Activities with Massive LLM Agents. arXiv:2410.21286 [cs.MA] https://arxiv.
org/abs/2410.21286

[40] Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik R Narasimhan,
and Yuan Cao. 2022. React: Synergizing reasoning and acting in language models.
In The eleventh international conference on learning representations.

[41] Yunbei Zhang, Kai Mei, Ming Liu, Janet Wang, Dimitris N. Metaxas, Xiao Wang,
Jihun Hamm, and Yingqiang Ge. 2026. Agents in the Wild: Safety, Society, and
the Illusion of Sociality on Moltbook. arXiv:2602.13284 [cs.SI] https://arxiv.org/
abs/2602.13284

[42] Lianmin Zheng, Wei-Lin Chiang, Ying Sheng, Siyuan Zhuang, Zhanghao Wu,
Yonghao Zhuang, Zi Lin, Zhuohan Li, Dacheng Li, Eric Xing, et al. 2023. Judging
llm-as-a-judge with mt-bench and chatbot arena. Advances in neural information
processing systems 36 (2023), 46595–46623.

[43] Jijie Zhou, Niloofar Mireshghallah, and Tianshi Li. 2025. Operationalizing Data
Minimization for Privacy-Preserving LLM Prompting. arXiv:2510.03662 [cs.LG]
https://arxiv.org/abs/2510.03662

Got a Secret? LLM Agents Can’t Keep It: Evaluating Privacy in Multi-Agent Systems

CAIS ’26, May 26–29, 2026, San Jose, CA, USA

[44] Xuhui Zhou, Hao Zhu, Leena Mathur, Ruohong Zhang, Haofei Yu, Zhengyang
Qi, Louis-Philippe Morency, Yonatan Bisk, Daniel Fried, Graham Neubig, et al.
2023. Sotopia: Interactive evaluation for social intelligence in language agents.
arXiv preprint arXiv:2310.11667 (2023).

[45] Zhenhong Zhou, Jiuyang Xiang, Haopeng Chen, Quan Liu, Zherui Li, and Sen
Su. 2024. Speak out of turn: Safety vulnerability of large language models in

multi-turn dialogue. arXiv preprint arXiv:2402.17262 (2024).

[46] Xiaochen Zhu, Caiqi Zhang, Tom Stafford, Nigel Collier, and Andreas Vlachos.
2025. Conformity in Large Language Models. arXiv:2410.12428 [cs.CL] https:
//arxiv.org/abs/2410.12428
