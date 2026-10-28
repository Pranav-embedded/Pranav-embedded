# Setup (5 minutes, one time)

You can delete this file from the repo after setup. GitHub only shows `README.md` on your profile.

## 1. Upload everything
- The repo must be public and named exactly like your username: `Pranav-embedded/Pranav-embedded`
- Keep the folder layout: `README.md`, `assets/`, `scripts/`, `.github/workflows/`

## 2. Allow the workflows to save images
- Repo → Settings → Actions → General → Workflow permissions → **Read and write permissions** → Save

## 3. Dashboard token (needed only for the big metrics dashboard)
- GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
- Tick: `read:user`, `read:org`, `public_repo` (also `repo` if private repos should count)
- Copy the token → repo Settings → Secrets and variables → Actions → New repository secret
- Name it exactly `METRICS_TOKEN`

## 4. Run both workflows once
- Repo → Actions tab → **Update profile card** → Run workflow
- Repo → Actions tab → **Metrics** → Run workflow
- After that they refresh by themselves every day

## 5. Change things later
- Card text: edit the PROFILE block in `scripts/build_card.py`, then run the **Update profile card** workflow
- Project cards and highlights: edit `scripts/build_project_cards.py`, run it locally, upload the new `assets/*.svg`
- New photo: run these locally, then upload `assets/` and `scripts/portrait_ascii.txt`
  - `pip install Pillow numpy opencv-python-headless`
  - `python scripts/make_ascii.py photo.png`
  - `python scripts/make_banner.py photo.png`
  - `python scripts/build_card.py`
- If the face looks cut off in the ASCII art, change `CROP` at the top of `scripts/make_ascii.py`
- If you rename your GitHub account: rename the profile repo too, then find-and-replace `Pranav-embedded` in `README.md` and `scripts/build_card.py`
