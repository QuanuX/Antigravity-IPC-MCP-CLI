# Domain Workflows

## Preferred Verification Sequence

When inspecting a Symphony repository or installation, prefer this read-only sequence:

1. `qxctl doctor` (`symphony_doctor`)
2. `qxctl contracts` (`symphony_contracts`)
3. `qxctl modules check` (`symphony_modules_check`)
4. `qxctl knowledge invariant status --json` (`symphony_knowledge_invariant_status`)
5. `qxctl knowledge invariant check --prefix PATH --json` (`symphony_knowledge_invariant_check`) when the exact Symphony Validator installation is available
6. `qxctl inventory digest` (`symphony_inventory_digest`)
7. `qxctl status --json` (`symphony_status`)
8. `qxctl ssiag doctor --tops-id UUID` (`symphony_ssiag_doctor`) when the selected SSIAG enrollment is running
9. `qxctl stav doctor --tops-id UUID` (`symphony_stav_doctor`) when the selected STAV enrollment is running
10. `qxctl knowledge engines doctor` (`symphony_knowledge_engines_doctor`)
11. `qxctl knowledge reconcile compatibility --json` (`symphony_knowledge_reconcile_compatibility`)
12. `qxctl knowledge reconcile status --json` (`symphony_knowledge_reconcile_status`)

## Domain-Specific Guidance

- **SSIAG & STAV (`ssiag ...`, `stav ...`)**:
  - Always pass `--tops-id UUID` and explicit `--prefix` / `--version` for enrollment and supervisor routes.
  - Use `ssiag provider show|verify|readiness|installations` and `ssiag provider binding status|plan|apply|apply-status|recover` for provider trust and binding lifecycle.
  - Never pass secret values through arguments or JSON files.
- **Knowledge Lifecycle, SAV & Maestro (`knowledge ...`, `sav ...`, `maestro ...`)**:
  - Supply `absent` for the first v2 engine registry or the exact digest returned by `knowledge engines list` for later mutations.
  - Use `knowledge lifecycle observe|report|boot|apply|apply-status|apply-recover` and `ownership status|reconcile|adopt|release` with exact profile and journal digests.
  - Use `sav named-version propose|seal|lookup|list|verify` with explicit `--tops-id`, `--operation-id`, and expected registry digests.
- **SCV & SHV (`scv ...`, `shv ...`)**:
  - Read the selected installation's `schema` and `template` before constructing `--input` JSON files.
  - For SCV `.5`/`.6`, use `scv coverage ...`, `scv provider pack prepare|evaluate`, `scv composition explore|reassess`, and `scv interface show`.
  - For SHV, use `shv inspect|evaluate|schema|template`, `shv catalogue build|query|publication ...`, `shv graph project|validate|adapter ...|store ...`, `shv source|refresh|partition|materialization|inventory|dossier|pdf ...`.
- **SNV (`snv ...`)**:
  - Use `snv identity|resources|clusters|names validate`, `snv names resolve`, `snv inspect`, `snv evidence prepare|commit|status`, and `snv state plan|apply|status|recover` with explicit `--prefix`, `--version`, and private `--state-root` where required.
- **SQV & SRRAPIV (`sqv ...`, `sqv rithmic ...`)**:
  - Use `sqv schema` and `sqv template` with `--operation` (and `--adapter fred|databento_historical|databento_reference` for `request_validate`).
  - Use `sqv rithmic schema|template` and `sqv rithmic binding|session|market|order|account|history|runtime ...` for sovereign C++ Rithmic R API+ administration. If a mutating `sqv rithmic` command is refused or uncertain, inspect `sqv rithmic runtime status` and `sqv rithmic runtime attempts` before retrying.
- **SBV (`sbv ...`)**:
  - Use `sbv capabilities`, `sbv catalogue`, `sbv schema`, `sbv template`, and portable result tools (`sbv result inspect|query|export|select`) alongside experiment/planning routes (`run`, `compose`, `compose-joint`, `evaluate`, `economics`, `book`, `liquidity`, `allocation-economics`, `backend-plan`, `live-plan`).
- **SOV (`sov ...`)**:
  - Use `sov remote plan|assess|schema|template|invoke` and `sov remote ssh-endpoint|ssh-invoke` for bounded remote handoff and SSH carrier evidence.
  - Use `sov cloudflare cf ...` with explicit `--adapter-prefix`, `--adapter-version`, and `--input` for native Cloudflare toolchain administration.
  - Use `sov transport profile schema|template|inspect|plan|apply|recover` for protected transport profile administration.
