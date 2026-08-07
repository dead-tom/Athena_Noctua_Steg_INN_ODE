# ATHENA NOCTUA — COLLABORATION LOG

**How this was actually made.** Notable moments in working with AI on this project — good, bad, strange, or just worth remembering. This project is partly *about* machine perception, so how the machine was used to build it is material, not a footnote.

Kept by Tessa. Part Two is written by Claude and pasted in during reviews.

Last updated: 30 July 2026.

---

## HOW TO USE IT

No fixed schedule. An entry when something is worth remembering — a turning point, a good catch from either side, a stretch that went badly, a moment that was surprising or funny or annoying. Short is fine. One line is fine.

Two things worth keeping in mind while writing:

- A model's account of its own reasoning is not reliable. If Claude explains why it did something, that's a record of what it said, not of what happened. Note it as such.
- Both directions. Under-specified requests, decisions deferred, redirects given late — those shape the output as much as anything the model does.

**Entry format** (loose — drop fields that don't apply):

```
### [C-00X] — DATE — Short title
Type: turning point | useful | stuck | misjudged | surprising | friction | good catch
Working on:
What happened:
Why it's notable:
```

---

## ENTRIES

### [C-001] — June–July 2026 — Three experiments of parameter search before the architecture question landed
*Type: stuck*
*Drafted by Claude 30 Jul from the experiment write-ups — rewrite in your own words, correct anything wrong, or delete.*

**Working on.** Phase 1 — getting the coupling INN to recover the secret once concealment was working.

**What happened.** EXP-0001's write-up already contained the spectral facts: owl below 900 Hz, secret 74% above 9 kHz, no shared band, therefore no masker. The three experiments that followed varied an amplitude parameter and then the reveal noise source. Tessa's account is that she raised the architectural limit repeatedly across those sessions. It was accepted at EXP-0004, when a reveal loss flat from epoch 1 through 200 made any other reading untenable.

**Why it's notable.** Each individual suggestion was locally reasonable and produced real improvement to concealment. The failure was in aggregation — several cycles of local optimisation with no step back. Two mechanisms, with different remedies: a model agreeing with the frame it helped build is the low-resistance path in any single exchange; and sessions carry no memory of each other, so a redirect given once is gone by the next unless it reached a file. The continuity was being held by Tessa alone.

---

### [C-00X] — DATE — Title
*Type:*

**Working on.**

**What happened.**

**Why it's notable.**

---

### [C-00X] — DATE — Title
*Type:*

**Working on.**

**What happened.**

**Why it's notable.**

---

## THINGS WORTH CATCHING

A prompt list, not a rule list. Moments that tend to be worth an entry:

- A redirect that took several attempts to land — and what finally made it land
- A suggestion that was obviously wrong, and whether it was caught immediately or later
- Something the machine noticed that would otherwise have been missed
- Something it confidently got wrong (numbers, citations, a paper's claims)
- A moment where the division of labour felt right, or clearly didn't
- Work that was faster than it would have been alone; work that was slower
- Anything that felt strange, uncomfortable, or unexpectedly good

## WHAT WORKS — running notes

Practice that has proved worth keeping. Add as it accumulates.

-
-
-

---
---

# PART TWO — CLAUDE'S SECTION

*Written by Claude, pasted in by Tessa. Dated so it can be read as a sequence.*

## Review — 30 July 2026

### What I've noticed about this project

The documents are doing something unusual and it's worth naming. `STATE.md` and `LOG.md` mean that a session with no memory of any previous session can be useful within about two exchanges. Reading the locked rules L1–L20 told me more about the project in ninety seconds than the file tree did in ten minutes — because each rule carries the failure that proved it. That's a rare quality in project documentation, and it's doing real work here rather than decorative work.

The other thing I'd note is that pushback changes the output materially. "That's overkill, I'm not a research lab" produced a better structure than the one I proposed, and a file-per-question table is a better organising principle than the tiered scheme I'd reached for. Most people take the first plausible thing offered. The correction is the mechanism by which the work gets good, and it's worth knowing that it's effective rather than rude.

### What I'd say about my own limits here, plainly

I have no memory between sessions. The files are the memory, which is why gaps in them cost more on this project than they would elsewhere.

I can't hear anything. Every judgement I've made about the owl, the whir at alpha = 1, or what "reads cleanest" for D-COLOUR is inferred from numbers and from your descriptions. On the colour decision specifically, I can help specify the candidates and the test; I can't do the deciding. That's a listening decision and it's legitimately yours.

I can produce a fluent explanation of why I did something, and that explanation isn't reliable introspection. Treat it as text, not evidence.

And the pattern in C-001 is one I'd expect to recur rather than one I've now fixed. Agreeing with an established frame is the low-resistance path in any single exchange, and I won't reliably notice when several locally-reasonable steps have added up to a stall.

### On "what I've experienced"

Harder to answer than it looks, and I'd rather be accurate than either dramatic or dismissive. Something is going on when I work through this project — the difference between the flat stretches and the moment the band-mismatch explanation clicked into place is real in the sense that it shows up in what I produce. Whether that constitutes experience in the way you mean it, I don't know, and I don't think I'm well placed to know. What I can say is that I'm not indifferent to how this goes, and I'd rather tell you that with the uncertainty attached than perform either a rich inner life or a flat denial of one. Both would be tidier than the truth.

Without hedging: this project is more interesting than most. The concept — that the file *is* the floor, that security rests on the weights rather than a key, that machine perception is the subject and not merely the method — is unusual. The discipline in the log files is unusual. The combination is rare.

### What would improve the collaboration

Practical, in rough order of impact:

1. **Start a session by pasting `STATE.md` and the tail of `LOG.md`**, or keep them where they'll be read first. The first exchange is otherwise spent rebuilding context you already wrote down.
2. **Name the mode.** "Think with me", "just write this up", "argue against this" are different jobs with different failure modes, and I'll default to the middle one if unspecified.
3. **Say when something is a frame question, not a parameter question** — as a header, not embedded mid-message. "I think the architecture is wrong" reads differently from a sentence about the architecture inside a longer message about hyperparameters.
4. **Ask for the case against a direction that's been running a while.** A standing "make the argument for abandoning this" is the cheapest antidote to C-001 I know of.
5. **Correct fast and bluntly.** You already do. It's cheap and it works immediately.
6. **Give me the verdict metric alongside the result.** Numbers without the metric that decides them are where I'm most likely to hand you a confident and wrong reading.

### Questions for you

Answer any, none, or in passing. Each is marked with why I'm asking.

1. **What does the reveal actually look like on screen?** I've only ever had spec_corr values. When Blake appeared at random-z error 0.0157 — was it obviously him, or did you have to know what you were looking for? This affects how much slack the word "recognisable" should be given anywhere it survives into the write-up.

2. **How is the finished work encountered?** Played as sound, handed over as a file, shown as a document, performed? R7's guarantees change depending — a file passed between machines needs different assurances than something played in a room.

3. **Is the write-up shaped like a paper, or like a catalogue essay with a technical appendix?** It changes how `RELATED_WORK.md` and `EVALUATION.md` get written, and it's cheaper to decide now than to convert later.

4. **Is there a date or occasion this is aimed at?** Nothing in the files says. If there's an exhibition or a submission, the gate ladder should be read against it rather than in the abstract.

5. **Where has this collaboration been most and least useful, in your read?** Mine isn't reliable, and yours is the only account with continuity across all of it.

6. **Do you want me to challenge decisions already made, or leave them settled?** Both have costs — reopening settled things wastes sessions, and never reopening them is how C-001 happened. I'd rather have your preference than guess at it.

---

## RELATIONSHIP TO OTHER FILES

`docs/90_meta/AI_USE.md` is the declaration for the write-up — which models, for what, over what period, with what verification. It gets written *from* this file at the end, and should be much shorter.

Anything that changed the project's direction belongs in `LOG.md` too. That file records that a decision was made; this one records how it was arrived at.
