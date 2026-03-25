"use client";

import { useEffect, useState, useMemo, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import type { TrainingContentItem } from "@/lib/types";

interface EnrollmentState {
  enrolled: boolean;
  status?: string;
  enrolled_at?: string;
  completed_at?: string;
}

// ---------------------------------------------------------------------------
// Constants & Config
// ---------------------------------------------------------------------------

const AREA_CONFIG: Record<
  string,
  { label: string; color: string; bg: string; border: string; icon: string }
> = {
  sensus: {
    label: "Sensus",
    color: "text-rose-600",
    bg: "bg-rose-500/10",
    border: "border-rose-500/20",
    icon: "S",
  },
  corpus: {
    label: "Corpus",
    color: "text-amber-600",
    bg: "bg-amber-500/10",
    border: "border-amber-500/20",
    icon: "C",
  },
  intellektus: {
    label: "Intellektus",
    color: "text-blue-600",
    bg: "bg-blue-500/10",
    border: "border-blue-500/20",
    icon: "I",
  },
  lingua: {
    label: "Lingua",
    color: "text-emerald-600",
    bg: "bg-emerald-500/10",
    border: "border-emerald-500/20",
    icon: "L",
  },
  general: {
    label: "Allgemein",
    color: "text-slate-600",
    bg: "bg-slate-500/10",
    border: "border-slate-500/20",
    icon: "G",
  },
};

const CONTENT_TYPE_CONFIG: Record<
  string,
  { label: string; iconPath: string }
> = {
  video: {
    label: "Video",
    iconPath:
      "M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z",
  },
  exercise: {
    label: "Uebung",
    iconPath:
      "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  },
  reflection: {
    label: "Reflexion",
    iconPath:
      "M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z",
  },
  article: {
    label: "Artikel",
    iconPath:
      "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z",
  },
  quiz: {
    label: "Quiz",
    iconPath:
      "M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
  },
};

// ---------------------------------------------------------------------------
// Markdown renderer (simple)
// ---------------------------------------------------------------------------

function renderMarkdown(md: string): string {
  let html = md
    // Code blocks (fenced)
    .replace(
      /```(\w*)\n([\s\S]*?)```/g,
      '<pre class="bg-black/[0.03] border border-black/[0.06] rounded-xl p-4 overflow-x-auto my-4"><code>$2</code></pre>'
    )
    // Inline code
    .replace(
      /`([^`]+)`/g,
      '<code class="bg-black/[0.05] px-1.5 py-0.5 rounded text-sm font-mono text-slate-700">$1</code>'
    )
    // Headers
    .replace(
      /^### (.+)$/gm,
      '<h3 class="text-lg font-semibold text-slate-900 mt-6 mb-2">$1</h3>'
    )
    .replace(
      /^## (.+)$/gm,
      '<h2 class="text-xl font-bold text-slate-900 mt-8 mb-3">$1</h2>'
    )
    .replace(
      /^# (.+)$/gm,
      '<h1 class="text-2xl font-bold text-slate-900 mt-8 mb-4">$1</h1>'
    )
    // Bold & Italic
    .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Unordered lists
    .replace(
      /^[\-\*] (.+)$/gm,
      '<li class="ml-4 pl-2 text-slate-600 relative before:content-[\'\\2022\'] before:absolute before:-left-3 before:text-scil">$1</li>'
    )
    // Ordered lists
    .replace(
      /^\d+\. (.+)$/gm,
      '<li class="ml-4 pl-2 text-slate-600 list-decimal">$1</li>'
    )
    // Blockquotes
    .replace(
      /^> (.+)$/gm,
      '<blockquote class="border-l-3 border-scil/30 pl-4 italic text-slate-500 my-4">$1</blockquote>'
    )
    // Horizontal rules
    .replace(
      /^---$/gm,
      '<hr class="my-6 border-black/[0.06]" />'
    )
    // Links
    .replace(
      /\[([^\]]+)\]\(([^)]+)\)/g,
      '<a href="$2" class="text-scil hover:underline" target="_blank" rel="noopener noreferrer">$1</a>'
    )
    // Line breaks -> paragraphs
    .replace(/\n\n/g, '</p><p class="text-slate-600 leading-relaxed mb-3">')
    .replace(/\n/g, "<br />");

  // Wrap consecutive <li> elements
  html = html.replace(
    /(<li[^>]*>.*?<\/li>(\s*<br \/>)?)+/g,
    (match) => `<ul class="space-y-1.5 my-3">${match.replace(/<br \/>/g, "")}</ul>`
  );

  return `<p class="text-slate-600 leading-relaxed mb-3">${html}</p>`;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function DifficultyDots({ level }: { level: number }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((n) => (
        <div
          key={n}
          className={`w-2 h-2 rounded-full transition-colors ${
            n <= level ? "bg-scil" : "bg-black/[0.08]"
          }`}
        />
      ))}
    </div>
  );
}

function AuthorCard({
  name,
  bio,
  imageUrl,
}: {
  name: string;
  bio: string | null;
  imageUrl: string | null;
}) {
  const initials = name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="flex items-start gap-3 p-4 bg-black/[0.02] border border-black/[0.06] rounded-xl">
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={name}
          className="w-10 h-10 rounded-full object-cover flex-shrink-0"
        />
      ) : (
        <div className="w-10 h-10 rounded-full bg-scil/15 flex items-center justify-center flex-shrink-0">
          <span className="text-sm font-semibold text-scil">{initials}</span>
        </div>
      )}
      <div className="min-w-0">
        <div className="text-sm font-medium text-slate-900">{name}</div>
        {bio && (
          <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{bio}</p>
        )}
      </div>
    </div>
  );
}

function VideoPlaceholder({ content }: { content: TrainingContentItem }) {
  const videoUrl = content.body.video_url as string | undefined;
  return (
    <div className="space-y-4">
      <div className="relative aspect-video bg-black/[0.03] border border-black/[0.06] rounded-2xl overflow-hidden flex items-center justify-center">
        {videoUrl ? (
          <iframe
            src={videoUrl}
            className="absolute inset-0 w-full h-full"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            title={content.title}
          />
        ) : (
          <div className="text-center p-8">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-scil/10 flex items-center justify-center">
              <svg
                className="w-8 h-8 text-scil"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-900">Video wird geladen</p>
            <p className="text-xs text-slate-400 mt-1">
              Das Video steht nach dem Start zur Verfuegung
            </p>
          </div>
        )}
      </div>
      {Boolean(content.body.video_description) && (
        <div className="p-4 bg-black/[0.02] border border-black/[0.06] rounded-xl">
          <p className="text-sm text-slate-600">
            {String(content.body.video_description)}
          </p>
        </div>
      )}
    </div>
  );
}

function ExerciseContent({ content }: { content: TrainingContentItem }) {
  const { body } = content;
  const instruction = body.instruction as string | undefined;
  const steps = body.steps as string[] | undefined;
  const tips = body.tips as string[] | undefined;
  const reflectionPrompt = body.reflection_prompt as string | undefined;

  return (
    <div className="space-y-6">
      {instruction && (
        <div className="p-4 bg-scil/[0.05] border border-scil/15 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-4 h-4 text-scil"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm font-semibold text-slate-900">
              Anleitung
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">{instruction}</p>
        </div>
      )}

      {steps && steps.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-slate-900 mb-3">
            Schritte
          </h3>
          <div className="space-y-3">
            {steps.map((step, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-3 bg-white border border-black/[0.06] rounded-xl"
              >
                <div className="w-7 h-7 rounded-lg bg-scil/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-scil stat-number">
                    {i + 1}
                  </span>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed pt-1">
                  {step}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {tips && tips.length > 0 && (
        <div className="p-4 bg-amber-500/[0.06] border border-amber-500/15 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-4 h-4 text-amber-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
              />
            </svg>
            <span className="text-sm font-semibold text-amber-800">Tipps</span>
          </div>
          <ul className="space-y-1.5">
            {tips.map((tip, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-amber-900/70"
              >
                <span className="text-amber-500 mt-0.5">&#8226;</span>
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}

      {reflectionPrompt && (
        <div className="p-4 bg-blue-500/[0.06] border border-blue-500/15 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-4 h-4 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"
              />
            </svg>
            <span className="text-sm font-semibold text-blue-800">
              Reflexionsfrage
            </span>
          </div>
          <p className="text-sm text-blue-900/70 leading-relaxed italic">
            {reflectionPrompt}
          </p>
        </div>
      )}
    </div>
  );
}

function ReflectionContent({ content }: { content: TrainingContentItem }) {
  const { body } = content;
  const instruction = body.instruction as string | undefined;
  const prompts = body.prompts as string[] | undefined;

  return (
    <div className="space-y-6">
      {instruction && (
        <div className="p-4 bg-blue-500/[0.06] border border-blue-500/15 rounded-xl">
          <div className="flex items-center gap-2 mb-2">
            <svg
              className="w-4 h-4 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <span className="text-sm font-semibold text-slate-900">
              Anleitung
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed">{instruction}</p>
        </div>
      )}

      {prompts && prompts.length > 0 && (
        <div>
          <h3 className="text-base font-semibold text-slate-900 mb-3">
            Reflexionsfragen
          </h3>
          <div className="space-y-3">
            {prompts.map((prompt, i) => (
              <div
                key={i}
                className="flex items-start gap-3 p-4 glass-card rounded-xl"
              >
                <div className="w-7 h-7 rounded-full bg-blue-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <svg
                    className="w-3.5 h-3.5 text-blue-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed pt-1">
                  {prompt}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function QuizContent({ content }: { content: TrainingContentItem }) {
  const { body } = content;
  const questions = body.questions as
    | Array<{ question: string; options?: string[]; answer?: string }>
    | undefined;

  if (!questions || questions.length === 0) {
    return (
      <div className="p-6 glass-card rounded-xl text-center">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-scil/10 flex items-center justify-center">
          <svg
            className="w-6 h-6 text-scil"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <p className="text-sm text-slate-500">
          Das Quiz wird nach dem Start angezeigt.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h3 className="text-base font-semibold text-slate-900">
        {questions.length} Frage{questions.length !== 1 ? "n" : ""}
      </h3>
      {questions.map((q, i) => (
        <div
          key={i}
          className="p-4 glass-card rounded-xl"
        >
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg bg-scil/10 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-scil stat-number">
                {i + 1}
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-slate-900">{q.question}</p>
              {q.options && (
                <ul className="mt-2 space-y-1.5">
                  {q.options.map((opt, oi) => (
                    <li
                      key={oi}
                      className="flex items-center gap-2 text-sm text-slate-600"
                    >
                      <div className="w-4 h-4 rounded-full border border-black/[0.12] flex-shrink-0" />
                      {opt}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function ArticleContent({ content }: { content: TrainingContentItem }) {
  const markdown = content.body.content_markdown as string | undefined;
  if (!markdown) {
    return (
      <p className="text-sm text-slate-400 italic">
        Kein Artikelinhalt verfuegbar.
      </p>
    );
  }
  return (
    <div
      className="prose prose-slate max-w-none"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(markdown) }}
    />
  );
}

function LessonsSidebar({
  lessons,
}: {
  lessons: Array<{ title: string; description?: string; duration_minutes?: number }>;
}) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-1">
        <svg
          className="w-4 h-4 text-scil"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M4 6h16M4 10h16M4 14h16M4 18h16"
          />
        </svg>
        <h3 className="text-sm font-semibold text-slate-900">
          Lektionen ({lessons.length})
        </h3>
      </div>
      <div className="space-y-1.5">
        {lessons.map((lesson, i) => (
          <div
            key={i}
            className="flex items-start gap-3 p-3 rounded-xl hover:bg-black/[0.03] transition-colors cursor-default"
          >
            <div className="w-6 h-6 rounded-lg bg-black/[0.04] flex items-center justify-center flex-shrink-0 mt-0.5">
              <span className="text-[10px] font-bold text-slate-500 stat-number">
                {i + 1}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium text-slate-700 truncate">
                {lesson.title}
              </div>
              {lesson.duration_minutes && (
                <div className="text-[10px] text-slate-400 mt-0.5">
                  {lesson.duration_minutes} Min.
                </div>
              )}
            </div>
            {/* Progress indicator circle */}
            <div className="w-5 h-5 rounded-full border-2 border-black/[0.08] flex-shrink-0 mt-0.5" />
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main Page
// ---------------------------------------------------------------------------

export default function TrainingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const contentId = params.contentId as string;

  const [content, setContent] = useState<TrainingContentItem | null>(null);
  const [allContent, setAllContent] = useState<TrainingContentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enrollment, setEnrollment] = useState<EnrollmentState | null>(null);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    async function fetchContent() {
      setIsLoading(true);
      setError(null);
      try {
        const items = await api.get<TrainingContentItem[]>("/training/content");
        setAllContent(items);
        const found = items.find(
          (item) => item.id === contentId || item.slug === contentId
        );
        if (found) {
          setContent(found);
        } else {
          setError("Trainingsinhalt nicht gefunden.");
        }
      } catch {
        setError("Fehler beim Laden des Trainingsinhalts.");
      } finally {
        setIsLoading(false);
      }
    }
    fetchContent();
  }, [contentId]);

  // Check enrollment status
  useEffect(() => {
    if (!contentId) return;
    api
      .get<EnrollmentState>(`/training/enrollments/${contentId}`)
      .then(setEnrollment)
      .catch(() => setEnrollment(null));
  }, [contentId]);

  const handleEnroll = useCallback(async () => {
    if (!contentId) return;
    setEnrolling(true);
    try {
      await api.post(`/training/enroll/${contentId}`);
      setEnrollment({ enrolled: true, status: "active" });
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Fehler beim Einschreiben";
      setError(msg);
    } finally {
      setEnrolling(false);
    }
  }, [contentId]);

  // Find next content in same area
  const nextContent = useMemo(() => {
    if (!content || allContent.length === 0) return null;
    const sameArea = allContent
      .filter((c) => c.area === content.area && c.id !== content.id)
      .sort((a, b) => a.sort_order - b.sort_order);
    const currentIndex = sameArea.findIndex(
      (c) => c.sort_order > content.sort_order
    );
    return currentIndex >= 0 ? sameArea[currentIndex] : sameArea[0] || null;
  }, [content, allContent]);

  const lessonsOverview = content?.body?.lessons_overview as
    | Array<{ title: string; description?: string; duration_minutes?: number }>
    | undefined;

  const area = content ? AREA_CONFIG[content.area] || AREA_CONFIG.general : null;
  const typeConfig = content
    ? CONTENT_TYPE_CONFIG[content.content_type] || CONTENT_TYPE_CONFIG.article
    : null;

  // Format price
  const formatPrice = (cents: number) => {
    return new Intl.NumberFormat("de-CH", {
      style: "currency",
      currency: "CHF",
    }).format(cents / 100);
  };

  // Sidebar content for lessons
  const leftSidebar = (
    <div className="flex flex-col h-full">
      <div className="p-4">
        <button
          onClick={() => router.push("/training")}
          className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 transition-colors mb-4"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          Zurueck zum Training
        </button>

        {content && area && (
          <>
            <div className="flex items-center gap-2 mb-1">
              <svg
                className="w-5 h-5 text-scil"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
              <h2 className="text-sm font-semibold text-slate-900">
                {content.title}
              </h2>
            </div>
            <p className="text-xs text-slate-400">{area.label}</p>
          </>
        )}
      </div>

      {/* Lessons list in sidebar */}
      {lessonsOverview && lessonsOverview.length > 0 && (
        <div className="px-4 pb-4 flex-1 overflow-y-auto">
          <LessonsSidebar lessons={lessonsOverview} />
        </div>
      )}

      {/* Quick nav */}
      {content && (
        <div className="p-4 border-t border-black/[0.06] space-y-2">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2">
            Details
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Dauer</span>
            <span className="text-slate-900 font-medium">
              {content.duration_minutes} Min.
            </span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Schwierigkeit</span>
            <DifficultyDots level={content.difficulty} />
          </div>
          {content.lesson_count > 0 && (
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-500">Lektionen</span>
              <span className="text-slate-900 font-medium stat-number">
                {content.lesson_count}
              </span>
            </div>
          )}
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">Typ</span>
            <span className="text-slate-900 font-medium">
              {typeConfig?.label}
            </span>
          </div>
        </div>
      )}
    </div>
  );

  return (
    <AppShell
      leftSidebar={leftSidebar}
      rightDefaultOpen={false}
    >
      <div className="w-full max-w-4xl mx-auto px-4 sm:px-6 py-6">
        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="flex gap-1">
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
              <div className="w-2 h-2 rounded-full bg-scil typing-dot" />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="animate-fade-in-up">
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-600 text-sm">
              {error}
            </div>
            <button
              onClick={() => router.push("/training")}
              className="px-4 py-2 btn-ghost text-slate-600 text-sm rounded-xl"
            >
              Zurueck zum Training
            </button>
          </div>
        )}

        {/* Content loaded */}
        {content && area && typeConfig && (
          <div className="space-y-8 animate-fade-in-up">
            {/* ── Hero Section ──────────────────────────────────────────── */}
            <section>
              {/* Breadcrumb */}
              <div className="flex items-center gap-2 text-xs text-slate-400 mb-4">
                <button
                  onClick={() => router.push("/training")}
                  className="hover:text-slate-600 transition-colors"
                >
                  Training
                </button>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                <span className="text-slate-600">{content.title}</span>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap items-center gap-2 mb-4">
                {/* Content type badge */}
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-scil/10 text-scil text-xs font-medium">
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d={typeConfig.iconPath}
                    />
                  </svg>
                  {typeConfig.label}
                </span>

                {/* Area badge */}
                <span
                  className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${area.bg} ${area.color}`}
                >
                  <span className="w-4 h-4 rounded-md flex items-center justify-center text-[10px] font-bold">
                    {area.icon}
                  </span>
                  {area.label}
                </span>

                {/* Premium badge */}
                {content.is_premium && (
                  <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 text-xs font-medium">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                    Premium
                  </span>
                )}

                {/* Target frequency */}
                {content.target_frequency && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full bg-slate-500/10 text-slate-500 text-xs font-medium">
                    {content.target_frequency}
                  </span>
                )}
              </div>

              {/* Title & Description */}
              <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-3 leading-tight">
                {content.title}
              </h1>
              <p className="text-base text-slate-500 leading-relaxed mb-6 max-w-2xl">
                {content.description}
              </p>

              {/* Meta row */}
              <div className="flex flex-wrap items-center gap-4 mb-6">
                {/* Duration */}
                <div className="flex items-center gap-1.5 text-sm text-slate-500">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <span>{content.duration_minutes} Minuten</span>
                </div>

                {/* Difficulty */}
                <div className="flex items-center gap-1.5 text-sm text-slate-500">
                  <span>Schwierigkeit:</span>
                  <DifficultyDots level={content.difficulty} />
                </div>

                {/* Lesson count */}
                {content.lesson_count > 0 && (
                  <div className="flex items-center gap-1.5 text-sm text-slate-500">
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.5}
                        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                      />
                    </svg>
                    <span>
                      {content.lesson_count} Lektion
                      {content.lesson_count !== 1 ? "en" : ""}
                    </span>
                  </div>
                )}
              </div>

              {/* Tags */}
              {content.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {content.tags.map((tag, i) => (
                    <span
                      key={i}
                      className="px-2.5 py-1 bg-black/[0.03] border border-black/[0.06] rounded-lg text-xs text-slate-500"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              {/* Author card */}
              {content.author && (
                <div className="mb-6">
                  <AuthorCard
                    name={content.author}
                    bio={content.author_bio}
                    imageUrl={content.author_image_url}
                  />
                </div>
              )}

              {/* Action button */}
              <div className="flex flex-wrap items-center gap-3">
                {content.is_premium && content.price_cents ? (
                  enrollment?.enrolled ? (
                    <button
                      onClick={handleEnroll}
                      className="px-6 py-3 btn-glass text-white font-medium rounded-xl text-sm"
                    >
                      {enrollment.status === "completed"
                        ? "Abgeschlossen \u2713"
                        : "Fortsetzen"}
                    </button>
                  ) : (
                    <>
                      <button
                        onClick={() => router.push("/resources?tab=trainings")}
                        className="px-6 py-3 btn-glass text-white font-medium rounded-xl text-sm"
                      >
                        Jetzt kaufen &middot;{" "}
                        {formatPrice(content.price_cents)}
                      </button>
                      <span className="text-xs text-slate-400">
                        Einmalzahlung, lebenslanger Zugang
                      </span>
                    </>
                  )
                ) : enrollment?.enrolled ? (
                  <button
                    className={`px-6 py-3 font-medium rounded-xl text-sm ${
                      enrollment.status === "completed"
                        ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 cursor-default"
                        : "btn-glass text-white"
                    }`}
                    disabled={enrollment.status === "completed"}
                  >
                    {enrollment.status === "completed"
                      ? "Abgeschlossen \u2713"
                      : "Fortsetzen"}
                  </button>
                ) : (
                  <button
                    onClick={handleEnroll}
                    disabled={enrolling}
                    className="px-6 py-3 btn-glass text-white font-medium rounded-xl text-sm disabled:opacity-50"
                  >
                    {enrolling ? "Wird eingeschrieben..." : "Training starten"}
                  </button>
                )}
              </div>
            </section>

            {/* ── Content Body ──────────────────────────────────────────── */}
            <section>
              <div className="flex flex-col lg:flex-row gap-8">
                {/* Main content */}
                <div className="flex-1 min-w-0">
                  <div className="glass-card rounded-2xl p-6 sm:p-8">
                    <h2 className="text-lg font-semibold text-slate-900 mb-6 flex items-center gap-2">
                      <svg
                        className="w-5 h-5 text-scil"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.5}
                          d={typeConfig.iconPath}
                        />
                      </svg>
                      {content.content_type === "article"
                        ? "Artikel"
                        : content.content_type === "exercise"
                        ? "Uebungsanleitung"
                        : content.content_type === "reflection"
                        ? "Reflexion"
                        : content.content_type === "video"
                        ? "Video"
                        : "Quiz"}
                    </h2>

                    {content.content_type === "article" && (
                      <ArticleContent content={content} />
                    )}
                    {content.content_type === "exercise" && (
                      <ExerciseContent content={content} />
                    )}
                    {content.content_type === "reflection" && (
                      <ReflectionContent content={content} />
                    )}
                    {content.content_type === "video" && (
                      <VideoPlaceholder content={content} />
                    )}
                    {content.content_type === "quiz" && (
                      <QuizContent content={content} />
                    )}
                  </div>
                </div>

                {/* Lessons sidebar on desktop (if present) */}
                {lessonsOverview && lessonsOverview.length > 0 && (
                  <aside className="hidden lg:block w-72 flex-shrink-0">
                    <div className="glass-card rounded-2xl p-5 sticky top-6">
                      <LessonsSidebar lessons={lessonsOverview} />

                      {/* Progress bar */}
                      <div className="mt-4 pt-4 border-t border-black/[0.06]">
                        <div className="flex items-center justify-between text-xs mb-2">
                          <span className="text-slate-500">Fortschritt</span>
                          <span className="text-slate-900 font-medium stat-number">
                            0 / {lessonsOverview.length}
                          </span>
                        </div>
                        <div className="h-1.5 bg-black/[0.04] rounded-full overflow-hidden">
                          <div
                            className="h-full bg-scil rounded-full transition-all duration-500"
                            style={{ width: "0%" }}
                          />
                        </div>
                      </div>
                    </div>
                  </aside>
                )}
              </div>
            </section>

            {/* ── Navigation Footer ────────────────────────────────────── */}
            <section className="pt-4 border-t border-black/[0.06]">
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <button
                  onClick={() => router.push("/training")}
                  className="flex items-center gap-2 px-4 py-2.5 btn-ghost text-slate-600 text-sm rounded-xl"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                  Zurueck zum Training
                </button>

                {nextContent && (
                  <button
                    onClick={() =>
                      router.push(`/training/${nextContent.id}`)
                    }
                    className="flex items-center gap-2 px-4 py-2.5 btn-glass text-white text-sm font-medium rounded-xl"
                  >
                    Naechstes Training
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </button>
                )}
              </div>

              {/* Next content preview */}
              {nextContent && (
                <div
                  onClick={() =>
                    router.push(`/training/${nextContent.id}`)
                  }
                  className="mt-4 glass-card-interactive rounded-2xl p-4 cursor-pointer"
                >
                  <div className="text-xs text-slate-400 mb-1">
                    Naechstes Training im Bereich{" "}
                    {(AREA_CONFIG[nextContent.area] || AREA_CONFIG.general).label}
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-medium text-slate-900">
                        {nextContent.title}
                      </h4>
                      <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                        {nextContent.description}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${
                          (
                            AREA_CONFIG[nextContent.area] ||
                            AREA_CONFIG.general
                          ).bg
                        } ${
                          (
                            AREA_CONFIG[nextContent.area] ||
                            AREA_CONFIG.general
                          ).color
                        }`}
                      >
                        {
                          (
                            CONTENT_TYPE_CONFIG[nextContent.content_type] ||
                            CONTENT_TYPE_CONFIG.article
                          ).label
                        }
                      </span>
                      <span className="text-xs text-slate-400">
                        {nextContent.duration_minutes} Min.
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </section>
          </div>
        )}
      </div>
    </AppShell>
  );
}
