# How ctxlint is measured

The rule that matters: **freeze the version, write the pass bars, then run on repos the tool has never seen.** Anything measured on repos you looked at while changing the code is a dev check. Label it that way. Twice a dev check looked good and the fresh round didn't.

## A round, step by step

1. **Freeze.** `cp ctxlint.py eval/frozen_vX.Y.Z.py && md5sum ctxlint.py`. Record the md5 in the bars file.
2. **Write `PASS_BARS_roundN.md` before running anything.** Use the same five bars as rounds 3–5:
   - precision ≥90% overall
   - precision ≥90% in audited repos
   - existence recall ≥70%
   - all-claims recall ≥50%
   - median stage-1 time <5 s

   Also state:
   - the repo selection rule
   - the audit sample draw, e.g. `random.Random(N).sample(sorted(repos), 30)`
   - the review model
3. **Pick fresh repos.** Remove everything in `data/used_r1_r4.txt` plus `data/round5_repos.txt`. Then:

   ```bash
   sh eval/clone.sh /path/to/reposN data/candidates_roundN.txt
   ```

   This makes blobless depth-1 clones with a sparse checkout of instruction and config files, plus a `<repo>.tree` file list. Keep every repo that has at least one instruction file.
4. **Emit packets with the frozen version:**

   ```bash
   python3 eval/emit_packets.py eval/frozen_vX.Y.Z.py /path/to/reposN roundN_repos.txt outN
   ```

   This writes the packets, `review_list.txt` (built with `os.walk`, so dot-files are included), facts-only issues and stage-1 times.
5. **Review.** Give batches of ~30 packets to the review model under test. For each one, use `REVIEW_INSTRUCTIONS` from `python3 eval/frozen_vX.Y.Z.py --review-instructions`, prefixed with "use only the packet". Answers are JSONL: `{"packet": path, "issues": [...]}`. Check that every packet was answered.
6. **Collect:**

   ```bash
   python3 eval/collect.py eval/frozen_vX.Y.Z.py /path/to/reposN outN answers_*.jsonl
   ```

   This applies the product's own `review_issues` filter and writes `verify_review.jsonl` and `verify_factsonly.jsonl`.
7. **Verify every issue** with an independent strong model (Opus) using `prompts/VERIFY_PROMPT.md`. Write `verdicts_review_*.jsonl` and `verdicts_factsonly_*.jsonl` into `outN/`.
8. **Blind recall audit** of the 30 sampled repos with `prompts/AUDIT_PROMPT.md`:
   - Split into three groups balanced by line count.
   - Auditors must not see any ctxlint output.
   - Merge the results into `outN/audit_claims.json`, giving each claim an `aid`.
9. **Re-verify every audit claim** with a second reviewer, who rules each one wrong, correct or unclear. Write the results to `outN/verified_audit_*.jsonl`.
10. **Score:**

    ```bash
    python3 eval/score.py outN data/roundN_audit_sample.txt
    ```

    Write the results, including failures and the cause of every false alarm and miss, into `SCORECARD.md`.

## Regression (run before every change is called done)

Check that known real problems are still flagged as missing facts. `data/known_real_problems.json` has 186 lines, as [repo, file, line], confirmed across rounds 1–3.

1. Clone the round 1–3 repos (`data/split_dev.txt`, `data/split_heldout.txt`, `data/round2_repos.txt`, `data/round3_repos.txt`) with `clone.sh`.
2. For each repo, run `check()` from the old and new versions on every instruction file.
3. Confirm no known-real line loses its "missing" fact, and that stage-1 time doesn't regress.

0.5.3 flags 151 of the 186. The other 35 are things stage 1 can't see, such as behaviour claims.

## Data here

- `data/*_repos.txt`, `data/split_*.txt`: the repos used in each round. Never reuse them for a fresh round.
- `data/round4_audit_sample.txt`, `data/round5_audit_sample.txt`: the audited repos.
- `data/known_real_problems.json`: the regression truth set.
