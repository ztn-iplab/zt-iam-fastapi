# AIg Tamarin Verification

This directory contains the Tamarin models used to verify the core trace semantics of Actor Integrity (AIg).

## Models

- `aig_actor_integrity.spthy`
  - models authentication, explicit takeover, and two protected actions under one session
- `aig_security_property.spthy`
  - models abstract confidence transitions, direct grant, and recovery-based grant

These models are intentionally abstract. They do not encode concrete telecom, device, or behavioral signals. Instead, they verify the trace-level authorization consequences of the AIg rule.

## Prerequisites

- `tamarin-prover` available on `PATH`
- `maude` installed and reachable by Tamarin

The runs were refreshed with:

- Tamarin `1.10.0`
- Maude `2.7.1`

You can confirm your local setup with:

```bash
tamarin-prover --version
```

## Reproducing the AIg proofs

From the project root:

```bash
cd <PROJECT_ROOT>
./scripts/run_tamarin_aig_actor_integrity.sh
./scripts/run_tamarin_aig_security.sh
```

If the scripts are not executable in your environment, use:

```bash
cd <PROJECT_ROOT>
bash ./scripts/run_tamarin_aig_actor_integrity.sh
bash ./scripts/run_tamarin_aig_security.sh
```

In this README and in the sanitized proof outputs, `<PROJECT_ROOT>` denotes the local checkout directory of the repository on the reproducing machine.

## Output files

The proof outputs are written to:

- `tamarin/results/aig_actor_integrity.txt`
- `tamarin/results/aig_security_property.txt`

To inspect the proof summaries directly:

```bash
tail -n 20 tamarin/results/aig_actor_integrity.txt
tail -n 20 tamarin/results/aig_security_property.txt
```

## Verified properties

We report the following verified properties:

| Property | Source theory |
| --- | --- |
| Actor binding for first protected action | `aig_actor_integrity.spthy` |
| Actor continuity across protected actions | `aig_actor_integrity.spthy` |
| Direct grant requires high confidence | `aig_security_property.spthy` |
| Low-confidence grant requires recovery approval | `aig_security_property.spthy` |
| Decay requires reinforcement before later direct grant | `aig_security_property.spthy` |
| Recovery is bound to the same actor-request pair | `aig_security_property.spthy` |

The corresponding Tamarin lemmas are:

- `action1_requires_auth_or_takeover_to_actor`
- `actor_continuity_between_actions_unless_takeover`
- `direct_grant_requires_high_confidence_history`
- `low_confidence_grant_requires_stepup`
- `decay_then_direct_grant_needs_reinforcement`
- `stepup_is_actor_request_bound`

## Symbol guide

### Actor-integrity theory

- `a`: the actor currently controlling the session
- `b`: a second actor introduced by takeover
- `s`: the session identifier
- `AuthBound(a, s)`: actor `a` authenticated and established session `s`
- `Takeover(s, a, b)`: control of session `s` transfers from actor `a` to actor `b`
- `ActionAccepted(a, s, 'act1'/'act2')`: the first or second protected action is accepted for actor `a`
- `PreAct1`, `PreAct2`: intermediate state facts before the first and second protected actions

### Authorization-semantics theory

- `a`: actor identifier
- `r`: protected request or action context
- `CState(a, r, 'high'/'low')`: abstract AIg confidence state for actor `a` and request `r`
- `Decay(a, r)`: confidence falls because reinforcing evidence is absent
- `Reinforce(a, r)`: confidence is restored by new supporting evidence
- `GrantNoStepUp(a, r)`: direct authorization without recovery
- `StepUpApproved(a, r)`: recovery approval event for the same actor-request pair
- `GrantWithStepUp(a, r)`: authorization granted through the recovery path

The symbols are intentionally abstract. They represent trace events and authorization states, not concrete telecom fields, device identifiers, or numeric confidence values.

## Expected proof summary

For `aig_actor_integrity.spthy`, the summary should end with:

```text
action1_requires_auth_or_takeover_to_actor (all-traces): verified
actor_continuity_between_actions_unless_takeover (all-traces): verified
```

For `aig_security_property.spthy`, the summary should end with:

```text
direct_grant_requires_high_confidence_history (all-traces): verified
low_confidence_grant_requires_stepup (all-traces): verified
decay_then_direct_grant_needs_reinforcement (all-traces): verified
stepup_is_actor_request_bound (all-traces): verified
```

## Scope note

These proofs validate the abstract authorization semantics of AIg. They do not prove that real-world observation sources always detect actor transfer correctly, and they do not model numeric confidence calibration. Those aspects are evaluated separately in the empirical sections of the manuscript.
