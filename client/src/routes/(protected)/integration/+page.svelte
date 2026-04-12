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
		<h1 class="text-2xl font-bold text-slate-900">Интеграция 1С</h1>
		<p class="text-sm text-slate-600">
			Заголовок <code class="text-xs">X-API-KEY</code> · маршруты
			<code class="text-xs">/api/v1/integration/1c/*</code>
		</p>
	</div>

	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}
	{#if ok}
		<Alert variant="info">{ok}</Alert>
	{/if}

	<section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
		<h2 class="font-semibold text-slate-900">API-ключ</h2>
		<p class="mt-1 text-xs text-slate-600">Хранится только в браузере (localStorage).</p>
		<div class="mt-4 flex flex-wrap gap-2">
			<input
				type="password"
				class="min-w-[240px] flex-1 rounded-md border-slate-300 text-sm"
				bind:value={apiKey}
				placeholder="X-API-KEY"
				autocomplete="off"
			/>
			<button
				type="button"
				class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
				onclick={saveKey}>Сохранить ключ</button
			>
		</div>
	</section>

	<section class="grid gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:grid-cols-2">
		<div>
			<h3 class="font-medium text-slate-900">POST /sync-sales</h3>
			<p class="mt-1 text-xs text-slate-600">Синхронизация продаж из OData в ответ (без записи в БД по коду маршрута).</p>
			<button
				type="button"
				class="mt-3 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
				disabled={pending}
				onclick={() => syncSales()}>Выполнить</button
			>
		</div>
		<div>
			<h3 class="font-medium text-slate-900">POST /sync-sales-history</h3>
			<p class="mt-1 text-xs text-slate-600">Догрузка истории в БД (query: lookback_days, date_from).</p>
			<div class="mt-2 flex flex-wrap gap-2">
				<input
					type="number"
					class="w-28 rounded-md border-slate-300 text-sm"
					bind:value={lookbackDays}
					placeholder="lookback"
				/>
				<input type="date" class="rounded-md border-slate-300 text-sm" bind:value={dateFrom} />
			</div>
			<button
				type="button"
				class="mt-3 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
				disabled={pending}
				onclick={() => syncHistory()}>Выполнить</button
			>
		</div>
		<div>
			<h3 class="font-medium text-slate-900">GET /export/kaggle-dataset</h3>
			<p class="mt-1 text-xs text-slate-600">ZIP с CSV в формате Kaggle.</p>
			<button
				type="button"
				class="mt-3 rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm hover:bg-slate-50 disabled:opacity-50"
				disabled={pending}
				onclick={() => downloadKaggle()}>Скачать ZIP</button
			>
		</div>
		<div class="sm:col-span-2">
			<h3 class="font-medium text-slate-900">POST /push/orders</h3>
			<p class="mt-1 text-xs text-slate-600">Тело: <code>{"{ \"orders\": [ ... ] }"}</code></p>
			<textarea
				class="mt-2 w-full rounded-md border-slate-300 font-mono text-xs"
				rows="8"
				bind:value={pushJson}
			></textarea>
			<button
				type="button"
				class="mt-3 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
				disabled={pending}
				onclick={() => pushOrders()}>Отправить</button
			>
		</div>
	</section>
</div>
