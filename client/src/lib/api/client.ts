import { ACCESS_TOKEN_KEY } from '$lib/constants';
import type { ApiError } from './types';

function readStoredToken(): string | null {
	if (typeof window === 'undefined') return null;
	return localStorage.getItem(ACCESS_TOKEN_KEY);
}

function apiBase(): string {
	const env = import.meta.env.PUBLIC_API_URL as string | undefined;
	if (env && env.length > 0) {
		return env.replace(/\/$/, '');
	}
	return '';
}

export function apiUrl(path: string): string {
	const p = path.startsWith('/') ? path : `/${path}`;
	return `${apiBase()}${p}`;
}

async function parseError(res: Response): Promise<ApiError> {
	let detail: ApiError['detail'] = res.statusText;
	try {
		const body = await res.json();
		if (body?.detail !== undefined) detail = body.detail;
	} catch {
		/* ignore */
	}
	return { detail, status: res.status };
}

export type FetchOptions = RequestInit & {
	json?: unknown;
	skipAuth?: boolean;
	apiKey?: string | null;
};

export async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
	const { json, skipAuth, apiKey, headers: initHeaders, ...rest } = options;
	const headers = new Headers(initHeaders);

	if (json !== undefined) {
		headers.set('Content-Type', 'application/json');
	}

	if (!skipAuth) {
		const token = readStoredToken();
		if (token) headers.set('Authorization', `Bearer ${token}`);
	}

	if (apiKey) {
		headers.set('X-API-KEY', apiKey);
	}

	const url = apiUrl(path.startsWith('/api/') ? path : `/api/v1${path.startsWith('/') ? path : `/${path}`}`);

	const res = await fetch(url, {
		...rest,
		headers,
		body: json !== undefined ? JSON.stringify(json) : rest.body
	});

	if (!res.ok) {
		throw await parseError(res);
	}

	if (res.status === 204) {
		return undefined as T;
	}

	const ct = res.headers.get('content-type');
	if (ct?.includes('application/json')) {
		return (await res.json()) as T;
	}

	return (await res.text()) as T;
}

export async function apiFetchBlob(path: string, options: FetchOptions = {}): Promise<Blob> {
	const { skipAuth, apiKey, headers: initHeaders, ...rest } = options;
	const headers = new Headers(initHeaders);

	if (!skipAuth) {
		const token = readStoredToken();
		if (token) headers.set('Authorization', `Bearer ${token}`);
	}
	if (apiKey) headers.set('X-API-KEY', apiKey);

	const url = apiUrl(path.startsWith('/api/') ? path : `/api/v1${path.startsWith('/') ? path : `/${path}`}`);

	const res = await fetch(url, { ...rest, headers });
	if (!res.ok) {
		throw await parseError(res);
	}
	return res.blob();
}
