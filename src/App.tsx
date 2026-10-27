import { useEffect, useRef, useState } from "react";
import {
  answer,
  byId,
  completeExam,
  emptyProgress,
  filterQuestions,
  grade,
  evaluate,
  finishPractice,
  summarizeSession,
  latest,
  loadProgress,
  parseBackup,
  questions,
  recordAttempt,
  saveProgress,
  shuffle,
  stats,
  toggleSelection,
  type Filters,
  type Progress,
  type Question,
  type Session,
} from "./model";
import report from "./data/import-report.json";
type View =
  | "dashboard"
  | "practice"
  | "exam"
  | "banks"
  | "incorrect"
  | "bookmarked"
  | "performance";
const topics = [...new Set(questions.map((q) => q.topic))].sort();
const similarPairs =
  (
    report as unknown as {
      similarQuestionPairs?: { a: string; b: string; similarity: number }[];
    }
  ).similarQuestionPairs ?? [];
const defaultFilters: Filters = {
  banks: [1, 2, 3],
  topic: "all",
  status: "all",
  verification: "all",
};
function Explanation({ q, selected }: { q: Question; selected: string[] }) {
  const verified = q.verification === "verified";
  return (
    <section className="explanation" aria-label="Answer review">
      <div className="eyebrow">Answer review</div>
      <h3>
        {verified
          ? grade(q, selected)
            ? "Correct"
            : "Incorrect"
          : "Not graded — answer unresolved"}
      </h3>
      <p>
        Your answer:{" "}
        <strong>
          {selected.length ? selected.join(", ").toUpperCase() : "Unanswered"}
        </strong>{" "}
        · {verified ? "Verified answer" : "Unverified source answer"}:{" "}
        <strong>{answer(q).join(", ").toUpperCase()}</strong>
      </p>
      {!verified && (
        <div className="notice">
          This question is not scored because no single documentation-supported
          answer has been established. The original key is shown for source
          comparison only. Read the research notes below before relying on any
          option.
        </div>
      )}
      <div className="research-conclusion">
        <h4>
          {verified
            ? "Why the documented answer fits"
            : "Why this question remains unresolved"}
        </h4>
        <p>{q.analysis ?? q.keyConcept}</p>
        {q.reviewedAt && (
          <small>
            Research reviewed {q.reviewedAt} ·{" "}
            {q.reviewStatus?.replaceAll("-", " ")}
          </small>
        )}
      </div>
      <div className="option-reviews">
        {q.choices.map((c) => (
          <div key={c.id}>
            <strong>
              {c.id.toUpperCase()} ·{" "}
              {answer(q).includes(c.id)
                ? verified
                  ? "Correct"
                  : "Keyed answer"
                : verified
                  ? "Incorrect"
                  : "Not keyed"}
            </strong>
            <p>
              {q.explanations[c.id] ??
                "Unverified — an option-specific explanation is not yet available. Consult the original choice and source PDF; do not treat the supplied key as authoritative."}
            </p>
          </div>
        ))}
      </div>
      {q.keyConcept && (
        <div className="learning-note">
          <h4>Key concept to remember</h4>
          <p>{q.keyConcept}</p>
          <h4>Exam tip</h4>
          <p>{q.examTip}</p>
        </div>
      )}
      {q.references.length > 0 && (
        <div>
          <h4>Official documentation</h4>
          {q.references.map((r) => (
            <p key={r.url}>
              <a href={r.url} target="_blank" rel="noreferrer">
                {r.title} ↗
              </a>
              <br />
              {r.section} — {r.support}
            </p>
          ))}
        </div>
      )}
      {!verified && (
        <p className="muted">
          Verification sources:{" "}
          <a
            href="https://docs.databricks.com/"
            target="_blank"
            rel="noreferrer"
          >
            Official Databricks documentation ↗
          </a>{" "}
          ·{" "}
          <a
            href="https://www.databricks.com/learn/certification"
            target="_blank"
            rel="noreferrer"
          >
            Certification objectives ↗
          </a>
          . These are research entry points, not evidence for this answer.
        </p>
      )}
      <details>
        <summary>Original answer-key transcription</summary>
        <pre>{q.originalKeyText}</pre>
      </details>
    </section>
  );
}
export default function App() {
  const [initial] = useState(() => {
    try {
      return loadProgress(window.localStorage);
    } catch {
      return {
        progress: emptyProgress(),
        error:
          "Browser storage is unavailable. You can study in this tab and export a backup, but refreshing cannot preserve progress until storage is enabled.",
      };
    }
  });
  const [progress, setProgress] = useState<Progress>(initial.progress);
  const [message, setMessage] = useState(initial.error ?? "");
  const [view, setView] = useState<View>(
    initial.progress.session
      ? initial.progress.session.mode === "exam"
        ? "exam"
        : "practice"
      : "dashboard",
  );
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [count, setCount] = useState("20");
  const [random, setRandom] = useState(true);
  const [minutes, setMinutes] = useState("0");
  const [now, setNow] = useState(Date.now());
  const [confirmFinish, setConfirmFinish] = useState(false);
  const [replaceSession, setReplaceSession] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const [confirmImport, setConfirmImport] = useState<Progress | null>(null);
  const [storageBlocked, setStorageBlocked] = useState(Boolean(initial.error));
  const fileRef = useRef<HTMLInputElement>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    if (storageBlocked) return;
    try {
      saveProgress(window.localStorage, progress);
    } catch {
      setMessage(
        "Browser storage is unavailable or full. Keep this tab open and export a backup to preserve your work.",
      );
    }
  }, [progress, storageBlocked]);
  useEffect(() => {
    document.documentElement.dataset.theme = progress.dark ? "dark" : "light";
  }, [progress.dark]);
  const session = progress.session;
  const timerActive =
    session?.mode === "exam" && !session.finished && session.expiresAt !== null;
  useEffect(() => {
    if (!timerActive) return;
    const tick = () => {
      const time = Date.now();
      setNow(time);
      setProgress((p) =>
        p.session?.expiresAt && time >= p.session.expiresAt
          ? completeExam(p)
          : p,
      );
    };
    tick();
    const handle = window.setInterval(tick, 1000);
    return () => clearInterval(handle);
  }, [timerActive]);
  useEffect(() => {
    setConfirmFinish(false);
    headingRef.current?.focus();
  }, [session?.index]);
  const total = stats(progress.history);
  const last = latest(progress.history);
  const candidates = filterQuestions(filters, progress);
  const question = session ? byId[session.ids[session.index]] : null;
  const selection =
    question && session ? (session.selections[question.id] ?? []) : [];
  const submitted = Boolean(
    question && session?.submitted.includes(question.id),
  );
  const reveal = Boolean(
    session && (session.mode === "practice" ? submitted : session.finished),
  );
  const isQuiz = ["practice", "exam", "incorrect", "bookmarked"].includes(view);
  function navigate(v: View) {
    setView(v);
    setReplaceSession(false);
    if (v === "incorrect" || v === "bookmarked")
      setFilters({ ...defaultFilters, status: v });
    else if (v === "practice" || v === "exam") setFilters(defaultFilters);
  }
  function start() {
    if (!candidates.length) return;
    const ids = (random ? shuffle(candidates) : candidates)
      .slice(0, count === "all" ? candidates.length : Number(count))
      .map((q) => q.id);
    const mode = view === "exam" ? "exam" : "practice";
    const s: Session = {
      ids,
      index: 0,
      mode,
      selections: {},
      submitted: [],
      finished: false,
      expiresAt:
        mode === "exam" && Number(minutes) > 0
          ? Date.now() + Number(minutes) * 60000
          : null,
    };
    setProgress((p) => ({ ...p, session: s }));
    setReplaceSession(false);
    setConfirmFinish(false);
  }
  function submit() {
    if (
      !question ||
      !session ||
      !selection.length ||
      submitted ||
      session.finished
    )
      return;
    setProgress((p) => {
      const updated = recordAttempt(p, question, selection, "practice");
      return {
        ...updated,
        session: { ...session, submitted: [...session.submitted, question.id] },
      };
    });
  }
  function exportBackup() {
    const blob = new Blob([JSON.stringify(progress, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lakehouse-study-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  async function importBackup(file: File | undefined) {
    if (!file) return;
    try {
      if (file.size > 25_000_000) throw new Error("Backup exceeds 25 MB.");
      setConfirmImport(parseBackup(await file.text()));
    } catch (e) {
      setMessage(`Import failed: ${(e as Error).message}`);
    }
    if (fileRef.current) fileRef.current.value = "";
  }
  function topicRows() {
    return topics.map((t) => {
      const qs = questions.filter((q) => q.topic === t);
      const attempted = qs.filter((q) => last[q.id]);
      const correct = attempted.filter(
        (q) => last[q.id].correct === true,
      ).length;
      const graded = attempted.filter(
        (q) => last[q.id].correct !== null,
      ).length;
      return {
        topic: t,
        total: qs.length,
        answered: attempted.length,
        correct,
        graded,
        accuracy: graded ? Math.round((correct / graded) * 100) : 0,
      };
    });
  }
  const quizGraded = session
    ? session.ids.filter((id) => byId[id].verification === "verified").length
    : 0;
  const quizCorrect = session
    ? session.ids.filter(
        (id) =>
          session.selections[id]?.length &&
          evaluate(byId[id], session.selections[id]) === true,
      ).length
    : 0;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            navigate("dashboard");
          }}
        >
          <span className="brand-icon">▱</span>
          <span>
            Lakehouse<span className="brand-sub">STUDY ROOM</span>
          </span>
        </a>
        <div className="sidebar-label">YOUR WORKSPACE</div>
        <nav aria-label="Main navigation">
          {(
            [
              ["dashboard", "◫", "Dashboard"],
              ["practice", "▷", "Practice quiz"],
              ["exam", "◷", "Mock exam"],
              ["banks", "▤", "Question banks"],
              ["incorrect", "↺", "Wrong answers"],
              ["bookmarked", "☆", "Bookmarks"],
              ["performance", "▥", "Performance"],
            ] as [View, string, string][]
          ).map(([key, icon, label]) => (
            <button
              key={key}
              aria-current={view === key ? "page" : undefined}
              className={view === key ? "nav-item active" : "nav-item"}
              onClick={() => navigate(key)}
            >
              <span aria-hidden="true">{icon}</span>
              {label}
              {key === "incorrect" && <small>{total.incorrect}</small>}
              {key === "bookmarked" && (
                <small>{progress.bookmarks.length}</small>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="local-dot" /> Saved in this browser
          <p>Personal study, at your pace.</p>
          <button
            className="text-button"
            onClick={() => setProgress((p) => ({ ...p, dark: !p.dark }))}
          >
            {progress.dark ? "☀ Light appearance" : "☾ Dark appearance"}
          </button>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <span>
            Databricks <span className="divider">/</span> Data Engineer
            Associate
          </span>
          <span className="pill">PERSONAL WORKSPACE</span>
          <button
            className="theme-toggle"
            aria-label="Toggle color theme"
            aria-pressed={progress.dark}
            onClick={() => setProgress((p) => ({ ...p, dark: !p.dark }))}
          >
            {progress.dark ? "☀" : "☾"}
          </button>
        </header>
        <main>
          <div className="page-heading">
            <div className="eyebrow">DATABRICKS CERTIFICATION PREP</div>
            <h1>
              {
                {
                  dashboard: "Make every session count.",
                  practice: "Understand. Practice. Improve.",
                  exam: "Your exam, your pace.",
                  banks: "Three banks. One study space.",
                  incorrect: "Turn mistakes into progress.",
                  bookmarked: "Keep the important questions close.",
                  performance: "See where you’re growing.",
                }[view]
              }
            </h1>
            <p className="muted">
              {isQuiz
                ? "Real questions from your PDFs, with your progress always close at hand."
                : "A clear view of your preparation for the Data Engineer Associate exam."}
            </p>
          </div>
          {message && (
            <div className="notice" role="status">
              {message}
              <button className="text-button" onClick={() => setMessage("")}>
                Dismiss
              </button>
              {storageBlocked && (
                <button
                  onClick={() => {
                    setStorageBlocked(false);
                    setMessage(
                      "New progress will now replace the unreadable browser data.",
                    );
                  }}
                >
                  Save new progress
                </button>
              )}
            </div>
          )}
          <div className="verification-banner">
            <span className="status-dot" />
            <div>
              <strong>Source keys ≠ verified answers</strong>
              <span>
                {report.total} imported · {report.verified} independently
                verified. Unverified answers are labeled throughout.
              </span>
            </div>
            <button className="text-button" onClick={() => navigate("banks")}>
              View import details ↗
            </button>
          </div>
          {confirmImport && (
            <section
              className="card"
              role="alertdialog"
              aria-label="Replace study progress"
            >
              <h2>Replace your saved progress?</h2>
              <p>
                This backup contains {confirmImport.history.length} attempts and{" "}
                {confirmImport.bookmarks.length} bookmarks. Export your current
                progress first if you want to keep it.
              </p>
              <button onClick={exportBackup}>Export current backup</button>{" "}
              <button
                className="primary"
                onClick={() => {
                  setProgress(confirmImport);
                  setStorageBlocked(false);
                  setConfirmImport(null);
                  setMessage(
                    "Backup imported. Scores were recalculated from the question data.",
                  );
                }}
              >
                Replace with backup
              </button>{" "}
              <button onClick={() => setConfirmImport(null)}>Cancel</button>
            </section>
          )}
          {(view === "dashboard" || view === "performance") && (
            <>
              <div className="stats-grid">
                {[
                  [
                    "Questions completed",
                    total.answered,
                    `${questions.length - total.answered} left to explore`,
                  ],
                  [
                    "Correct answers",
                    total.correct,
                    "Documentation-verified grading only",
                  ],
                  [
                    "Accuracy",
                    total.correct + total.incorrect
                      ? `${total.accuracy}%`
                      : "—",
                    "Excludes ungraded questions",
                  ],
                  [
                    "Bookmarked",
                    progress.bookmarks.length,
                    "Your personal review list",
                  ],
                ].map(([label, value, sub]) => (
                  <section className="stat card" key={label}>
                    <span>{label}</span>
                    <strong>{value}</strong>
                    <small>{sub}</small>
                  </section>
                ))}
              </div>
              {total.ungraded > 0 && (
                <div className="notice">
                  {total.ungraded} answered questions remain ungraded because
                  their answers are unresolved. Accuracy and wrong-answer counts
                  use only documentation-verified questions.
                </div>
              )}
              <div className="dashboard-grid">
                <section className="card study-card">
                  <div className="eyebrow">BUILD YOUR MOMENTUM</div>
                  <h2>
                    A little practice.
                    <br />A deeper understanding.
                  </h2>
                  <p>
                    Choose a bank, focus on a topic, or revisit the questions
                    that challenged you.
                  </p>
                  <button
                    className="primary"
                    onClick={() => navigate("practice")}
                  >
                    Start practicing <span>→</span>
                  </button>
                  <div className="study-art" aria-hidden="true">
                    <span>▱</span>
                    <span>▱</span>
                    <span>▱</span>
                  </div>
                </section>
                <section className="card progress-card">
                  <h2>Your study progress</h2>
                  <div
                    className="progress-ring"
                    style={{
                      background: `conic-gradient(var(--accent) ${(total.answered / questions.length) * 360}deg, var(--line) 0)`,
                    }}
                  >
                    <div>
                      <strong>
                        {Math.round((total.answered / questions.length) * 100)}%
                      </strong>
                      <span>completed</span>
                    </div>
                  </div>
                  <p>
                    {total.answered} of {questions.length} source questions
                  </p>
                  <div className="legend">
                    <span>● {total.correct} correct</span>
                    <span>○ {total.incorrect} incorrect</span>
                  </div>
                </section>
              </div>
              <section className="card">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">FIND YOUR FOCUS</div>
                    <h2>Progress by topic</h2>
                  </div>
                  <span className="muted">
                    Latest answer for each source question
                  </span>
                </div>
                <div className="topic-list">
                  {topicRows()
                    .sort(
                      (a, b) =>
                        b.answered - a.answered || a.accuracy - b.accuracy,
                    )
                    .map((t) => (
                      <button
                        className="topic-row"
                        key={t.topic}
                        onClick={() => {
                          setFilters({ ...defaultFilters, topic: t.topic });
                          setView("practice");
                        }}
                      >
                        <div>
                          <strong>{t.topic}</strong>
                          <span>
                            {t.answered} / {t.total} answered ·{" "}
                            {t.graded
                              ? t.accuracy + "% verified accuracy"
                              : t.answered
                                ? "Not graded yet"
                                : "Not started"}
                          </span>
                        </div>
                        <progress
                          aria-label={`${t.topic} completion`}
                          max={t.total}
                          value={t.answered}
                        />
                        <span>→</span>
                      </button>
                    ))}
                </div>
              </section>
              <section className="card">
                <h2>Focus next · weakest topics</h2>
                {topicRows().some((t) => t.graded) ? (
                  topicRows()
                    .filter((t) => t.graded)
                    .sort((a, b) => a.accuracy - b.accuracy)
                    .slice(0, 3)
                    .map((t) => (
                      <button
                        className="topic-row"
                        key={t.topic}
                        onClick={() => {
                          setFilters({ ...defaultFilters, topic: t.topic });
                          setView("practice");
                        }}
                      >
                        <div>
                          <strong>{t.topic}</strong>
                          <span>
                            {t.accuracy}% accuracy across {t.graded} graded
                            questions
                          </span>
                        </div>
                        <span>Practice →</span>
                      </button>
                    ))
                ) : (
                  <p className="muted">
                    Answer a few questions to see where to focus your next
                    session.
                  </p>
                )}
              </section>
              <section className="card">
                <h2>Previous quiz results</h2>
                {progress.completedSessions.length ? (
                  <ul className="recent-list">
                    {progress.completedSessions
                      .slice(-10)
                      .reverse()
                      .map((s, i) => {
                        const r = summarizeSession(s);
                        return (
                          <li key={i}>
                            <span>
                              {s.mode === "exam" ? "Exam" : "Practice"}
                              <small>
                                {r.answered} / {r.total} answered · {r.ungraded}{" "}
                                ungraded
                              </small>
                            </span>
                            <strong>
                              {r.correct} / {r.graded} verified ·{" "}
                              {r.accuracy === null
                                ? "Not scored"
                                : r.accuracy + "%"}
                            </strong>
                            <time>
                              {new Date(s.finishedAt).toLocaleString()}
                            </time>
                          </li>
                        );
                      })}
                  </ul>
                ) : (
                  <p className="muted">
                    Finish an exam or select Finish practice to save a session
                    result. Existing individual attempts remain in your history.
                  </p>
                )}
              </section>
              <section className="card">
                <h2>Recent attempts</h2>
                {progress.history.length === 0 ? (
                  <p className="muted">
                    Your first answer is the start of your progress. Try a
                    practice session.
                  </p>
                ) : (
                  <ul className="recent-list">
                    {progress.history
                      .slice(-8)
                      .reverse()
                      .map((a, i) => (
                        <li key={i}>
                          <span
                            className={
                              a.correct === null
                                ? "result ungraded"
                                : a.correct
                                  ? "result correct"
                                  : "result incorrect"
                            }
                          >
                            {a.correct === null ? "—" : a.correct ? "✓" : "×"}
                          </span>
                          <span>
                            Bank {byId[a.questionId].bank} · Question{" "}
                            {byId[a.questionId].number}
                            <small>
                              {byId[a.questionId].topic} · {a.mode}
                              {a.correct === null ? " · Not graded" : ""}
                            </small>
                          </span>
                          <time>{new Date(a.at).toLocaleString()}</time>
                        </li>
                      ))}
                  </ul>
                )}
              </section>
            </>
          )}
          {view === "banks" && (
            <>
              <section className="card">
                <h2>Import and research audit</h2>
                <p>
                  {report.researched} / {report.total} researched ·{" "}
                  {report.completedExplanations} with saved choice explanations
                  · {report.correctedKeys} corrected keys ·{" "}
                  {report.reviewedUnresolved} unresolved after review.
                </p>
                <p>
                  All numbered questions and answer keys were imported. PDF
                  images preserve original wording, code, tables, and choices.
                  Text transcriptions support search and accessibility; use the
                  images and original PDF as the authoritative presentation.
                </p>
                <div className="bank-grid">
                  {report.banks.map((b) => (
                    <article key={b.bank}>
                      <span className="eyebrow">QUESTION BANK {b.bank}</span>
                      <h3>Associate V3.{b.bank}</h3>
                      <strong className="bank-number">{b.imported}</strong>
                      <p>{b.answerKeys} answer keys mapped</p>
                      <a
                        href={`/sources/bank-${b.bank}.pdf`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open original PDF ↗
                      </a>
                      <br />
                      <a
                        href={`/sources/bank-${b.bank}.txt`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Extracted source text ↗
                      </a>
                    </article>
                  ))}
                </div>
                <p>
                  {report.total} source entries · {report.unique} unique
                  questions · {report.total - report.unique} exact duplicates.
                  Default quizzes retain one copy within your selected filters;
                  every source entry remains in the audit below.
                </p>
                <div className="notice">
                  Documentation verification remains incomplete.{" "}
                  {report.verified} answers are verified; {report.unverified}{" "}
                  remain unverified. Topic labels are study aids and do not
                  replace the current official exam guide. Image-only choices
                  and ambiguous source wording are flagged; original keys may be
                  wrong or outdated.
                </div>
              </section>
              <section className="card">
                <h2>Question inventory</h2>
                {similarPairs.length > 0 && (
                  <details>
                    <summary>
                      {similarPairs.length} similar prompt pairs · retained
                      separately because choices or wording differ
                    </summary>
                    {similarPairs.map((pair) => (
                      <p key={pair.a + pair.b}>
                        {pair.a} ↔ {pair.b} ·{" "}
                        {Math.round(pair.similarity * 100)}% text similarity.
                        Compare the originals before treating them as
                        duplicates.
                      </p>
                    ))}
                  </details>
                )}
                <div className="inventory">
                  {questions.map((q) => (
                    <details key={q.id}>
                      <summary>
                        Bank {q.bank} · Q{q.number} · {q.topic}{" "}
                        {q.duplicateOf ? "· Duplicate" : ""}{" "}
                        {q.issues.length ? "· Review flag" : ""}
                      </summary>
                      <p>{q.text}</p>
                      <p>
                        {q.verification === "verified"
                          ? "Verified"
                          : "Unverified"}{" "}
                        ·{" "}
                        {q.type === "multiple"
                          ? "Multiple answers"
                          : "Single answer"}{" "}
                        · Pages {q.pages.join(", ")}
                      </p>
                      {q.issues.map((issue) => (
                        <p className="notice" key={issue}>
                          {issue}
                        </p>
                      ))}
                      {q.duplicateOf && (
                        <p>
                          Exact duplicate of {q.duplicateOf}; source reference
                          retained.
                        </p>
                      )}
                      <a
                        href={`/sources/bank-${q.bank}.pdf#page=${q.pages[0]}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Read source page ↗
                      </a>
                    </details>
                  ))}
                </div>
              </section>
            </>
          )}
          {isQuiz && (
            <>
              <section className="card setup-card">
                <div className="section-heading">
                  <div>
                    <div className="eyebrow">YOUR NEXT SESSION</div>
                    <h2>
                      {view === "exam"
                        ? "Configure a mock exam"
                        : "Choose your practice"}
                    </h2>
                  </div>
                  <span className="pill">{candidates.length} available</span>
                </div>
                <div className="filters">
                  <fieldset>
                    <legend>Question banks</legend>
                    {[1, 2, 3].map((b) => (
                      <label className="check" key={b}>
                        <input
                          type="checkbox"
                          checked={filters.banks.includes(b)}
                          onChange={() =>
                            setFilters((f) => ({
                              ...f,
                              banks: f.banks.includes(b)
                                ? f.banks.filter((x) => x !== b)
                                : [...f.banks, b],
                            }))
                          }
                        />{" "}
                        Bank {b}
                      </label>
                    ))}
                  </fieldset>
                  <label>
                    Topic
                    <select
                      value={filters.topic}
                      onChange={(e) =>
                        setFilters((f) => ({ ...f, topic: e.target.value }))
                      }
                    >
                      <option value="all">All topics</option>
                      {topics.map((t) => (
                        <option key={t}>{t}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Review filter
                    <select
                      value={filters.status}
                      onChange={(e) =>
                        setFilters((f) => ({ ...f, status: e.target.value }))
                      }
                    >
                      <option value="all">All questions</option>
                      <option value="unanswered">Unanswered</option>
                      <option value="correct">Correctly answered</option>
                      <option value="incorrect">Incorrect answers</option>
                      <option value="bookmarked">Bookmarked</option>
                    </select>
                  </label>
                  <label>
                    Verification
                    <select
                      value={filters.verification}
                      onChange={(e) =>
                        setFilters((f) => ({
                          ...f,
                          verification: e.target.value,
                        }))
                      }
                    >
                      <option value="all">All statuses</option>
                      <option value="verified">Verified only</option>
                      <option value="unverified">Unverified only</option>
                    </select>
                  </label>
                  <label>
                    Questions
                    <select
                      value={count}
                      onChange={(e) => setCount(e.target.value)}
                    >
                      {["10", "20", "40", "all"].map((n) => (
                        <option value={n} key={n}>
                          {n === "all" ? "All available" : n}
                        </option>
                      ))}
                    </select>
                  </label>
                  {view === "exam" && (
                    <label>
                      Time limit
                      <select
                        value={minutes}
                        onChange={(e) => setMinutes(e.target.value)}
                      >
                        <option value="0">Untimed</option>
                        {[15, 30, 45, 60, 90].map((n) => (
                          <option value={n} key={n}>
                            {n} minutes
                          </option>
                        ))}
                      </select>
                    </label>
                  )}
                  <label className="check">
                    <input
                      type="checkbox"
                      checked={random}
                      onChange={(e) => setRandom(e.target.checked)}
                    />{" "}
                    Randomize order
                  </label>
                </div>
                <div className="session-actions">
                  <button
                    className="primary"
                    disabled={!candidates.length}
                    onClick={() =>
                      session && !session.finished
                        ? setReplaceSession(true)
                        : start()
                    }
                  >
                    {view === "exam" ? "Start exam" : "Start practice"} →
                  </button>
                  <span className="muted">
                    {!candidates.length
                      ? "No questions match these filters."
                      : `Up to ${count === "all" ? candidates.length : Math.min(Number(count), candidates.length)} questions · ${view === "exam" ? "Answers hidden until you finish" : "Immediate feedback after submission"}`}
                  </span>
                </div>
                {replaceSession && (
                  <div
                    className="notice"
                    role="alertdialog"
                    aria-label="Replace session"
                  >
                    Replace your current session? Submitted practice answers
                    stay in your history; an unfinished exam will be discarded.{" "}
                    <button onClick={start}>Replace session</button>{" "}
                    <button onClick={() => setReplaceSession(false)}>
                      Keep current session
                    </button>
                  </div>
                )}
              </section>
              {session && question && (
                <section className="card question-card">
                  <div className="section-heading">
                    <div>
                      <div className="eyebrow">
                        {session.mode === "exam"
                          ? "MOCK EXAM"
                          : "PRACTICE SESSION"}
                        {session.finished ? " · COMPLETED" : ""}
                      </div>
                      <h2 ref={headingRef} tabIndex={-1}>
                        Question {session.index + 1}{" "}
                        <span className="muted">of {session.ids.length}</span>
                      </h2>
                    </div>
                    <button
                      aria-label={
                        progress.bookmarks.includes(question.id)
                          ? "Remove bookmark"
                          : "Bookmark question"
                      }
                      aria-pressed={progress.bookmarks.includes(question.id)}
                      onClick={() =>
                        setProgress((p) => ({
                          ...p,
                          bookmarks: p.bookmarks.includes(question.id)
                            ? p.bookmarks.filter((id) => id !== question.id)
                            : [...p.bookmarks, question.id],
                        }))
                      }
                    >
                      {progress.bookmarks.includes(question.id)
                        ? "★ Bookmarked"
                        : "☆ Bookmark"}
                    </button>
                  </div>
                  <progress
                    className="full-progress"
                    aria-label="Session position"
                    max={session.ids.length}
                    value={session.index + 1}
                  />
                  <div className="question-meta">
                    <span className="topic-tag">{question.topic}</span>
                    <span>
                      Bank {question.bank} · Original Q{question.number}
                    </span>
                    <span
                      className={
                        question.verification === "verified"
                          ? "topic-tag"
                          : "unverified"
                      }
                    >
                      {question.verification === "verified"
                        ? "Verified"
                        : "Unverified"}
                    </span>
                    {timerActive && (
                      <strong role="timer" aria-label="Time remaining">
                        {Math.max(
                          0,
                          Math.ceil(((session.expiresAt ?? now) - now) / 60000),
                        )}{" "}
                        min remaining
                      </strong>
                    )}
                  </div>
                  {session.mode === "exam" && session.finished && (
                    <div className="exam-results" role="status">
                      <h3>
                        Exam complete · {quizCorrect} / {quizGraded} correct (
                        {quizGraded
                          ? Math.round((quizCorrect / quizGraded) * 100) + "%"
                          : "not scored"}
                        )
                      </h3>
                      <p>
                        {
                          session.ids.filter(
                            (id) => !session.selections[id]?.length,
                          ).length
                        }{" "}
                        unanswered · {session.ids.length - quizGraded} ungraded
                        questions excluded from the score. Only
                        documentation-verified answers are scored.
                      </p>
                    </div>
                  )}
                  <div className="question-prompt">
                    {question.promptImages.map((src, i) => (
                      <img
                        src={src}
                        alt={`Original question ${question.number}, part ${i + 1}. ${question.text}`}
                        key={src}
                      />
                    ))}
                  </div>
                  {question.promptFigures?.length ? (
                    <details className="source-scan">
                      <summary>
                        Original-resolution diagram or code (
                        {question.promptFigures.length})
                      </summary>
                      {question.promptFigures.map((src) => (
                        <a
                          key={src}
                          href={src}
                          target="_blank"
                          rel="noreferrer"
                        >
                          <img
                            src={src}
                            alt="Original-resolution figure preserved from the source PDF"
                          />
                        </a>
                      ))}
                    </details>
                  ) : null}
                  <details className="source-scan">
                    <summary>
                      Full original question scan · open images to enlarge
                    </summary>
                    {question.sourceImages.map((src, i) => (
                      <a key={src} href={src} target="_blank" rel="noreferrer">
                        <img
                          src={src}
                          alt={`Complete source scan, part ${i + 1}`}
                        />
                      </a>
                    ))}
                  </details>
                  <details className="transcript">
                    <summary>Question text transcription</summary>
                    <pre>{question.text}</pre>
                  </details>
                  <p className="selection-hint">
                    {question.type === "multiple"
                      ? "Select all answers that apply."
                      : "Select one answer."}
                  </p>
                  {reveal && question.issues.length > 0 && (
                    <details className="source-note">
                      <summary>
                        Source review notes ({question.issues.length})
                      </summary>
                      {question.issues.map((issue) => (
                        <p key={issue}>{issue}</p>
                      ))}
                    </details>
                  )}
                  <fieldset
                    className="answer-choices"
                    disabled={reveal || session.finished}
                  >
                    <legend className="sr-only">Answer choices</legend>
                    {question.choices.map((c) => {
                      const chosen = selection.includes(c.id);
                      const correct =
                        reveal &&
                        question.verification === "verified" &&
                        answer(question).includes(c.id);
                      const wrong =
                        reveal &&
                        question.verification === "verified" &&
                        chosen &&
                        !correct;
                      return (
                        <label
                          key={c.id}
                          className={`choice ${chosen ? "selected" : ""} ${correct ? "correct-choice" : ""} ${wrong ? "wrong-choice" : ""}`}
                        >
                          <input
                            aria-label={`Option ${c.id.toUpperCase()}`}
                            type={
                              question.type === "multiple"
                                ? "checkbox"
                                : "radio"
                            }
                            name={`answer-${question.id}`}
                            checked={chosen}
                            onChange={() =>
                              setProgress((p) => ({
                                ...p,
                                session: {
                                  ...session,
                                  selections: {
                                    ...session.selections,
                                    [question.id]: toggleSelection(
                                      question,
                                      selection,
                                      c.id,
                                    ),
                                  },
                                },
                              }))
                            }
                          />
                          <span className="choice-letter">
                            {c.id.toUpperCase()}
                          </span>
                          <span className="choice-content">
                            <img
                              src={c.image}
                              alt={
                                c.text ||
                                `Image-based option ${c.id.toUpperCase()}; see source PDF for original code.`
                              }
                            />
                            {!c.text && (
                              <small>
                                Image-based choice · Original code preserved
                              </small>
                            )}
                          </span>
                          {reveal && (
                            <span className="choice-status">
                              {correct ? "Keyed" : chosen ? "Your answer" : ""}
                            </span>
                          )}
                        </label>
                      );
                    })}
                  </fieldset>
                  <div className="question-actions">
                    {session.mode === "practice" && !session.finished && (
                      <button onClick={() => setProgress(finishPractice)}>
                        Finish practice
                      </button>
                    )}
                    {session.mode === "practice" && (
                      <button
                        className="primary"
                        disabled={
                          !selection.length || submitted || session.finished
                        }
                        onClick={submit}
                      >
                        {submitted ? "Answer submitted" : "Submit answer"}
                      </button>
                    )}
                    {session.mode === "exam" && !session.finished && (
                      <>
                        <span>
                          {
                            Object.values(session.selections).filter(
                              (s) => s.length,
                            ).length
                          }{" "}
                          / {session.ids.length} answered
                        </span>
                        <button
                          className="primary"
                          onClick={() => setConfirmFinish(true)}
                        >
                          Finish exam
                        </button>
                      </>
                    )}
                    <a
                      href={`/sources/bank-${question.bank}.pdf#page=${question.pages[0]}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Original PDF · page {question.pages[0]} ↗
                    </a>
                  </div>
                  {confirmFinish && !session.finished && (
                    <div
                      className="notice"
                      role="alertdialog"
                      aria-label="Finish exam confirmation"
                    >
                      Submit this exam? Unanswered verified questions count as
                      incorrect. Unverified questions remain ungraded.{" "}
                      <button
                        className="primary"
                        onClick={() => {
                          setProgress(completeExam);
                          setConfirmFinish(false);
                        }}
                      >
                        Confirm final submission
                      </button>{" "}
                      <button onClick={() => setConfirmFinish(false)}>
                        Keep working
                      </button>
                    </div>
                  )}
                  {reveal && <Explanation q={question} selected={selection} />}
                  <div className="question-navigation">
                    <button
                      disabled={session.index === 0}
                      onClick={() =>
                        setProgress((p) => ({
                          ...p,
                          session: { ...session, index: session.index - 1 },
                        }))
                      }
                    >
                      ← Previous
                    </button>
                    <span>
                      {session.index + 1} / {session.ids.length}
                    </span>
                    <button
                      disabled={session.index === session.ids.length - 1}
                      onClick={() =>
                        setProgress((p) => ({
                          ...p,
                          session: { ...session, index: session.index + 1 },
                        }))
                      }
                    >
                      Next →
                    </button>
                  </div>
                  <div className="question-map" aria-label="Jump to question">
                    {session.ids.map((id, i) => (
                      <button
                        key={id}
                        aria-label={`Go to question ${i + 1}`}
                        aria-current={i === session.index ? "step" : undefined}
                        className={`${i === session.index ? "current" : ""} ${session.selections[id]?.length ? "answered" : ""}`}
                        onClick={() =>
                          setProgress((p) => ({
                            ...p,
                            session: { ...session, index: i },
                          }))
                        }
                      >
                        {i + 1}
                      </button>
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
          {confirmReset && (
            <section
              className="card"
              role="alertdialog"
              aria-label="Reset study progress"
            >
              <h2>Reset all study progress?</h2>
              <p>
                This removes attempts, bookmarks, and the current session from
                this browser. Export a backup first if you want to keep them.
              </p>
              <button onClick={exportBackup}>Export backup before reset</button>
              <button
                className="primary"
                onClick={() => {
                  setProgress({ ...emptyProgress(), dark: progress.dark });
                  setStorageBlocked(false);
                  setConfirmReset(false);
                  setView("dashboard");
                  setMessage("Study progress reset.");
                }}
              >
                Confirm reset
              </button>
              <button onClick={() => setConfirmReset(false)}>
                Cancel reset
              </button>
            </section>
          )}
          <footer>
            <button
              className="text-button"
              onClick={() => setConfirmReset(true)}
            >
              Reset progress
            </button>
            <span>
              Local-first learning. Your progress stays in this browser.
            </span>
            <div>
              <button className="text-button" onClick={exportBackup}>
                ↓ Export backup
              </button>
              <button
                className="text-button"
                onClick={() => fileRef.current?.click()}
              >
                ↑ Import backup
              </button>
              <input
                ref={fileRef}
                className="sr-only"
                aria-label="Import backup file"
                type="file"
                accept="application/json,.json"
                onChange={(e) => void importBackup(e.target.files?.[0])}
              />
            </div>
          </footer>
        </main>
      </div>
    </div>
  );
}
