export const ACCESS_TOKEN_KEY = 'upsale_access_token';
export const INTEGRATION_API_KEY_STORAGE = 'upsale_1c_api_key';

/** База API без завершающего слэша (для ссылок вне SvelteKit, например Swagger). */
export function publicApiOrigin(): string {
	const env = import.meta.env.PUBLIC_API_URL as string | undefined;
	if (env && env.trim().length > 0) {
		return env.replace(/\/$/, '');
	}
	return 'http://127.0.0.1:8000';
}

export function getApiDocsUrl(): string {
	return `${publicApiOrigin()}/api/docs`;
}
