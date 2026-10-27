import raw from "./data/questions.json";
export type Choice = { id: string; text: string; image: string };
export type Reference = {
  title: string;
  url: string;
  section: string;
  support: string;
};
export type Question = {
  id: string;
  bank: number;
  number: number;
  sourceFile: string;
  pages: number[];
  text: string;
  promptImages: string[];
  sourceImages: string[];
  choices: Choice[];
  type: string;
  originalAnswer: string[];
  originalKeyText: string;
  verifiedAnswer: string[] | null;
  verification: string;
  topic: string;
  issues: string[];
  explanations: Record<string, string>;
  references: Reference[];
  duplicateOf: string | null;
  keyConcept?: string;
  examTip?: string;
};
export const questions = raw as Question[];
export const byId = Object.fromEntries(questions.map((q) => [q.id, q]));
export type Attempt = {
  questionId: string;
  selected: string[];
  correct: boolean;
  at: string;
  mode: "practice" | "exam";
};
export type Session = {
  ids: string[];
  index: number;
  mode: "practice" | "exam";
  selections: Record<string, string[]>;
  submitted: string[];
  finished: boolean;
  expiresAt: number | null;
};
export type Progress = {
  version: 1;
  history: Attempt[];
  bookmarks: string[];
  session: Session | null;
  dark: boolean;
};
export const STORAGE_KEY = "lakehouse-study-v1";
export const emptyProgress = (): Progress => ({
  version: 1,
  history: [],
  bookmarks: [],
  session: null,
  dark: false,
});
export function answer(q: Question) {
  return q.verifiedAnswer ?? q.originalAnswer;
}
export function grade(q: Question, selected: string[]) {
  const expected = answer(q);
  return (
    expected.length === selected.length &&
    new Set(selected).size === selected.length &&
    expected.every((x) => selected.includes(x))
  );
}
export function latest(history: Attempt[]) {
  return Object.fromEntries(history.map((a) => [a.questionId, a]));
}
export function stats(history: Attempt[]) {
  const values = Object.values(latest(history));
  const correct = values.filter((a) => a.correct).length;
  return {
    answered: values.length,
    correct,
    incorrect: values.length - correct,
    accuracy: values.length ? Math.round((correct / values.length) * 100) : 0,
  };
}
export type Filters = {
  banks: number[];
  topic: string;
  status: string;
  verification: string;
};
export function filterQuestions(filters: Filters, progress: Progress) {
  const last = latest(progress.history);
  const candidates = questions.filter(
    (q) =>
      filters.banks.includes(q.bank) &&
      (filters.topic === "all" || q.topic === filters.topic) &&
      (filters.verification === "all" ||
        q.verification === filters.verification) &&
      (filters.status === "all" ||
        (filters.status === "unanswered" && !last[q.id]) ||
        (filters.status === "incorrect" && last[q.id]?.correct === false) ||
        (filters.status === "bookmarked" && progress.bookmarks.includes(q.id))),
  );
  // Deduplicate within the selected candidates, retaining a source even if its canonical bank is excluded.
  const seen = new Set<string>();
  return candidates.filter((q) => {
    const id = q.duplicateOf ?? q.id;
    if (seen.has(id)) return false;
    seen.add(id);
    return true;
  });
}
export function shuffle<T>(
  items: T[],
  random: () => number = Math.random,
): T[] {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}
export function toggleSelection(q: Question, current: string[], id: string) {
  return q.type === "multiple"
    ? current.includes(id)
      ? current.filter((x) => x !== id)
      : [...current, id]
    : [id];
}
export function recordAttempt(
  progress: Progress,
  q: Question,
  selected: string[],
  mode: "practice" | "exam",
  at = new Date().toISOString(),
): Progress {
  return {
    ...progress,
    history: [
      ...progress.history,
      {
        questionId: q.id,
        selected: [...selected],
        correct: grade(q, selected),
        mode,
        at,
      },
    ],
  };
}
export function completeExam(progress: Progress): Progress {
  const session = progress.session;
  if (!session || session.mode !== "exam" || session.finished) return progress;
  let result = progress;
  for (const id of session.ids)
    result = recordAttempt(
      result,
      byId[id],
      session.selections[id] ?? [],
      "exam",
    );
  return {
    ...result,
    session: { ...session, finished: true, submitted: [...session.ids] },
  };
}
function hasQuestion(id: unknown): id is string {
  return typeof id === "string" && Object.hasOwn(byId, id);
}
function validSelection(id: string, x: unknown): x is string[] {
  return (
    hasQuestion(id) &&
    Array.isArray(x) &&
    new Set(x).size === x.length &&
    x.every(
      (c) => typeof c === "string" && byId[id]?.choices.some((o) => o.id === c),
    ) &&
    (byId[id]?.type === "multiple" || x.length <= 1)
  );
}
export function parseBackup(text: string): Progress {
  if (text.length > 25_000_000) throw new Error("Backup exceeds 25 MB.");
  const x = JSON.parse(text) as Progress;
  if (
    !x ||
    x.version !== 1 ||
    !Array.isArray(x.history) ||
    !Array.isArray(x.bookmarks) ||
    typeof x.dark !== "boolean"
  )
    throw new Error("Invalid backup format or version.");
  if (
    x.history.length > 100000 ||
    x.history.some(
      (a) =>
        !a ||
        !hasQuestion(a.questionId) ||
        !validSelection(a.questionId, a.selected) ||
        !["practice", "exam"].includes(a.mode) ||
        !Number.isFinite(Date.parse(a.at)),
    )
  )
    throw new Error("Backup contains invalid attempts.");
  if (
    x.bookmarks.some((id) => !hasQuestion(id)) ||
    new Set(x.bookmarks).size !== x.bookmarks.length
  )
    throw new Error("Backup contains invalid bookmarks.");
  const s = x.session;
  if (s !== null) {
    if (
      !s ||
      !Array.isArray(s.ids) ||
      !s.ids.length ||
      s.ids.some((id) => !hasQuestion(id)) ||
      new Set(s.ids).size !== s.ids.length ||
      !Number.isInteger(s.index) ||
      s.index < 0 ||
      s.index >= s.ids.length ||
      !["practice", "exam"].includes(s.mode) ||
      typeof s.finished !== "boolean" ||
      !(
        s.expiresAt === null ||
        (typeof s.expiresAt === "number" &&
          Number.isFinite(s.expiresAt) &&
          s.expiresAt > 0)
      ) ||
      !s.selections ||
      typeof s.selections !== "object" ||
      Array.isArray(s.selections) ||
      Object.entries(s.selections).some(
        ([id, v]) => !s.ids.includes(id) || !validSelection(id, v),
      ) ||
      !Array.isArray(s.submitted) ||
      s.submitted.some(
        (id) =>
          !s.ids.includes(id) ||
          (s.mode === "practice" && !s.selections[id]?.length),
      ) ||
      new Set(s.submitted).size !== s.submitted.length
    )
      throw new Error("Backup contains an invalid session.");
  }
  // Never trust externally supplied scores.
  return {
    version: 1,
    dark: x.dark,
    bookmarks: [...x.bookmarks],
    history: x.history.map((a) => ({
      ...a,
      correct: grade(byId[a.questionId], a.selected),
    })),
    session: s,
  };
}
export function loadProgress(storage: Pick<Storage, "getItem">): {
  progress: Progress;
  error: string | null;
} {
  try {
    const text = storage.getItem(STORAGE_KEY);
    return {
      progress: text ? parseBackup(text) : emptyProgress(),
      error: null,
    };
  } catch {
    return {
      progress: emptyProgress(),
      error:
        "Saved progress could not be loaded. The original browser data has been left untouched; import a backup or explicitly replace it by saving new progress.",
    };
  }
}
export function saveProgress(
  storage: Pick<Storage, "setItem">,
  progress: Progress,
) {
  storage.setItem(STORAGE_KEY, JSON.stringify(progress));
}
