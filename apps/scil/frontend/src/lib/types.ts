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
