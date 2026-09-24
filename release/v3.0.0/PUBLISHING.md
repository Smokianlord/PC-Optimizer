# GitHub release setup

- Repository: `Smokianlord/PC-Optimizer`
- Tag: `v3.0.0`
- Target branch: `main`, after committing and pushing the v3.0.0 changes
- Release title: `PC Optimizer v3.0.0`
- Release body: paste `RELEASE_NOTES.md`
- Upload assets: `release/v3.0.0/PC Optimizer v3.0.0.exe` and `release/v3.0.0/SHA256SUMS.txt`
- Mark as latest release; do not mark as prerelease

The executable must match the checksum file. The release tag should point to the commit containing the v3.0.0 source, spec, version metadata, and documentation.

## Publish through GitHub

1. Commit and push the v3.0.0 repository changes to `main`.
2. Open `https://github.com/Smokianlord/PC-Optimizer/releases/new`.
3. Create tag `v3.0.0` from the updated `main` commit.
4. Set the title and paste the contents of `RELEASE_NOTES.md` into the description.
5. Upload the two assets listed above, mark the release as latest, and publish it.

Optional screenshots for the release description: `ui_preview.png`, `ui_app_manager.png`, and `ui_maintenance.png`.
