import { browser } from '$app/environment';
import { apiFetch } from '$lib/api/client';
import type { TokenResponse, UserMe } from '$lib/api/types';
import { ACCESS_TOKEN_KEY } from '$lib/constants';

let accessToken = $state<string | null>(browser ? localStorage.getItem(ACCESS_TOKEN_KEY) : null);

export const auth = $state({
	currentUser: null as UserMe | null,
	authLoading: false
});

export function setAccessToken(token: string | null) {
	accessToken = token;
	if (browser) {
		if (token) localStorage.setItem(ACCESS_TOKEN_KEY, token);
		else localStorage.removeItem(ACCESS_TOKEN_KEY);
	}
}

export async function refreshCurrentUser() {
	if (!accessToken) {
		auth.currentUser = null;
		return;
	}
	auth.authLoading = true;
	try {
		auth.currentUser = await apiFetch<UserMe>('/users/me');
	} catch {
		auth.currentUser = null;
		setAccessToken(null);
	} finally {
		auth.authLoading = false;
	}
}

export function logout() {
	setAccessToken(null);
	auth.currentUser = null;
}

export async function login(username: string, password: string): Promise<void> {
	const body = new URLSearchParams();
	body.set('username', username);
	body.set('password', password);

	const root = (import.meta.env.PUBLIC_API_URL as string | undefined)?.replace(/\/$/, '') ?? '';
	const res = await fetch(`${root}/api/v1/auth/login`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
		body
	});

	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw { detail: err.detail ?? res.statusText, status: res.status };
	}

	const data = (await res.json()) as TokenResponse;
	setAccessToken(data.access_token);
	await refreshCurrentUser();
}
