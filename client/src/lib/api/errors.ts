import type { ApiError } from './types';

export function formatApiError(err: unknown): string {
	if (err && typeof err === 'object' && 'detail' in err) {
		const d = (err as ApiError).detail;
		if (typeof d === 'string') return d;
		if (Array.isArray(d)) {
			return d
				.map((x) => (typeof x === 'string' ? x : (x as { msg?: string }).msg ?? JSON.stringify(x)))
				.join('; ');
		}
	}
	if (err instanceof Error) return err.message;
	return String(err);
}
