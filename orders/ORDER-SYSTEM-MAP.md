# Order → System Function Map

Each Watcher Order maps to concrete ORGANVM CLI commands, SOPs, and system functions. This is the bridge between mythology and operations.

## I. Architects → Design Law

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Schema validation | `organvm-validate <file>` | SOP--genesis-dna |
| Naming conventions | `organvm ontologia resolve <name>` | SOP--ontological-renaming |
| Structural standards | — | CONSTITUTION-- documents |
| Context file generation | `organvm context sync` | — |
| Registry schema enforcement | `organvm registry validate` | — |
| Seed contract verification | `organvm seed validate` | — |

## II. Oracles → Predictive Monitoring

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| System health overview | `organvm omega status` | — |
| Living Data Organism | `organvm organism` | — |
| Metrics forecasting | `organvm metrics calculate` | — |
| Soak monitoring | `organvm ci health` | SOP--system-dashboard-telemetry |
| Pressure point detection | `vigiles colosseum run --regime <any>` | SOP--autopoietic-systems-diagnostics |
| Deadline tracking | `organvm deadlines` | — |

## III. Seraphim → Active Protection

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Governance audit | `organvm governance audit` | SOP--structural-integrity-audit |
| CI enforcement | GitHub Actions on push | SOP--the-descent-protocol |
| Data integrity guards | `save_registry()` min-50 guard | — |
| Branch protection | GitHub branch rules | SOP--promotion-and-state-transitions |
| Security audit | — | SOP--security-and-accessibility-audit |
| Dependency graph validation | `organvm governance check-deps` | — |

## IV. Psychopomps → State Transitions

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Promotion state machine | `organvm governance promote <repo> <target>` | SOP--promotion-and-state-transitions |
| Repo onboarding | — | SOP--repo-onboarding-and-habitat-creation |
| Theory-to-concrete gate | — | SOP--theory-to-concrete-gate |
| The Membrane Protocol | — | SOP--the-membrane-protocol |
| Blast radius impact | `organvm governance impact <repo>` | — |
| Styx pipeline traversal | — | SOP--styx-pipeline-traversal |

## V. Smiths → Adversarial Testing

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Stranger test | — | SOP--stranger-test-protocol |
| Polymorphic agent testing | — | SOP--polymorphic-agent-testing |
| Regression testing | `pytest` across all repos | — |
| Adversarial audit | `vigiles colosseum run --regime <adversarial>` | — |
| Contradiction scanning | `vigiles colosseum compare --regimes <all>` | — |
| Fuzzing | — | — |

## VI. Witnesses → Immutable Recording

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Event log | `organvm ontologia events` | — |
| Claims registry | Claims JSONL at `~/.organvm/claims.jsonl` | — |
| Session transcripts | `organvm session transcript <id>` | SOP--session-self-critique |
| Git history | `git log` | — |
| Chronicle of the Agon | `vigiles colosseum chronicle` | — |
| Append-only audit trail | Chronicle JSONL in `chronicles/` | — |

## VII. Cosmogonists → Meta-Systemic Coherence

| System Function | CLI Command | SOP |
|----------------|-------------|-----|
| Living Data Organism | `organvm organism --omega` | — |
| Regime rotation | `vigiles colosseum compare --regimes <all>` | — |
| Constitutional consensus | `vigiles colosseum consensus` | — |
| Meta-governance | Design spec Section 5.2 (Colosseum Loop) | — |
| Agon rule-setting | `colosseum/COLOSSEUM.md` | — |
| Phaethon detection | Internal (automatic during audit) | — |

## Cross-Order Dependencies

```
Architects DECLARE → Seraphim PROTECT → Psychopomps GATE
    ↑                                         ↓
Cosmogonists OBSERVE ← Witnesses RECORD ← Smiths TEST
    ↑                                         ↓
    └──────────── Oracles FORECAST ───────────┘
```
