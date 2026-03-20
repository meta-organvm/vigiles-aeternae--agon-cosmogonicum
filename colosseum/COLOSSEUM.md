# The Colosseum — Rules of Engagement

The Colosseum is simultaneously:
- **A simulation engine** (code that runs regime audits against real system state)
- **A narrative arena** (the mythological theater where Watchers argue and trade reins)
- **A Constitutional forge** (where consensus becomes immutable law)
- **The RPG hub city** (where characters return between adventures)

## The Agon Loop

```
1. SUMMON    — A regime is invoked (by schedule, community vote, or Cosmogonist decree)
2. AUDIT     — The regime's audit_rules run against real ORGANVM state
3. REPORT    — Findings produced in the regime's voice and aesthetic
4. DIVERGE   — Findings compared against what OTHER regimes found
5. CONSENSUS — Where all regimes agree → Constitutional law candidate
6. CONFLICT  — Where regimes disagree → conflict resolution
7. CHRONICLE — The Witnesses record the entire cycle immutably
8. ROTATE    — The next regime is summoned. The Agon continues.
```

## Summoning Rules

A regime can be summoned by:
- **Schedule** — round-robin through all active regimes
- **Community vote** — participants in ORGAN-VI elect the next regime
- **Cosmogonist decree** — the Demiurgi override normal rotation for cause

## Conflict Resolution

When regimes produce contradictory findings:

1. **Record the divergence.** All disagreements preserved. Divergence is data.
2. **Classify the conflict:**
   - *Perspective divergence* — same fact, different interpretation. Both preserved.
   - *Priority conflict* — same fact, different severity. Highest severity surfaced as ceiling.
   - *Structural contradiction* — mutually exclusive claims. Escalated to Cosmogonists.
3. **Cosmogonist arbitration** for structural contradictions against metaLAWs substrate.
4. **No forced consensus.** Persistent disagreement is research, not failure.

## Constitutional Threshold

A finding becomes Constitutional law when:
- **All active regimes** agree on it
- Across **at least two separate Agon cycles**
- Two-cycle requirement prevents transient agreement from becoming permanent law

If a later regime disagrees, the law is flagged for **re-evaluation** — not automatically revoked.

## The Phaethon Principle

Every regime must declare its own blind spot (the `phaethon` field in regime YAML). If the Colosseum detects that a regime's declared blind spot is manifesting in the system during its reign, a **Phaethon Warning** is raised and the regime is rotated early. The chariot of the sun must not burn the world.
