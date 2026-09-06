# Coordinator review: supported Human Eval breaks frozen legacy validation

Observed against the in-progress F047 code using a real isolated temporary fixture and actual scripts/human-eval.py subprocess:
1. Create a legacy done Feature F001 with no active_run/receipt; completion.freeze_policy captures it.
2. Run human-eval.py F001 --result pass --classification current_feature --feedback 'looks good', with HARNESS_FEATURE_LIST/HARNESS_RUNS_DIR pointing to fixture.
3. Human Eval exits 0 and appends accepted human metadata.
4. completion.verify_history(fixture, updated_state) raises 'F001: missing current-run completion receipt', because legacy_identity includes the whole human_acceptance object.

Supported feedback must not report success then leave validation broken. Also cover new_requirement feedback on a done legacy Feature. Keep frozen legacy policy immutable; preserve actual repository original 44 entries. Either provide a durable migration/feedback path or explicitly reject unsupported transition before any state mutation with clear recovery guidance. Prefer keeping the documented Human Eval functionality usable. Add regression for both outputs and resulting history verification; do not weaken receipt-era reopening or new-run requirements.
