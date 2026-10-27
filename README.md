# Lakehouse Study — Databricks exam reviewer

A standalone React + TypeScript + Vite application. No ChatGPT session, API key, database, or Databricks workspace is needed to study. Tailwind CSS is integrated alongside the responsive stylesheet. Question data and PDF-derived images ship with the application.

## Run locally

Install Node.js 22.12+ or 24 LTS and npm, then run from the project directory:

```sh
npm ci
npm run dev
```

Open the address printed by Vite in your own browser. Production commands:

```sh
npm run build
npm run preview
```

The deployable website is generated in `dist/`. Serve this directory over HTTP; do not open `index.html` directly with a `file://` URL.

## Study workflow

- **Practice quiz:** select one or all banks, topic, review status, verification status (including correctly answered, incorrectly answered, unanswered, and bookmarked reviews), and 10/20/40/all questions. Shuffle is optional. Choose an answer, then submit to see feedback and per-option explanation status. Multi-select answers require the exact answer set; there is no partial credit.
- **Mock exam:** optional time limit, selections retained while navigating, and no feedback until final submission or timer expiry. Unanswered verified questions count as incorrect; unresolved questions are ungraded and excluded from the denominator. A deadline is saved, so reloading does not reset the timer.
- **Dashboard / Performance:** the latest answer per source question determines completed/correct/incorrect/accuracy and topic completion. Attempt history is retained so a corrected mistake can be distinguished from its earlier incorrect attempt. Accuracy uses only documentation-verified questions; unresolved attempts are saved as ungraded. Finish an exam or click **Finish practice** to save a previous-quiz result. Use **Reset progress** and its confirmation to clear browser study data; export a backup first. Active exam answers do not enter dashboard scores until completion.
- **Wrong answers / Bookmarks:** select a filtered practice set and start it. A question leaves the wrong-answer set after its latest submitted answer becomes correct. You can change the topic to focus review on a weak area; the topic table shows accuracy and completion.
- **Navigation:** previous/next and numbered jump buttons preserve selections. Starting another session asks before discarding an unfinished session. Submitted practice answers remain in history.
- **Backups:** export JSON from the footer. Import validates question IDs, option mappings, session state, and format before asking to replace current progress. It recomputes scores instead of trusting imported correctness fields. Export your current backup before replacing it.
- **Appearance:** light/dark setting persists with progress. Controls support keyboard navigation and visible focus.

Progress lives in local storage under `lakehouse-study-v1`, scoped to this browser and website origin. A local development site and a deployed site have separate storage; use export/import to move progress. Clearing browser site data removes progress. Storage failures are reported; export a backup when storage is unavailable. There is no account sync or server-side progress storage.

## Question provenance and verification

Imported **271 real questions**: Bank 1 **91**, Bank 2 **90**, Bank 3 **90**. All **271** were researched and have saved explanations for every choice. **216** have a documentation-supported answer set; **55 remain unresolved/unverified** because of ambiguity, malformed source code, outdated premises, missing context, or documentation gaps. Unresolved questions stay available but are **not graded**. There are **11 supported answer-key corrections** plus **2 explicitly outdated key premises**. No exact complete-question duplicates were found; **11** similar prompt pairs remain separately available.

Read [the full research report](RESEARCH_REPORT.md) and [the 271-question checklist](research/CHECKLIST.md) for counts, corrections, unresolved findings, and direct official references.

See `src/data/import-report.json` for exact current counts and flags, and `src/data/questions.json` for every entry. Source PDFs and layout text are retained in `public/sources/`; prompt, option, and full-question images are in `public/question-images/`.

Every question retains source bank, original filename, original question number, PDF page references, original wording as rendered images, choices, original key transcription, and verification status. Images are the authoritative presentation of code, screenshots, and unusual source formatting. Text extraction is a transcription, not a rewrite. Image-only choices are flagged instead of inventing code. Open the full scan or original PDF to enlarge content. Question types support single and multiple answers.

Exact duplicates are compared using whitespace-normalized prompt and labeled option text. The default combined quiz removes exact duplicates within selected filters; inventory and source files retain every original reference. Image-only choices and prompt diagrams participate through hashes of the preserved native images; empty text alone cannot establish a duplicate. Similar or reworded questions remain distinct.

**Source answer keys are not authoritative.** Verified entries have independently reviewed answers, an explanation for every option, key concepts, exam tips, official documentation URLs, relevant headings, and retrieval dates. If a verified answer conflicts with the key, grading uses the verified answer and shows a source warning. All other entries are explicitly **Unverified**: the original PDF key is shown only for comparison, and no unsupported answer is graded as definitively correct. The saved per-choice research explains why the item remains unresolved. In particular, some source material uses old Repos/DLT terminology or ambiguous scenarios. The study score is not a guarantee of performance on the actual certification exam.

Research uses only official `docs.databricks.com` pages. Retrieved text and URL metadata are in `research/`. `research/question-reviews.json` and the authored `scripts/review_bank*.py` batches record the per-question decisions. `scripts/verify_questions.py` is the legacy 39-question bootstrap and is not the current research source of truth. It does not automatically declare all fetched topics verified. Documentation links open the actual official website; root documentation links on unverified items are research entry points, not citations supporting the key.

## Reproduce the PDF import (optional)

Normal web installation does **not** require Python. The imported database and images are already included. To rebuild the database from the preserved originals:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
python scripts/import_questions.py
python scripts/apply_reviews.py
python scripts/categorize_questions.py
python scripts/extract_native_images.py
python scripts/audit_import.py
python scripts/final_report.py
npm test
npm run build
```

The importer uses PDF coordinates to separate two-column choices and three-column answer keys, and asserts complete numbering and mapped keys. This can take several minutes. Run the saved-review application and categorization scripts after importing; importing alone resets entries to unverified. Native screenshot extraction preserves embedded code/figures at original resolution. Applying saved reviews restores prior documented findings; it does not perform a new research review. `research/sources.json` and the checked-in retrieved text record the sources used for existing explanations. To refresh documentation separately, provide a JSON mapping of evidence names to official URLs to `python scripts/research_batch.py /path/to/urls.json`, then review changed documentation **before** applying or changing verification. Use `python scripts/check_doc_links.py` for actual citation URL checks. A successful HTTP fetch alone does not verify an answer. Keep the stored evidence hashes and explanations consistent with the exact reviewed source snapshot.

## Tests

```sh
npm test
npm run build
npm run test:e2e
```

The browser tests use system Chromium at `/usr/bin/chromium`. Set `CHROMIUM_PATH` to your installed Chrome/Chromium executable if necessary. If using Playwright's browser distribution instead, install it with `npx playwright install chromium` and set `CHROMIUM_PATH` to that executable. Browser tests start their own Vite server on port 4173. They also test neutral unresolved-question feedback, historical quiz summaries, confirmed progress reset, and preserved appearance settings. They cover real question rendering and grading, practice feedback, navigation and refresh, bookmarks, exam feedback hiding, final submission, multi-select, filters, malformed backups, mobile width, and timer expiry. Unit tests additionally audit every imported question/answer mapping and source asset, exact-set grading, score calculation, shuffling, persistence, and backup validation.

## Deploy to Vercel

1. Save this project to your GitHub repository (including `public/`, `src/data/`, and `package-lock.json`; exclude `node_modules/` and `dist/`).
2. Sign in to Vercel and choose **Add New → Project**; import the repository.
3. Select **Vite**, repository root as the root directory, `npm run build` as build command, and `dist` as output directory. These are also recorded in `vercel.json`.
4. Use Node.js 22 or 24 in project settings. No environment variables are required.
5. Click **Deploy**, then open the deployment URL. Start a practice session and export a backup to confirm the browser workflow.
6. Future pushes to the configured production branch trigger redeployment. Browser progress stays associated with the same website origin; use a backup when moving to a new domain.

## Deploy to Netlify

1. Push the complete project to GitHub as above.
2. In Netlify choose **Add new project → Import an existing project**, select GitHub, and choose the repository.
3. Use repository root, build command `npm run build`, and publish directory `dist`. `netlify.toml` provides these settings and Node.js 22.
4. Choose **Deploy**, open the published URL, and test a practice session.
5. Alternatively run `npm run build` locally and upload the resulting `dist/` directory through Netlify’s manual deployment UI.

This application uses in-page navigation, so it needs no SPA rewrite or backend routes. All assets use root-relative paths; deploy at a domain root. This task prepares deployment files but does not publish a live site or push to GitHub automatically. The supplied PDFs are bundled for your requested personal reviewer; choose appropriate access controls when deploying your copy.
