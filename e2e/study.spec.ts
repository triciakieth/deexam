import { test, expect } from "@playwright/test";
import dataset from "../src/data/questions.json" with { type: "json" };
async function practice(page: import("@playwright/test").Page) {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Practice quiz", exact: true })
    .click();
  await page.getByLabel("Randomize order").uncheck();
  await page.getByRole("button", { name: "Start practice →" }).click();
}
test("real question, source mapping, feedback, navigation, refresh and bookmarks", async ({
  page,
}) => {
  await practice(page);
  await expect(
    page.getByRole("heading", { name: "Question 1 of 20" }),
  ).toBeVisible();
  await expect(page.getByRole("region", { name: "Answer review" })).toHaveCount(
    0,
  );
  const q = dataset[0];
  await page
    .getByRole("radio", {
      name: `Option ${(q.verifiedAnswer ?? q.originalAnswer)[0].toUpperCase()}`,
    })
    .check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toContainText("Correct");
  await page
    .getByRole("button", { name: "Bookmark question", exact: true })
    .click();
  await page.getByRole("button", { name: "Next →", exact: true }).click();
  await page.getByRole("button", { name: "← Previous" }).click();
  await expect(
    page.getByRole("radio", {
      name: `Option ${(q.verifiedAnswer ?? q.originalAnswer)[0].toUpperCase()}`,
    }),
  ).toBeChecked();
  await page.reload();
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Remove bookmark", exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Dashboard", exact: true }).click();
  await expect(
    page.locator(".stat").filter({ hasText: "Questions completed" }),
  ).toContainText("1");
});
test("exam hides feedback until final submission and counts unanswered questions", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Mock exam", exact: true }).click();
  await page.getByLabel("Randomize order").uncheck();
  await page.getByRole("button", { name: "Start exam →" }).click();
  await page.getByRole("radio", { name: "Option A" }).check();
  await expect(page.getByRole("region", { name: "Answer review" })).toHaveCount(
    0,
  );
  await page.getByRole("button", { name: "Next →", exact: true }).click();
  await page.getByRole("radio", { name: "Option B" }).check();
  await page.reload();
  await expect(page.getByRole("radio", { name: "Option B" })).toBeChecked();
  await expect(page.getByRole("region", { name: "Answer review" })).toHaveCount(
    0,
  );
  await page.getByRole("button", { name: "Finish exam", exact: true }).click();
  await page.getByRole("button", { name: "Confirm final submission" }).click();
  await expect(page.locator(".exam-results")).toContainText("18 unanswered");
  const graded = dataset
    .slice(0, 20)
    .filter((q) => q.verification === "verified").length;
  await expect(page.locator(".exam-results")).toContainText(
    `0 / ${graded} correct`,
  );
  await expect(page.locator(".exam-results")).toContainText(
    `${20 - graded} ungraded questions excluded`,
  );
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toBeVisible();
});
test("filters, multi-select, backup validation, and responsive layout", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Practice quiz", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "Verification", exact: true })
    .selectOption("verified");
  const n = dataset.filter((q) => q.verification === "verified").length;
  await expect(page.locator(".setup-card .pill")).toContainText(
    `${n} available`,
  );
  if (n === 0)
    await expect(
      page.getByRole("button", { name: "Start practice →" }),
    ).toBeDisabled();
  await page
    .getByRole("combobox", { name: "Verification", exact: true })
    .selectOption("all");
  await page.getByLabel("Bank 1", { exact: true }).uncheck();
  await page.getByLabel("Bank 3", { exact: true }).uncheck();
  await page.getByLabel("Randomize order").uncheck();
  await page.getByRole("button", { name: "Start practice →" }).click();
  await page
    .getByRole("button", { name: "Go to question 4", exact: true })
    .click();
  await page.getByRole("checkbox", { name: "Option D" }).check();
  await page.getByRole("checkbox", { name: "Option E" }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toContainText("Correct");
  await page.getByLabel("Import backup file").setInputFiles({
    name: "bad.json",
    mimeType: "application/json",
    buffer: Buffer.from("{}"),
  });
  await expect(page.getByRole("status")).toContainText("Import failed");
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("button", { name: "↓ Export backup" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
test("timer expiry survives refresh and finalizes only once", async ({
  page,
}) => {
  await page.goto("/");
  const q = dataset[0];
  await page.evaluate(
    ({ id }) => {
      localStorage.setItem(
        "lakehouse-study-v1",
        JSON.stringify({
          version: 1,
          history: [],
          bookmarks: [],
          dark: false,
          session: {
            ids: [id],
            index: 0,
            mode: "exam",
            selections: {},
            submitted: [],
            finished: false,
            expiresAt: Date.now() - 1000,
          },
        }),
      );
    },
    { id: q.id },
  );
  await page.reload();
  await expect(page.locator(".exam-results")).toContainText("0 / 1 correct");
  await page.reload();
  expect(
    await page.evaluate(
      () =>
        JSON.parse(localStorage.getItem("lakehouse-study-v1")!).history.length,
    ),
  ).toBe(1);
});
test("export and valid import restore progress; incorrect review improves after retake", async ({
  page,
}) => {
  await practice(page);
  const q = dataset[0];
  const correct = (q.verifiedAnswer ?? q.originalAnswer)[0];
  const wrong = q.choices.find((c) => c.id !== correct)!.id;
  await page
    .getByRole("radio", { name: `Option ${wrong.toUpperCase()}` })
    .check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toContainText("Incorrect");
  const downloaded = page.waitForEvent("download");
  await page.getByRole("button", { name: "↓ Export backup" }).click();
  const download = await downloaded;
  expect(download.suggestedFilename()).toMatch(/lakehouse-study-.*\.json/);
  const backup = await page.evaluate(() =>
    localStorage.getItem("lakehouse-study-v1")!,
  );
  await page.getByLabel("Import backup file").setInputFiles({
    name: "backup.json",
    mimeType: "application/json",
    buffer: Buffer.from(backup),
  });
  await expect(
    page.getByRole("alertdialog", { name: "Replace study progress" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Replace with backup" }).click();
  await page.getByRole("button", { name: /^Wrong answers/ }).click();
  await expect(page.locator(".setup-card .pill")).toContainText("1 available");
  await page.getByRole("button", { name: "Start practice →" }).click();
  await page
    .getByRole("button", { name: "Replace session", exact: true })
    .click();
  await page
    .getByRole("radio", { name: `Option ${correct.toUpperCase()}` })
    .check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(page.locator(".setup-card .pill")).toContainText("0 available");
  await page.reload();
  await page.getByRole("button", { name: "Dashboard", exact: true }).click();
  await expect(
    page.locator(".stat").filter({ hasText: "Accuracy" }),
  ).toContainText("100%");
  expect(
    await page.evaluate(
      () =>
        JSON.parse(localStorage.getItem("lakehouse-study-v1")!).history.length,
    ),
  ).toBe(2);
});

test("unresolved answers stay neutral, have researched explanations, and are excluded from scores", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Practice quiz", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "Verification", exact: true })
    .selectOption("unverified");
  await page.getByLabel("Randomize order").uncheck();
  await page.getByRole("button", { name: "Start practice →" }).click();
  await expect(page.getByRole("region", { name: "Answer review" })).toHaveCount(
    0,
  );
  await expect(page.locator(".source-note")).toHaveCount(0);
  await page.getByRole("radio", { name: "Option A" }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toContainText("Not graded");
  await expect(
    page.getByRole("region", { name: "Answer review" }),
  ).toContainText("seven days");
  await expect(page.locator(".correct-choice,.wrong-choice")).toHaveCount(0);
  await expect(
    page
      .locator(".explanation a[href^='https://docs.databricks.com/']")
      .first(),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Finish practice", exact: true })
    .click();
  await page.getByRole("button", { name: "Dashboard", exact: true }).click();
  await expect(
    page
      .locator(".notice")
      .filter({ hasText: "answered questions remain ungraded" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Previous quiz results" }).locator(".."),
  ).toContainText("Not scored");
  await expect(page.locator(".recent-list .ungraded")).toHaveCount(1);
  await page
    .getByRole("button", { name: "Practice quiz", exact: true })
    .click();
  await page
    .getByRole("combobox", { name: "Review filter", exact: true })
    .selectOption("correct");
  await expect(
    page.getByRole("button", { name: "Start practice →" }),
  ).toBeDisabled();
});

test("reset requires confirmation, persists, and keeps the theme preference", async ({
  page,
}) => {
  await practice(page);
  await page.getByRole("radio", { name: "Option B" }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Bookmark question", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Toggle color theme", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Finish practice", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Reset progress", exact: true })
    .click();
  await page.getByRole("button", { name: "Cancel reset" }).click();
  expect(
    await page.evaluate(
      () =>
        JSON.parse(localStorage.getItem("lakehouse-study-v1")!).history.length,
    ),
  ).toBe(1);
  await page
    .getByRole("button", { name: "Reset progress", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Confirm reset", exact: true })
    .click();
  await page.reload();
  const saved = await page.evaluate(() =>
    JSON.parse(localStorage.getItem("lakehouse-study-v1")!),
  );
  expect(saved.history).toEqual([]);
  expect(saved.bookmarks).toEqual([]);
  expect(saved.completedSessions).toEqual([]);
  expect(saved.session).toBeNull();
  expect(saved.dark).toBe(true);
  await expect(
    page.getByRole("button", { name: "Toggle color theme" }),
  ).toHaveAttribute("aria-pressed", "true");
});

test("a corrected source key uses the documented answer and keeps the original key for review", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Practice quiz", exact: true })
    .click();
  await page.getByLabel("Bank 1", { exact: true }).uncheck();
  await page.getByLabel("Bank 2", { exact: true }).uncheck();
  await page
    .getByRole("combobox", { name: "Questions", exact: true })
    .selectOption("all");
  await page.getByLabel("Randomize order").uncheck();
  await page.getByRole("button", { name: "Start practice →" }).click();
  await page
    .getByRole("button", { name: "Go to question 82", exact: true })
    .click();
  await expect(page.locator(".source-note")).toHaveCount(0);
  await page.getByRole("radio", { name: "Option B" }).check();
  await page
    .getByRole("button", { name: "Submit answer", exact: true })
    .click();
  const review = page.getByRole("region", { name: "Answer review" });
  await expect(review).toContainText("Incorrect");
  await expect(review).toContainText("30-MB");
  await expect(review).toContainText("10 MB");
  await expect(
    page.locator(".correct-choice").getByRole("radio", { name: "Option C" }),
  ).toBeChecked({ checked: false });
  await expect(
    page.locator(".wrong-choice").getByRole("radio", { name: "Option B" }),
  ).toBeChecked();
  await page
    .getByText("Original answer-key transcription", { exact: true })
    .click();
  await expect(review.locator("pre")).toContainText("b)");
  await expect(
    review.getByRole("link", {
      name: /Known limitations of Databricks notebooks/,
    }),
  ).toBeVisible();
});
