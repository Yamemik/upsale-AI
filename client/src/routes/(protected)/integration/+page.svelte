<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch, apiFetchBlob } from '$lib/api/client';
	import { INTEGRATION_API_KEY_STORAGE } from '$lib/constants';
	import { formatApiError } from '$lib/api/errors';

	let apiKey = $state('');
	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);

	let lookbackDays = $state('');
	let dateFrom = $state('');

	let pushJson = $state('[\n  {}\n]');

	onMount(() => {
		apiKey = localStorage.getItem(INTEGRATION_API_KEY_STORAGE) ?? '';
	});

	function saveKey() {
		localStorage.setItem(INTEGRATION_API_KEY_STORAGE, apiKey.trim());
		ok = 'Ключ сохранён локально';
		setTimeout(() => {
			if (ok === 'Ключ сохранён локально') ok = null;
		}, 2000);
	}

	async function syncSales() {
		err = null;
		ok = null;
		pending = true;
		try {
			const res = await apiFetch<{ status: string; synced_count: number }>('/integration/1c/sync-sales', {
				method: 'POST',
				apiKey: apiKey.trim() || null
			});
			ok = `${res.status}: ${res.synced_count} записей`;
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}

	async function syncHistory() {
		err = null;
		ok = null;
		pending = true;
		try {
			const q = new URLSearchParams();
			const lb = lookbackDays.trim();
			if (lb !== '') q.set('lookback_days', lb);
			const df = dateFrom.trim();
			if (df !== '') q.set('date_from', df);
			const suffix = q.toString() ? `?${q}` : '';
			const res = await apiFetch<Record<string, unknown>>(`/integration/1c/sync-sales-history${suffix}`, {
				method: 'POST',
				apiKey: apiKey.trim() || null
			});
			ok = JSON.stringify(res);
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}

	async function downloadKaggle() {
		err = null;
		ok = null;
		pending = true;
		try {
			const blob = await apiFetchBlob('/integration/1c/export/kaggle-dataset', {
				apiKey: apiKey.trim() || null
			});
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = 'kaggle_predict_future_sales.zip';
			a.click();
			URL.revokeObjectURL(url);
			ok = 'Архив скачан';
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}

	async function pushOrders() {
		err = null;
		ok = null;
		pending = true;
		try {
			let orders: unknown;
			try {
				orders = JSON.parse(pushJson);
			} catch {
				throw new Error('Некорректный JSON');
			}
			if (!Array.isArray(orders)) throw new Error('Ожидается массив заказов');
			const res = await apiFetch<unknown>('/integration/1c/push/orders', {
				method: 'POST',
				json: { orders },
				apiKey: apiKey.trim() || null
			});
			ok = typeof res === 'string' ? res : JSON.stringify(res);
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

<div class="space-y-8">
	<div>
		<h1 class="text-2xl font-semibold text-white">Интеграция 1С</h1>
		<p class="text-sm text-slate-400">
			Заголовок <code class="text-xs text-slate-500">X-API-KEY</code> · маршруты
			<code class="text-xs text-slate-500">/api/v1/integration/1c/*</code>
		</p>
	</div>

	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}
	{#if ok}
		<Alert variant="info">{ok}</Alert>
	{/if}

	<section class="ds-card p-6">
		<h2 class="font-semibold text-slate-100">API-ключ</h2>
		<p class="mt-1 text-xs text-slate-400">Хранится только в браузере (localStorage).</p>
		<div class="mt-4 flex flex-wrap gap-2">
			<input
				type="password"
				class="ds-input min-w-[240px] flex-1 text-sm"
				bind:value={apiKey}
				placeholder="ключ X-API-KEY"
				autocomplete="off"
			/>
			<button type="button" class="ds-btn-primary text-sm" onclick={saveKey}>Сохранить ключ</button>
		</div>
	</section>

	<section class="ds-card grid gap-4 p-6 sm:grid-cols-2">
		<div>
			<h3 class="font-medium text-slate-100">POST /sync-sales</h3>
			<p class="mt-1 text-xs text-slate-400">Синхронизация продаж из OData в ответ (без записи в БД по коду маршрута).</p>
			<button
				type="button"
				class="ds-btn-ghost mt-3 border border-slate-600 px-3 py-1.5 text-sm disabled:opacity-50"
				disabled={pending}
				onclick={() => syncSales()}>Выполнить</button
			>
		</div>
		<div>
			<h3 class="font-medium text-slate-100">POST /sync-sales-history</h3>
			<p class="mt-1 text-xs text-slate-400">Догрузка истории в БД (query: lookback_days, date_from).</p>
			<div class="mt-2 flex flex-wrap gap-2">
				<input type="number" class="ds-input w-28 text-sm" bind:value={lookbackDays} placeholder="дней назад" />
				<input type="date" class="ds-input text-sm" bind:value={dateFrom} />
			</div>
			<button
				type="button"
				class="ds-btn-ghost mt-3 border border-slate-600 px-3 py-1.5 text-sm disabled:opacity-50"
				disabled={pending}
				onclick={() => syncHistory()}>Выполнить</button
			>
		</div>
		<div>
			<h3 class="font-medium text-slate-100">GET /export/kaggle-dataset</h3>
			<p class="mt-1 text-xs text-slate-400">ZIP с CSV в формате Kaggle.</p>
			<button
				type="button"
				class="ds-btn-ghost mt-3 border border-slate-600 px-3 py-1.5 text-sm disabled:opacity-50"
				disabled={pending}
				onclick={() => downloadKaggle()}>Скачать ZIP</button
			>
		</div>
		<div class="sm:col-span-2">
			<h3 class="font-medium text-slate-100">POST /push/orders</h3>
			<p class="mt-1 text-xs text-slate-400">Тело: <code class="text-slate-500">{"{ \"orders\": [ ... ] }"}</code></p>
			<textarea
				class="ds-input mt-2 w-full font-mono text-xs"
				rows="8"
				bind:value={pushJson}
			></textarea>
			<button
				type="button"
				class="ds-btn-primary mt-3 text-sm disabled:opacity-50"
				disabled={pending}
				onclick={() => pushOrders()}>Отправить</button
			>
		</div>
	</section>
</div>
