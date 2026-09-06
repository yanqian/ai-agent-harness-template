# F048 coordinating review

## Dirty index/worktree cancellation case (real Git reproduced)

Initial role_boundary.capture uses git diff --name-only -z HEAD to find tracked dirty paths. This misses a path whose index contains a staged user change while its working-tree bytes have been restored to HEAD. Real reproduction: commit file.txt='base', change to 'staged user change', git add file.txt, write 'base' back to file.txt. git diff --name-only -z HEAD returns empty; both git diff --cached --name-only -z and git diff --name-only -z return file.txt. The boundary snapshot includes index identity but dirty protection then fails to classify the path as protected. A coding change to its staged/working contents would not require adopt.

Use the union of staged and unstaged dirty paths (plus untracked) and add a real-Git regression for cancellation. Keep NUL-separated filenames and preserve staged/unstaged distinctions. No root source change was made during child coding.

## Self-hosting and external protocol

The current parent loaded F047 completion.py before this child. If F048 changes the evaluator bridge to require scope judgment/changes.json, ensure current parent cannot accidentally bypass or misclaim new guard enrollment. Retain fail-closed behavior and document that a new coordinator may be necessary for F048's own final acceptance. Coordinator can run an authorized real-provider fixture smoke after protocol changes. Do not weaken new scope judgment because the old parent cannot supply it.

## Guard evidence retention

Historical verification currently checks scope only if boundary.json exists. For a run enrolled via boundary-required.json, deleting boundary.json must not silently turn it into a pre-F048 run and skip scope evidence validation. Use explicit enrollment when deciding required historical sidecars; test missing boundary/scope/changes artifacts after completion. Similarly, the bridge's compatibility branch should distinguish genuinely old unenrolled parents from missing boundary files on newly enrolled runs. The current parent is genuinely pre-F048 and has no boundary-required marker.
