import { describe, it, expect } from "vitest";
import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import {
  questions,
  byId,
  grade,
  evaluate,
  finishPractice,
  summarizeSession,
  emptyProgress,
  filterQuestions,
  shuffle,
  stats,
  recordAttempt,
  parseBackup,
  completeExam,
  toggleSelection,
  loadProgress,
  saveProgress,
  STORAGE_KEY,
  type Session,
} from "./model";
import report from "./data/import-report.json";
describe("real PDF import integrity", () => {
  it.each([
    [1, 91],
    [2, 90],
    [3, 90],
  ])("imports every question and key from bank %i", (bank, count) => {
    const rows = questions.filter((q) => q.bank === bank);
    expect(rows).toHaveLength(count);
    expect(rows.map((q) => q.number)).toEqual(
      Array.from({ length: count }, (_, i) => i + 1),
    );
  });
  it("maps all answer keys to unique option labels and retains source assets", () => {
    expect(new Set(questions.map((q) => q.id)).size).toBe(271);
    for (const q of questions) {
      expect(q.text.length, q.id).toBeGreaterThan(10);
      expect(q.choices.length, q.id).toBeGreaterThanOrEqual(2);
      expect(new Set(q.choices.map((c) => c.id)).size, q.id).toBe(
        q.choices.length,
      );
      for (const key of q.originalAnswer)
        expect(
          q.choices.map((c) => c.id),
          q.id,
        ).toContain(key);
      for (const path of [
        ...q.promptImages,
        ...(q.promptFigures ?? []),
        ...q.sourceImages,
        ...q.choices.map((c) => c.image),
      ])
        expect(existsSync(`public${path}`), path).toBe(true);
      expect(q.pages.length).toBeGreaterThan(0);
    }
  });
  it("requires per-option explanations and official citations for verified entries", () => {
    for (const q of questions) {
      if (q.verification === "verified") {
        expect(q.verifiedAnswer, q.id).not.toBeNull();
        expect(q.references.length, q.id).toBeGreaterThan(0);
        for (const c of q.choices)
          expect(q.explanations[c.id]?.length, q.id + c.id).toBeGreaterThan(35);
        for (const ref of q.references)
          expect(new URL(ref.url).hostname).toBe("docs.databricks.com");
      } else expect(q.verifiedAnswer).toBeNull();
    }
    expect(report.verified).toBe(
      questions.filter((q) => q.verification === "verified").length,
    );
  });
});
describe("research completeness and cautious grading", () => {
  it("retains per-option research, official references, and original keys for every real question", () => {
    expect(report.researched).toBe(271);
    expect(report.pendingResearch).toBe(0);
    for (const q of questions) {
      expect(q.analysis?.length, q.id).toBeGreaterThan(60);
      expect(q.reviewedAt, q.id).toBeTruthy();
      expect(q.references.length, q.id).toBeGreaterThan(0);
      expect(Object.keys(q.explanations).sort(), q.id).toEqual(
        q.choices.map((c) => c.id).sort(),
      );
      for (const c of q.choices)
        expect(q.explanations[c.id].length, q.id + c.id).toBeGreaterThan(70);
      for (const ref of q.references)
        expect(new URL(ref.url).hostname, q.id).toBe("docs.databricks.com");
    }
  });
  it("does not score an unresolved source key or include it in wrong-answer filters", () => {
    const q = questions.find((q) => q.verification !== "verified")!;
    expect(evaluate(q, q.originalAnswer)).toBeNull();
    const p = recordAttempt(emptyProgress(), q, q.originalAnswer, "practice");
    expect(stats(p.history)).toEqual({
      answered: 1,
      correct: 0,
      incorrect: 0,
      ungraded: 1,
      accuracy: 0,
    });
    expect(
      filterQuestions(
        {
          banks: [1, 2, 3],
          topic: "all",
          status: "incorrect",
          verification: "all",
        },
        p,
      ),
    ).toHaveLength(0);
    const restored = parseBackup(
      JSON.stringify({ ...p, history: [{ ...p.history[0], correct: true }] }),
    );
    expect(restored.history[0].correct).toBeNull();
  });
  it("separates verified success, failure, and ungraded attempts in the same exam", () => {
    const good = questions.find((q) => q.verification === "verified")!,
      bad = questions.find((q) => q.verification !== "verified")!;
    const ids = [good.id, bad.id];
    const p = completeExam({
      ...emptyProgress(),
      session: {
        ids,
        index: 0,
        mode: "exam",
        selections: {
          [good.id]: good.verifiedAnswer!,
          [bad.id]: bad.originalAnswer,
        },
        submitted: [],
        finished: false,
        expiresAt: null,
      },
    });
    expect(stats(p.history)).toEqual({
      answered: 2,
      correct: 1,
      incorrect: 0,
      ungraded: 1,
      accuracy: 100,
    });
    expect(
      filterQuestions(
        {
          banks: [1, 2, 3],
          topic: "all",
          status: "correct",
          verification: "all",
        },
        p,
      ).map((q) => q.id),
    ).toEqual([good.id]);
  });
  it("has a successful live documentation check for every cited URL", () => {
    const checks = JSON.parse(
      readFileSync("research/link-checks.json", "utf8"),
    ) as { url: string; status?: number; error?: string }[];
    for (const q of questions)
      for (const ref of q.references)
        expect(checks.find((r) => r.url === ref.url)?.status, ref.url).toBe(
          200,
        );
  });
});
describe("session results and evidence integrity", () => {
  it("archives submitted practice only, once, and preserves original attempt history", () => {
    const good = questions[0],
      unknown = questions.find((q) => q.verification !== "verified")!;
    let p = recordAttempt(
      emptyProgress(),
      good,
      good.verifiedAnswer!,
      "practice",
    );
    p = {
      ...p,
      session: {
        ids: [good.id, unknown.id],
        index: 0,
        mode: "practice",
        selections: {
          [good.id]: good.verifiedAnswer!,
          [unknown.id]: unknown.originalAnswer,
        },
        submitted: [good.id],
        finished: false,
        expiresAt: null,
      },
    };
    const done = finishPractice(p);
    expect(done.history).toEqual(p.history);
    expect(done.completedSessions).toHaveLength(1);
    expect(summarizeSession(done.completedSessions[0])).toEqual({
      total: 2,
      answered: 1,
      correct: 1,
      incorrect: 0,
      graded: 1,
      ungraded: 0,
      accuracy: 100,
    });
    expect(finishPractice(done).completedSessions).toHaveLength(1);
    expect(parseBackup(JSON.stringify(done))).toEqual(done);
  });
  it("accepts old version-one backups without session summaries and rejects invented summary IDs", () => {
    const old = { ...emptyProgress() } as Record<string, unknown>;
    delete old.completedSessions;
    expect(parseBackup(JSON.stringify(old)).completedSessions).toEqual([]);
    expect(() =>
      parseBackup(
        JSON.stringify({
          ...emptyProgress(),
          completedSessions: [
            {
              ids: ["fake"],
              mode: "exam",
              selections: {},
              submitted: [],
              finishedAt: new Date().toISOString(),
            },
          ],
        }),
      ),
    ).toThrow();
  });
  it("ties every citation to unchanged retrieved official text", () => {
    for (const q of questions)
      for (const ref of q.references) {
        expect(ref.evidenceFile, ref.url).toBeTruthy();
        expect(existsSync(ref.evidenceFile!), ref.url).toBe(true);
        expect(
          createHash("sha256")
            .update(readFileSync(ref.evidenceFile!))
            .digest("hex"),
          ref.url,
        ).toBe(ref.evidenceSha256);
      }
  });
});
describe("documented corrections", () => {
  it.each([
    ["b1-q74", "b", "d"],
    ["b1-q91", "a", "d"],
    ["b2-q6", "b", "a"],
    ["b2-q12", "c", "a"],
    ["b2-q15", "a", "c"],
    ["b2-q35", "a", "b"],
    ["b2-q46", "b", "d"],
    ["b2-q53", "c", "a"],
    ["b3-q70", "b", "c"],
    ["b3-q76", "b", "c"],
    ["b3-q82", "b", "c"],
  ])(
    "preserves original %s key %s while grading documented %s",
    (id, original, correct) => {
      const q = byId[id];
      expect(q.originalAnswer).toEqual([original]);
      expect(q.verifiedAnswer).toEqual([correct]);
      expect(grade(q, [original])).toBe(false);
      expect(grade(q, [correct])).toBe(true);
    },
  );
});
describe("grading and study state", () => {
  it("grades only researched answers and rejects incomplete/wrong verified selections", () => {
    for (const q of questions) {
      if (q.verification !== "verified") {
        expect(grade(q, q.originalAnswer), q.id).toBeNull();
        continue;
      }
      const key = q.verifiedAnswer!;
      expect(grade(q, key)).toBe(true);
      expect(grade(q, [])).toBe(false);
      if (key.length > 1) expect(grade(q, key.slice(1))).toBe(false);
      const wrong = q.choices.find((c) => !key.includes(c.id));
      if (wrong) expect(grade(q, [wrong.id])).toBe(false);
      expect(grade(q, [...key, key[0]])).toBe(false);
    }
  });
  it("selects one radio answer or toggles multiple choices", () => {
    const single = questions.find((q) => q.type === "single")!,
      multi = questions.find((q) => q.type === "multiple")!;
    expect(toggleSelection(single, ["a"], "b")).toEqual(["b"]);
    expect(toggleSelection(multi, ["a"], "b")).toEqual(["a", "b"]);
    expect(toggleSelection(multi, ["a", "b"], "a")).toEqual(["b"]);
  });
  it("counts latest unique answers while retaining improvement history", () => {
    const q = questions[0];
    let p = recordAttempt(emptyProgress(), q, [], "practice");
    expect(stats(p.history)).toEqual({
      answered: 1,
      correct: 0,
      incorrect: 1,
      ungraded: 0,
      accuracy: 0,
    });
    p = recordAttempt(p, q, q.verifiedAnswer ?? q.originalAnswer, "practice");
    expect(stats(p.history)).toEqual({
      answered: 1,
      correct: 1,
      incorrect: 0,
      ungraded: 0,
      accuracy: 100,
    });
    expect(p.history).toHaveLength(2);
  });
  it("filters banks, topics, incorrect, unanswered, bookmarks and verification", () => {
    const q = questions[0];
    const p = recordAttempt(
      { ...emptyProgress(), bookmarks: [q.id] },
      q,
      [],
      "practice",
    );
    const f = {
      banks: [1, 2, 3],
      topic: "all",
      status: "all",
      verification: "all",
    };
    expect(
      filterQuestions({ ...f, banks: [2] }, p).every((x) => x.bank === 2),
    ).toBe(true);
    expect(
      filterQuestions({ ...f, topic: q.topic }, p).every(
        (x) => x.topic === q.topic,
      ),
    ).toBe(true);
    expect(
      filterQuestions({ ...f, status: "incorrect" }, p).map((x) => x.id),
    ).toEqual([q.id]);
    expect(
      filterQuestions({ ...f, status: "bookmarked" }, p).map((x) => x.id),
    ).toEqual([q.id]);
    expect(
      filterQuestions({ ...f, status: "unanswered" }, p).some(
        (x) => x.id === q.id,
      ),
    ).toBe(false);
    expect(
      filterQuestions({ ...f, verification: "verified" }, p).every(
        (x) => x.verification === "verified",
      ),
    ).toBe(true);
    expect(filterQuestions({ ...f, banks: [] }, p)).toHaveLength(0);
  });
  it("shuffles without mutating or changing answer mappings", () => {
    const sample = questions.slice(0, 20);
    const shuffled = shuffle(sample, () => 0);
    expect(shuffled).not.toEqual(sample);
    expect(new Set(shuffled.map((q) => q.id))).toEqual(
      new Set(sample.map((q) => q.id)),
    );
    for (const q of shuffled) expect(q).toBe(byId[q.id]);
    expect(sample[0]).toBe(questions[0]);
  });
  it("completes an exam once, including unanswered questions as incorrect", () => {
    const ids = questions.slice(0, 3).map((q) => q.id);
    const session: Session = {
      ids,
      index: 1,
      mode: "exam",
      selections: {
        [ids[0]]: questions[0].verifiedAnswer ?? questions[0].originalAnswer,
      },
      submitted: [],
      finished: false,
      expiresAt: null,
    };
    const p = completeExam({ ...emptyProgress(), session });
    expect(stats(p.history)).toEqual({
      answered: 3,
      correct: 1,
      incorrect: 2,
      ungraded: 0,
      accuracy: 33,
    });
    expect(p.session?.finished).toBe(true);
    expect(completeExam(p).history).toHaveLength(3);
  });
  it("round-trips progress and current selections through persistent storage", () => {
    const q = questions[0];
    const p = recordAttempt(
      {
        ...emptyProgress(),
        bookmarks: [q.id],
        session: {
          ids: [q.id],
          index: 0,
          mode: "practice",
          selections: { [q.id]: ["a"] },
          submitted: [],
          finished: false,
          expiresAt: null,
        },
      },
      q,
      ["a"],
      "practice",
    );
    const store = new Map<string, string>();
    const storage = {
      getItem: (key: string) => store.get(key) ?? null,
      setItem: (key: string, value: string) => {
        store.set(key, value);
      },
    };
    saveProgress(storage, p);
    expect(loadProgress(storage).progress).toEqual(p);
    expect(store.has(STORAGE_KEY)).toBe(true);
  });
  it("rejects malformed backups and recomputes externally supplied scores", () => {
    expect(() => parseBackup("{}")).toThrow();
    const p = recordAttempt(emptyProgress(), questions[0], [], "practice");
    p.history[0].correct = true;
    expect(parseBackup(JSON.stringify(p)).history[0].correct).toBe(false);
    expect(() =>
      parseBackup(JSON.stringify({ ...p, bookmarks: ["fake-question"] })),
    ).toThrow();
    expect(() =>
      parseBackup(
        JSON.stringify({
          ...p,
          history: [{ ...p.history[0], selected: ["z"] }],
        }),
      ),
    ).toThrow();
    expect(loadProgress({ getItem: () => "{bad json" }).error).toBeTruthy();
  });
});
