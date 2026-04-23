<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch, apiUrl, readStoredToken } from '$lib/api/client';
	import { INTEGRATION_API_KEY_STORAGE } from '$lib/constants';
	import { formatApiError } from '$lib/api/errors';
	import type { KaggleImportRunResult, KaggleImportStep } from '$lib/api/types';

	let apiKey = $state('');
	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);

	let lookbackDays = $state('');
	let dateFrom = $state('');

	let pushJson = $state('[\n  {}\n]');
	let importMode = $state<'upsert' | 'reload'>('upsert');
	let importDryRun = $state(false);
	let kaggleSteps = $state<KaggleImportStep[]>([]);
	let selectedSteps = $state<Record<string, boolean>>({});
	let importResult = $state<KaggleImportRunResult | null>(null);
	let importProgressText = $state<string | null>(null);

	let categoriesFileInput = $state<HTMLInputElement | undefined>(undefined);
	let itemsFileInput = $state<HTMLInputElement | undefined>(undefined);
	let shopsFileInput = $state<HTMLInputElement | undefined>(undefined);
	let salesFileInput = $state<HTMLInputElement | undefined>(undefined);
	let inventoryFileInput = $state<HTMLInputElement | undefined>(undefined);

	onMount(() => {
		apiKey = localStorage.getItem(INTEGRATION_API_KEY_STORAGE) ?? '';
		void loadKaggleSteps();
	});

	async function loadKaggleSteps() {
		try {
			kaggleSteps = await apiFetch<KaggleImportStep[]>('/sales/import/kaggle/steps');
			const next: Record<string, boolean> = {};
			for (const s of kaggleSteps) next[s.id] = true;
			selectedSteps = next;
		} catch (e) {
			err = formatApiError(e);
		}
	}

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

	function selectedStepIds(): string[] {
		return kaggleSteps.filter((s) => selectedSteps[s.id]).map((s) => s.id);
	}

	function hasFile(input?: HTMLInputElement): boolean {
		return Boolean(input?.files?.[0]);
	}

	function requiredFilesMissing(steps: string[]): string[] {
		const missing: string[] = [];
		if (steps.includes('categories') && !hasFile(categoriesFileInput)) missing.push('item_categories.csv');
		if ((steps.includes('items_ml') || steps.includes('products')) && !hasFile(itemsFileInput)) {
			missing.push('items.csv');
		}
		if (steps.includes('warehouses') && !hasFile(shopsFileInput)) missing.push('shops.csv');
		if (steps.includes('sales') && !hasFile(salesFileInput)) missing.push('sales_train.csv');
		// inventory.csv опционален: если файла нет, шаг строится расчетно из sales.
		return [...new Set(missing)];
	}

	function appendFile(fd: FormData, field: string, input?: HTMLInputElement) {
		const file = input?.files?.[0];
		if (file) fd.append(field, file);
	}

function buildAuthHeaders(): Headers {
	const headers = new Headers();
	const token = readStoredToken();
	if (token) headers.set('Authorization', `Bearer ${token}`);
	const key = apiKey.trim();
	if (key) headers.set('X-API-KEY', key);
	return headers;
}

	async function runKagglePipeline() {
		err = null;
		ok = null;
		importResult = null;
		importProgressText = null;
		pending = true;
		try {
			const steps = selectedStepIds();
			if (!steps.length) throw new Error('Выберите минимум один шаг');
			const missing = requiredFilesMissing(steps);
			if (missing.length) {
				throw new Error(`Для выбранных шагов не хватает файлов: ${missing.join(', ')}`);
			}
			importProgressText = `Загрузка запущена. Выполняются шаги: ${steps.join(', ')}`;

			const q = new URLSearchParams({
				mode: importMode,
				dry_run: importDryRun ? 'true' : 'false',
				steps: steps.join(',')
			});

			const fd = new FormData();
			appendFile(fd, 'categories_file', categoriesFileInput);
			appendFile(fd, 'items_file', itemsFileInput);
			appendFile(fd, 'shops_file', shopsFileInput);
			appendFile(fd, 'sales_file', salesFileInput);
			appendFile(fd, 'inventory_file', inventoryFileInput);

			const headers = buildAuthHeaders();

			const res = await fetch(apiUrl(`/api/v1/sales/import/kaggle/pipeline?${q.toString()}`), {
				method: 'POST',
				body: fd,
				headers
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw { detail: body.detail ?? res.statusText, status: res.status };
			}
			importResult = (await res.json()) as KaggleImportRunResult;
			ok = `Импорт завершён: +${importResult.totals.inserted}, ~${importResult.totals.updated}, пропущено ${importResult.totals.skipped}`;
		} catch (e) {
			err = formatApiError(e);
		} finally {
			importProgressText = null;
			pending = false;
		}
	}

	async function runKaggleStep(stepId: string) {
		err = null;
		ok = null;
		importResult = null;
		importProgressText = null;
		pending = true;
		try {
			const missing = requiredFilesMissing([stepId]);
			if (missing.length) {
				throw new Error(`Для шага "${stepId}" не хватает файлов: ${missing.join(', ')}`);
			}
			importProgressText = `Выполняется шаг: ${stepId}`;
			const q = new URLSearchParams({
				mode: importMode,
				dry_run: importDryRun ? 'true' : 'false'
			});
			const fd = new FormData();
			appendFile(fd, 'categories_file', categoriesFileInput);
			appendFile(fd, 'items_file', itemsFileInput);
			appendFile(fd, 'shops_file', shopsFileInput);
			appendFile(fd, 'sales_file', salesFileInput);
			appendFile(fd, 'inventory_file', inventoryFileInput);

			const headers = buildAuthHeaders();

			const res = await fetch(apiUrl(`/api/v1/sales/import/kaggle/step/${stepId}?${q.toString()}`), {
				method: 'POST',
				body: fd,
				headers
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw { detail: body.detail ?? res.statusText, status: res.status };
			}
			importResult = (await res.json()) as KaggleImportRunResult;
			ok = `Шаг "${stepId}" выполнен`;
		} catch (e) {
			err = formatApiError(e);
		} finally {
			importProgressText = null;
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
	{#if importProgressText}
		<Alert variant="info">{importProgressText}</Alert>
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

	<section class="ds-card space-y-4 p-6">
		<div class="flex flex-wrap items-end justify-between gap-3">
			<div>
				<h2 class="font-semibold text-slate-100">Импорт Kaggle CSV: оркестратор</h2>
				<p class="mt-1 text-xs text-slate-400">
					Полный прогон, отдельные шаги для отладки, частичное обновление и повторная загрузка.
				</p>
				<p class="mt-1 text-xs text-slate-500">
					Файлы CSV подготавливаются в 1С и загружаются в систему через форму ниже.
				</p>
			</div>
			<div class="flex flex-wrap gap-2">
				<select class="ds-input text-sm" bind:value={importMode}>
					<option value="upsert">Частичное обновление</option>
					<option value="reload">Повторная загрузка с очисткой</option>
				</select>
				<label
					class="inline-flex items-center gap-2 rounded-md border border-slate-700 px-3 py-2 text-xs text-slate-300"
					title="Пробный запуск: проверяет файлы и считает результат, но не сохраняет изменения в БД"
				>
					<input type="checkbox" bind:checked={importDryRun} />
					Пробный запуск без сохранения
				</label>
			</div>
		</div>
		<p class="text-xs text-slate-400">
			Режим <b>Частичное обновление</b> добавляет и обновляет только изменённые данные. Режим
			<b>Повторная загрузка с очисткой</b> сначала очищает выбранные шаги, затем загружает их заново.
		</p>

		<div class="grid gap-3 md:grid-cols-2">
			<label class="text-xs text-slate-400"
				>item_categories.csv
				<input bind:this={categoriesFileInput} type="file" accept=".csv,text/csv" class="ds-input mt-1 text-sm" />
				<span class="mt-1 block text-[11px] text-slate-500"
					>{categoriesFileInput?.files?.[0]?.name ?? 'файл не выбран'}</span
				>
			</label>
			<label class="text-xs text-slate-400"
				>items.csv
				<input bind:this={itemsFileInput} type="file" accept=".csv,text/csv" class="ds-input mt-1 text-sm" />
				<span class="mt-1 block text-[11px] text-slate-500">{itemsFileInput?.files?.[0]?.name ?? 'файл не выбран'}</span>
			</label>
			<label class="text-xs text-slate-400"
				>shops.csv
				<input bind:this={shopsFileInput} type="file" accept=".csv,text/csv" class="ds-input mt-1 text-sm" />
				<span class="mt-1 block text-[11px] text-slate-500">{shopsFileInput?.files?.[0]?.name ?? 'файл не выбран'}</span>
			</label>
			<label class="text-xs text-slate-400"
				>sales_train.csv
				<input bind:this={salesFileInput} type="file" accept=".csv,text/csv" class="ds-input mt-1 text-sm" />
				<span class="mt-1 block text-[11px] text-slate-500">{salesFileInput?.files?.[0]?.name ?? 'файл не выбран'}</span>
			</label>
			<label class="text-xs text-slate-400 md:col-span-2"
				>inventory.csv (опционально)
				<input bind:this={inventoryFileInput} type="file" accept=".csv,text/csv" class="ds-input mt-1 text-sm" />
				<span class="mt-1 block text-[11px] text-slate-500"
					>{inventoryFileInput?.files?.[0]?.name ?? 'не выбран, будет расчет из sales'}</span
				>
			</label>
		</div>

		<div class="space-y-2">
			<p class="text-xs text-slate-400">Шаги (можно выбрать под частичное обновление):</p>
			<div class="grid gap-2 sm:grid-cols-2">
				{#each kaggleSteps as s}
					<label class="inline-flex items-center gap-2 rounded-md border border-slate-700 px-3 py-2 text-sm text-slate-200">
						<input
							type="checkbox"
							checked={selectedSteps[s.id] ?? false}
							onchange={(e) => {
								const checked = (e.currentTarget as HTMLInputElement).checked;
								selectedSteps = { ...selectedSteps, [s.id]: checked };
							}}
						/>
						<span>{s.order}. {s.title}</span>
					</label>
				{/each}
			</div>
		</div>

		<div class="flex flex-wrap gap-2">
			<button type="button" class="ds-btn-primary text-sm disabled:opacity-50" disabled={pending} onclick={() => runKagglePipeline()}>
				Запустить все выбранные шаги
			</button>
			{#each kaggleSteps as s}
				<button
					type="button"
					class="ds-btn-ghost border border-slate-600 px-3 py-1.5 text-xs disabled:opacity-50"
					disabled={pending}
					onclick={() => runKaggleStep(s.id)}
				>
					Запустить только шаг: {s.id}
				</button>
			{/each}
		</div>

		{#if importResult}
			<div class="rounded-lg border border-slate-700 bg-slate-900/60 p-3 text-xs text-slate-300">
				<div class="flex flex-wrap gap-4">
					<span>rows: {importResult.totals.rows_read}</span>
					<span>inserted: {importResult.totals.inserted}</span>
					<span>updated: {importResult.totals.updated}</span>
					<span>skipped: {importResult.totals.skipped}</span>
					<span>errors: {importResult.totals.errors}</span>
				</div>
			</div>
			<div class="overflow-x-auto">
				<table class="min-w-full text-left text-xs">
					<thead class="ds-table-head">
						<tr>
							<th class="px-3 py-2">step</th>
							<th class="px-3 py-2 text-right">read</th>
							<th class="px-3 py-2 text-right">ins</th>
							<th class="px-3 py-2 text-right">upd</th>
							<th class="px-3 py-2 text-right">skip</th>
							<th class="px-3 py-2">errors</th>
						</tr>
					</thead>
					<tbody>
						{#each importResult.steps_executed as st}
							<tr class="ds-table-row">
								<td class="px-3 py-2">{st.step}</td>
								<td class="px-3 py-2 text-right">{st.rows_read}</td>
								<td class="px-3 py-2 text-right">{st.inserted}</td>
								<td class="px-3 py-2 text-right">{st.updated}</td>
								<td class="px-3 py-2 text-right">{st.skipped}</td>
								<td class="px-3 py-2 text-slate-400">{st.errors.slice(0, 2).join('; ')}</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</section>
</div>
