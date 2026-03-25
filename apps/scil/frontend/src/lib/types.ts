// SCIL Score types matching backend structure
export interface SCILScores {
  sensus: Record<string, number>;
  corpus: Record<string, number>;
  intellektus: Record<string, number>;
  lingua: Record<string, number>;
}

export interface PolygonAreaData {
  label: string;
  color: string;
  average: number;
  frequencies: Record<string, {
    score: number;
    label: string;
    level: string;
    level_label: string;
  }>;
}

export interface PolygonData {
  areas: Record<string, PolygonAreaData>;
  overall_mean: number;
  balance_score: number;
  total_frequencies: number;
  classified_count: number;
}

// Chat message types
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

// Cluster progress tracking
export interface ClusterProgress {
  sensus: { answered: number; total: number };
  corpus: { answered: number; total: number };
  intellektus: { answered: number; total: number };
  lingua: { answered: number; total: number };
}

// SSE event types from backend
export interface SSEEvent {
  type: "agent_text" | "scores_update" | "status" | "complete" | "session_state" | "cluster_progress" | "suggestions";
  content?: string;
  done?: boolean;
  scores?: SCILScores;
  progress?: number;
  polygon?: PolygonData;
  status?: string;
  result_id?: string;
  // Cluster progress fields
  cluster?: ClusterProgress;
  total_scored?: number;
  total_required?: number;
  // Suggestion chips
  suggestions?: string[];
}

// Session types
export interface Session {
  id: string;
  title: string | null;
  status: string;
  progress: number;
  created_at: string;
  completed_at: string | null;
}

export interface SessionDetail extends Session {
  conversation: Array<{ role: string; content: string }>;
  scores: SCILScores | null;
  polygon: PolygonData | null;
  cluster_progress: ClusterProgress | null;
  items_scored: number;
  items_total: number;
  suggestions: string[] | null;
}

export interface DiagnosticResult {
  id: string;
  scores: SCILScores;
  summary: string;
  recommendations: Array<{
    area: string;
    frequency: string;
    label: string;
    current_score: number;
    level: string;
  }>;
  polygon_data: PolygonData | null;
  created_at: string;
}

// Auth types
export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface UserData {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

// Code/Purchase types
export interface CodePackage {
  type: string;
  quantity: number;
  unit_price_cents: number;
  total_price_cents: number;
  label: string;
  savings_percent: number;
}

export interface DiagnosticCode {
  id: string;
  token_code: string;
  status: string;
  diagnostic_type: string;
  tier: string;
  created_at: string;
  activated_at: string | null;
  consumed_at: string | null;
  expires_at: string | null;
}

export interface Purchase {
  id: string;
  package_type: string;
  quantity: number;
  total_price_cents: number;
  status: string;
  codes: DiagnosticCode[];
  created_at: string;
  completed_at: string | null;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
  purchase_id: string;
}

// Coach types
export interface CoachDashboardStats {
  total_coachees: number;
  active_diagnostics: number;
  codes_available: number;
  completed_diagnostics: number;
  recent_invitations: number;
}

export interface CoacheeListItem {
  id: string;
  coachee_email: string;
  coachee_name: string | null;
  status: string;
  has_diagnostic: boolean;
  last_activity: string | null;
  created_at: string;
  notes: string | null;
}

export interface CoacheeDetail {
  id: string;
  coachee_email: string;
  coachee_name: string | null;
  status: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  diagnostic_runs: Array<{
    id: string;
    status: string;
    progress: number;
    started_at: string;
    completed_at: string | null;
    scores?: Record<string, unknown>;
    polygon_data?: PolygonData | null;
  }>;
  latest_scores: Record<string, unknown> | null;
  latest_polygon: PolygonData | null;
  token_code: string | null;
  token_status: string | null;
}

export interface CodeInventoryItem {
  id: string;
  token_code: string;
  status: string;
  diagnostic_type: string;
  tier: string;
  created_at: string;
  assigned_to: string | null;
}

export interface ActivityItem {
  type: string;
  description: string;
  timestamp: string;
  coachee_email: string | null;
}

export interface InviteResponse {
  id: string;
  coachee_email: string;
  status: string;
  invitation_token: string | null;
  message: string;
}

// Training types
export interface TrainingContentItem {
  id: string;
  slug: string;
  title: string;
  description: string;
  content_type: "video" | "exercise" | "reflection" | "article" | "quiz";
  area: "sensus" | "corpus" | "intellektus" | "lingua" | "general";
  target_frequency: string | null;
  difficulty: number;
  duration_minutes: number;
  body: Record<string, unknown>;
  tags: string[];
  author: string | null;
  author_bio: string | null;
  author_image_url: string | null;
  is_premium: boolean;
  price_cents: number | null;
  sort_order: number;
  lesson_count: number;
}

export interface TrainingDayProgress {
  id: string;
  started_at: string | null;
  completed_at: string | null;
  time_spent_minutes: number;
  reflection: string | null;
  rating: number | null;
  ai_feedback: string | null;
}

export interface TrainingDay {
  id: string;
  week_number: number;
  day_number: number;
  title: string;
  coaching_note: string | null;
  area: string;
  status: "locked" | "available" | "in_progress" | "completed" | "skipped";
  scheduled_date: string | null;
  content: TrainingContentItem | null;
  progress: TrainingDayProgress | null;
}

export interface TrainingPlanSummary {
  id: string;
  title: string;
  description: string | null;
  total_weeks: number;
  days_per_week: number;
  status: "draft" | "active" | "paused" | "completed" | "archived";
  overall_progress: number;
  current_week: number;
  focus_areas: Record<string, unknown>;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface TrainingPlanDetail extends TrainingPlanSummary {
  ai_rationale: string | null;
  days: TrainingDay[];
}

export interface TodayTraining {
  has_training: boolean;
  plan_id: string | null;
  plan_title: string | null;
  day: TrainingDay | null;
  stats: TrainingStats | null;
}

export interface TrainingStats {
  total_completed_days: number;
  total_time_minutes: number;
  average_rating: number | null;
  current_streak: number;
  active_plan: {
    id: string;
    title: string;
    progress: number;
    current_week: number;
  } | null;
}

// Booking types
export interface AvailabilitySlot {
  id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  recurrence: string;
  notes: string | null;
  is_active: boolean;
  created_at: string;
}

export interface AvailableTime {
  date: string;
  time: string;
  datetime: string;
  duration_minutes: number;
  slot_id: string;
}

export interface Booking {
  id: string;
  coach_id: string;
  coachee_id: string;
  coach_name: string | null;
  coachee_name: string | null;
  scheduled_at: string;
  duration_minutes: number;
  status: "requested" | "confirmed" | "cancelled" | "completed" | "no_show";
  topic: string | null;
  coachee_notes: string | null;
  coach_notes: string | null;
  meeting_link: string | null;
  completed_at: string | null;
  summary: string | null;
  has_briefing: boolean;
  created_at: string;
}

export interface SessionBriefing {
  id: string;
  status: string;
  content: string | null;
  coachee_profile_summary: string | null;
  scil_highlights: Record<string, unknown> | null;
  suggested_topics: string[] | null;
  suggested_exercises: string[] | null;
  previous_session_notes: string | null;
  training_progress_summary: string | null;
  generated_at: string | null;
}
