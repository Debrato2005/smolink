// Current fields: backend/app/schemas/url.py. IDs currently arrive as JSON numbers.
export interface CreateLinkInput {
  destination: string;
  alias?: string;
  expiresAt?: string;
}
export interface CreateUrlWire {
  id: number;
  short_code: string;
  short_url: string;
  destination: string;
  expires_at: string | null;
  created_at: string;
}
export interface CreatedLink {
  linkId: string | null;
  shortCode: string;
  shortUrl: string;
  destination: string;
  expiresAt: string | null;
  createdAt: string;
}
export interface LinkGateway {
  readonly source: 'fixture' | 'live';
  create(input: CreateLinkInput, signal?: AbortSignal): Promise<CreatedLink>;
}

export interface SavedLink extends CreatedLink {
  linkId: string;
  clicks: number;
  active: boolean;
}
export interface LinkReport {
  daily: { date: string; clicks: number }[];
  referrers: { name: string; clicks: number }[];
  devices: { name: string; clicks: number }[];
  updatedAt: string;
}
export type AccountAction =
  | 'login'
  | 'register'
  | 'verify-email'
  | 'forgot-password'
  | 'reset-password'
  | 'resend-verification';
export interface AccountInput {
  email?: string;
  password?: string;
  token?: string;
}
export type DemoScenario =
  | 'normal'
  | 'empty'
  | 'error'
  | 'limited'
  | 'locked'
  | 'unverified'
  | 'expired';
export interface ProductGateway extends LinkGateway {
  account(
    action: AccountAction,
    input: AccountInput,
    signal?: AbortSignal,
  ): Promise<void>;
  list(signal?: AbortSignal): Promise<SavedLink[]>;
  get(id: string, signal?: AbortSignal): Promise<SavedLink>;
  update(
    id: string,
    changes: { destination: string; expiresAt: string | null; active: boolean },
    signal?: AbortSignal,
  ): Promise<SavedLink>;
  remove(id: string, signal?: AbortSignal): Promise<void>;
  analytics(
    id: string,
    days: number,
    signal?: AbortSignal,
  ): Promise<LinkReport>;
  qr(link: CreatedLink, signal?: AbortSignal): Promise<string>;
  setScenario?: (scenario: DemoScenario) => void;
  resetDemo?: () => void;
}
