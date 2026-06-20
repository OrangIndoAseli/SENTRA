# Git and Monorepo Guide

## Recommended Setup

For this hackathon, there are two viable options.

### Option A: Separate Repositories

```text
sentra-ml
sentra-backend
sentra-frontend
```

This is the safest option if each member works independently.

### Option B: Monorepo

```text
sentra/
  apps/
    ml/
    backend/
    frontend/
  docs/
  README.md
```

Use this if the team wants one GitHub repo for the whole product/demo.

## Suggested Monorepo Layout

```text
sentra/
  apps/
    ml/
      app/
      tools/
      models/
      API_CONTRACT.md
      requirements.txt
      run_detector.py
    backend/
    frontend/
  docs/
    architecture.md
    api-contract.md
  README.md
  .gitignore
```

Do not commit generated ML artifacts:

```text
apps/ml/datasets/
apps/ml/runs/
apps/ml/logs/
apps/ml/.venv/
apps/ml/.python312/
apps/ml/models/*.pt
```

Store model weights outside Git:

```text
Google Drive
Hugging Face
GitHub Release
local shared folder
```

Then document the download location in `models/README.md`.

## Branch Naming

```text
main
dev
ml/dual-model-detector
ml/cctv-stream
be/detection-api
fe/dashboard
docs/api-contract
```

## Commit Examples

```text
feat(ml): add dual-model helmet and vest detection
docs(api): add ML detection response contract
feat(be): store detection events
feat(fe): add multi-camera dashboard
fix(ml): improve vest matching threshold
```

## Pull Request Rule

Before merging to `main`:

```text
ML API starts successfully
BE can call /detect-image
FE can show sample detection data
README/API contract updated
```
