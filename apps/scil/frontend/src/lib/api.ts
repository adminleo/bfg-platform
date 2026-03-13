const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
    this.name = "ApiError";
  }
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private headers(): HeadersInit {
    const headers: HeadersInit = { "Content-Type": "application/json" };
    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  /**
   * Handle 401 responses by clearing auth state and redirecting to login.
   */
  private handleUnauthorized(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_data");
    window.location.href = "/login";
  }

  private async handleResponse<T>(res: Response): Promise<T> {
    if (res.status === 401) {
      this.handleUnauthorized();
      throw new ApiError(401, "Sitzung abgelaufen. Bitte erneut anmelden.");
    }
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new ApiError(res.status, error.detail || `API Error ${res.status}`);
    }
    return res.json();
  }

  async get<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      headers: this.headers(),
    });
    return this.handleResponse<T>(res);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return this.handleResponse<T>(res);
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "PATCH",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });
    return this.handleResponse<T>(res);
  }

  async delete<T>(path: string): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });
    return this.handleResponse<T>(res);
  }

  /**
   * Send a message and return the SSE Response object for streaming.
   */
  async postSSE(path: string, body: unknown): Promise<Response> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: JSON.stringify(body),
    });
    if (res.status === 401) {
      this.handleUnauthorized();
      throw new Error("Sitzung abgelaufen. Bitte erneut anmelden.");
    }
    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(error.detail || `API Error ${res.status}`);
    }
    return res;
  }
}

export const api = new ApiClient(`${API_URL}/api/v1`);
export { API_URL };
