/**
 * API client for backend communication
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface QueryRequest {
  question: string;
  location: string;
  context?: Record<string, any>;
  conversation_id?: string;
}

export interface Citation {
  title: string;
  url: string;
  excerpt: string;
  source: string;
  published_date?: string;
  relevance_score?: number;
  similarity_score?: number;
  authority_level?: string;
  source_citation?: string;
}

export interface ConfidenceScore {
  level: 'high' | 'medium' | 'low';
  score: number;
  factors: Array<{
    name: string;
    score: number;
    weight: number;
    explanation: string;
  }>;
  explanation: string;
}

export interface GraphNode {
  id: string;
  type: string;
  data: Record<string, any>;
  position: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  label?: string;
  data?: Record<string, any>;
  animated?: boolean;
}

export interface SourceGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

// Inline citation for highlighting facts in the answer
export interface InlineCitation {
  id: string;
  fact: string;
  source_index: number;
  source_title: string;
  source_excerpt: string;
  source_url?: string;
}

// Retrieval flow for knowledge graph visualization
export interface RetrievalFlowNode {
  id: string;
  type: string;
  label: string;
  metadata?: Record<string, unknown>;
}

export interface RetrievalFlowEdge {
  source: string;
  target: string;
  label?: string;
  relevance_score?: number;
}

export interface RetrievalFlow {
  nodes: RetrievalFlowNode[];
  edges: RetrievalFlowEdge[];
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  inline_citations?: InlineCitation[];
  retrieval_flow?: RetrievalFlow;
  confidence: string;
  confidence_score?: ConfidenceScore;
  source_graph?: SourceGraph;
  processing_time_ms?: number;
  query_id?: string;
  conversation_id?: string;
  metadata?: {
    intent?: any;
    documents_used?: number;
    validation?: any;
    model_used?: string;
    processing_steps?: any;
    sources_searched?: string[];
    sources_found?: number;
    sources_used?: number;
    used_gpt_fallback?: boolean;
    total_processing_time_ms?: number;
  };
}

export interface ProcessingStep {
  step: string;
  status: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface DataCollectionResponse {
  status: string;
  message: string;
  jurisdiction?: string;
  source?: string;
}

export interface DataStats {
  jurisdiction: string;
  document_count: number;
  sources: string[];
}

// ============================================================================
// API Client Class
// ============================================================================

class APIClient {
  private baseUrl: string;
  private isRefreshing: boolean = false;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    skipAuth: boolean = false
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders: HeadersInit = {
      'Content-Type': 'application/json',
    };

    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      credentials: 'include', // Include cookies for auth
    });

    if (!response.ok) {
      // Handle 401 - try to refresh token (but only once, not for auth endpoints)
      if (response.status === 401 && !skipAuth && !this.isRefreshing) {
        this.isRefreshing = true;
        try {
          const refreshed = await this.refreshToken();
          this.isRefreshing = false;
          if (refreshed) {
            // Retry the request once
            return this.request(endpoint, options, true);
          }
        } catch {
          this.isRefreshing = false;
        }
        // If refresh failed, throw error (don't loop)
      }

      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // ==========================================================================
  // Authentication
  // ==========================================================================

  async register(email: string, password: string, fullName?: string): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    }, true); // Skip auth retry for auth endpoints
  }

  async login(email: string, password: string): Promise<TokenPair> {
    return this.request<TokenPair>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }, true); // Skip auth retry for auth endpoints
  }

  async logout(): Promise<void> {
    try {
      await this.request('/auth/logout', { method: 'POST' }, true);
    } catch {
      // Ignore logout errors
    }
  }

  async refreshToken(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      return response.ok;
    } catch {
      return false;
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      return await this.request<User>('/auth/me', {}, true);
    } catch {
      return null;
    }
  }

  // ==========================================================================
  // Queries (no auth required for MVP)
  // ==========================================================================

  async submitQuery(request: QueryRequest): Promise<QueryResponse> {
    return this.request<QueryResponse>('/api/queries', {
      method: 'POST',
      body: JSON.stringify(request),
    }, true); // Skip auth - queries work without login
  }

  // ==========================================================================
  // Health & Status
  // ==========================================================================

  async healthCheck(): Promise<{ status: string; database: string; environment: string }> {
    return this.request('/health', {}, true);
  }

  // ==========================================================================
  // Data Collection
  // ==========================================================================

  async startDataCollection(jurisdiction: string = 'colorado'): Promise<DataCollectionResponse> {
    return this.request<DataCollectionResponse>(
      `/api/data/collect?jurisdiction=${jurisdiction}`,
      { method: 'POST' },
      true
    );
  }

  async startSourceCollection(source: string, jurisdiction: string = 'colorado'): Promise<DataCollectionResponse> {
    return this.request<DataCollectionResponse>(
      `/api/data/collect/${source}?jurisdiction=${jurisdiction}`,
      { method: 'POST' },
      true
    );
  }

  async getDataStats(jurisdiction: string = 'colorado'): Promise<DataStats> {
    return this.request<DataStats>(`/api/data/stats?jurisdiction=${jurisdiction}`, {}, true);
  }

  // ==========================================================================
  // Conversations (no auth required for MVP)
  // ==========================================================================

  async createConversation(location: string = 'colorado'): Promise<{ conversation_id: string }> {
    return this.request<{ conversation_id: string }>(
      `/api/conversations/create?location=${location}`,
      { method: 'POST' },
      true // Skip auth - conversations work without login
    );
  }

  async deleteConversation(conversationId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(
      `/api/conversations/${conversationId}`,
      { method: 'DELETE' },
      true
    );
  }
}

// ============================================================================
// Singleton Instance & Exports
// ============================================================================

export const api = new APIClient();

// Legacy function exports for backward compatibility
export const submitQuery = (request: QueryRequest) => api.submitQuery(request);
export const healthCheck = () => api.healthCheck();
export const startDataCollection = (jurisdiction?: string) => api.startDataCollection(jurisdiction);
export const startSourceCollection = (source: string, jurisdiction?: string) => api.startSourceCollection(source, jurisdiction);
export const getDataStats = (jurisdiction?: string) => api.getDataStats(jurisdiction);
export const createConversation = (location?: string) => api.createConversation(location);
export const deleteConversation = (conversationId: string) => api.deleteConversation(conversationId);
