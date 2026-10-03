# Roadmap

Each item has an expected result so it's clear when it's done. Move finished items into CHANGELOG.

| # | Item | Expected result |
|---|---|---|
| 1 | Focus edition as MP4 (record the player) | `build_video.py --focus` produces an MP4 where the ring motion and dimming match the player, frame-accurate to sentence starts |
| 3 | Cue authoring aid | `build_player.py --suggest-cues` prints a draft `focus_cues.py` (one selector per sentence from default reveals) so authors edit instead of writing from scratch |
| 4 | Auto layout lint | `--preview` also reports elements overflowing the 1080px canvas or the footer, and `sN` classes beyond the step count, without needing screenshots |
| 5 | Shareable artifact | Option to publish the player (HTML + audio) as a private hosted page; audio stays under the size limit |
| 6 | Skill evals | Run `evals/evals.json` with and without the skill; record pass rates for the assertions |
| 7 | Stable slide ids for cues | Cue keys can use a slide id (`slide(..., id="rrf")`) so inserting a slide doesn't shift every later `"slide.step"` key |
| 8 | Real animation for visual proofs | `slide(..., clip="pgrid.mp4")` embeds a Manim-rendered clip (pair grid shrinking, window sliding, stack push/pop) in both the MP4 and the player, timed to the step narration |
