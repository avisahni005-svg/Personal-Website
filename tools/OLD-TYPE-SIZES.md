# Old type sizes (to restore on 16 Dec 2026)

Before the grading change (Nov 2026) the site used:

- body / section headers: `--fs-base: 13.266px` (12.375px below 1000px wide; 16.83px from 1700px; 20.79px from 2100px; 25.74px from 2600px)
- captions: 0.8 x body = 10.6px
- headlines: `--fs-head: 3.8727rem` = 51.4px on laptop
- phone: `--fs-base: 13.86px`, `--fs-head: 3.0909rem` = 42.8px
- logo gap `--gap-logo: 1.364rem`, Playground title gap `1.364rem`, Playground title `white-space: nowrap`

Last commit with these values: `bb8e9b98705d3f062c21364851028a55430aaab9` (main, after PR #11).
The change was commit `dd90a32` "Type sizes: body 16.25px...".

To restore: `git apply tools/restore-old-type-sizes.patch`, then `python3 tools/build.py`, commit, open a PR into `main` and merge.
