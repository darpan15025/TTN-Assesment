# QA AI Practical Assessment – Practice Software Testing Toolshop

## Project Information

| Field | Value |
|-------|-------|
| Framework | Playwright with PrismStructure (Page Object Model) |
| Application (UI) | https://practicesoftwaretesting.com/ |
| Application (API) | https://api.practicesoftwaretesting.com/ |
| API Docs | https://api.practicesoftwaretesting.com/api/documentation |

## Prerequisites

- Node.js 18+
- npm

## Setup

```bash
cd PrismStructure
npm install
npx playwright install chromium
```

## Test Data

- Dynamic test users are generated at runtime via `prism/utils/testDataGenerator.js`
- Each test creates a unique email and password to avoid account lockouts
- Invoice billing data is defined in `prism/utils/config.js`

## Running Tests

### All tests

```bash
npm test
```

### Smoke tests only

```bash
npm run test:smoke
```

### Regression tests only

```bash
npm run test:regression
```

### UI tests

```bash
npm run test:ui              # All UI tests
npm run test:ui:smoke        # UI smoke only
npm run test:ui:regression   # UI regression only
```

### API tests

```bash
npm run test:api             # All API tests
npm run test:api:smoke       # API smoke only
npm run test:api:regression  # API regression only
```

## Reports

After execution, reports are generated in:

| Report | Location |
|--------|----------|
| HTML Report | `PrismStructure/reports/html-report/index.html` |
| JSON Results | `PrismStructure/reports/execution-results.json` |
| JUnit XML | `PrismStructure/reports/junit-results.xml` |
| Screenshots/Videos | `PrismStructure/reports/test-results/` |

View HTML report:

```bash
npm run report
```

## Repository Structure

```
qa-ai-practical-assessment/
├── FunctionalTestCase.csv          # Manual test cases
├── PrismStructure/                 # Playwright automation (Prism Framework)
│   ├── prism/
│   │   ├── pages/                  # UI page objects
│   │   ├── api/                    # API client classes
│   │   ├── fixtures/               # Test fixtures
│   │   └── utils/                  # Config and test data helpers
│   ├── tests/
│   │   ├── ui/                     # UI automation specs
│   │   └── api/                    # API automation specs
│   └── reports/                    # Execution reports
├── project-info.md                 # AI workflow documentation
├── readme.md                       # This file
└── ai-prompts/                     # Prompt history by phase
```

## Manual Test Cases

Open `FunctionalTestCase.csv` in Excel or any CSV viewer. Cases are tagged `@Smoke` or `@regression` in the Category column.

## Notes

- Invoice generation requires pressing **Confirm** twice on the checkout page
- API registration requires passwords with uppercase, lowercase, and symbols (not in breach databases)
- UI tests run against the live hosted application
