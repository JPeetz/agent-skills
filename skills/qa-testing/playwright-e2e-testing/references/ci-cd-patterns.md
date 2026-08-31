# CI/CD Patterns for Playwright

## GitHub Actions — Complete Workflow

```yaml
name: Playwright Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1-5'  # Daily weekday run

jobs:
  e2e:
    timeout-minutes: 30
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3, 4]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shard }}/4
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: report-${{ matrix.shard }}
          path: test-results/
```

## GitLab CI

```yaml
playwright:
  image: mcr.microsoft.com/playwright:v1.56.0-focal
  parallel: 4
  script:
    - npm ci
    - npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL
  artifacts:
    when: always
    paths: [test-results/]
    expire_in: 7 days
```

## CircleCI

```yaml
executors:
  playwright:
    docker:
      - image: mcr.microsoft.com/playwright:v1.56.0-focal
jobs:
  test:
    executor: playwright
    parallelism: 4
    steps:
      - checkout
      - run: npm ci
      - run:
          command: |
            npx playwright test --shard=$(expr $CIRCLE_NODE_INDEX + 1)/$CIRCLE_NODE_TOTAL
```

## Performance Optimization

| Strategy | Impact | Configuration |
|----------|--------|---------------|
| Browser cache | -2min cold start | `cache: ['~/.cache/ms-playwright']` in CI |
| npm cache | -30sec install | `cache: 'npm'` in setup-node |
| Sharding | 4x speedup | Matrix strategy with `--shard` |
| Selective tests | 10x for PRs | `--grep` smoke tests on PR, full on main |
| Workers | CPU-bound tuning | `workers: process.env.CI ? 4 : undefined` |

## Failure Notification

```yaml
- name: Notify on failure
  if: failure()
  uses: slackapi/slack-github-action@v2
  with:
    webhook: ${{ secrets.SLACK_WEBHOOK }}
    webhook-type: incoming-webhook
    payload: |
      {
        "text": "⚠️ Playwright tests failed on ${{ github.ref_name }}: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
      }
```

## Docker Container for Isolated Runs

```dockerfile
FROM mcr.microsoft.com/playwright:v1.56.0-focal
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
CMD ["npx", "playwright", "test"]
```

Run: `docker build -t playwright-tests . && docker run playwright-tests`