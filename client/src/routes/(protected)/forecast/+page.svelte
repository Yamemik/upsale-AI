<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import ForecastLineChart from '$lib/components/ForecastLineChart.svelte';
	import ShapBarChart from '$lib/components/ShapBarChart.svelte';
	import { apiFetch } from '$lib/api/client';
	import { formatApiError } from '$lib/api/errors';
	import type { ForecastResult, PipelineStep, TrainResult } from '$lib/api/types';
	import { interpretShap } from '$lib/forecast/shapInterpretation';

	let pipeline = $state<PipelineStep[]>([]);
	let history = $state<ForecastResult[]>([]);
	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);

	let lastPrediction = $state<ForecastResult | null>(null);

	let trainProductId = $state(1);
	let trainWarehouseId = $state('');

	let predProductId = $state('');
	let horizonDays = $state(7);
	let predWarehouseId = $state('');
	let leadTimeMonths = $state(1);
	let currentStock = $state('');
	let safetyStock = $state(0);

	const shapNarrative = $derived(
		lastPrediction?.shap_explanation?.length
			? interpretShap(lastPrediction.shap_base_value ?? null, lastPrediction.shap_explanation)
			: ''
	);

	const lineLabels = $derived(lastPrediction?.forecast.map((p) => p.date) ?? []);
	const lineValues = $derived(lastPrediction?.forecast.map((p) => p.predicted_sales) ?? []);

	async function loadPipeline() {
		try {
			pipeline = await apiFetch<PipelineStep[]>('/forecast/pipeline');
		} catch (e) {
			err = formatApiError(e);
		}
	}

	async function loadHistory() {
		try {
			history = await apiFetch<ForecastResult[]>('/forecast/history');
		} catch (e) {
			err = formatApiError(e);
		}
	}

	onMount(() => {
		void loadPipeline();
		void loadHistory();
	});

	async function train() {
		err = null;
		ok = null;
		pending = true;
		try {
			const body: { product_id: number; warehouse_id?: number } = { product_id: trainProductId };
			const w = trainWarehouseId.trim();
			if (w !== '') body.warehouse_id = Number(w);
			const res = await apiFetch<TrainResult>('/forecast/train', { method: 'POST', json: body });
			ok = `Обучено: строк данных: ${res.rows_used}, MAPE: ${res.mape ?? '—'}, RMSE: ${res.rmse ?? '—'}, движок: ${res.backend}`;
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}

	async function predict() {
		err = null;
		ok = null;
		pending = true;
		try {
			const body: Record<string, unknown> = {
				product_id: predProductId.trim(),
				horizon_days: horizonDays,
				lead_time_months: leadTimeMonths,
				safety_stock: safetyStock
			};
			const wh = predWarehouseId.trim();
			if (wh !== '') body.warehouse_id = wh;
			const cs = currentStock.trim();
			if (cs !== '') body.current_stock = Number(cs);
			const res = await apiFetch<ForecastResult>('/forecast/predict', { method: 'POST', json: body });
			lastPrediction = res;
			ok = `Прогноз: ${res.horizon} дн., модель: ${res.model_backend ?? '—'}, рекомендованный заказ: ${res.suggested_order_quantity ?? '—'}`;
			await loadHistory();
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

<div class="space-y-8">
	<div>
		<h1 class="text-2xl font-bold text-slate-100">Прогноз</h1>
		<p class="text-sm text-slate-400">
			Графики по дневным шагам модели; интерпретация — SHAP для первого шага прогноза.
		</p>
	</div>

	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}
	{#if ok}
		<Alert variant="success">{ok}</Alert>
	{/if}

	<section class="ds-card p-6">
		<h2 class="font-semibold text-slate-100">Конвейер</h2>
		<ol class="mt-4 list-decimal space-y-2 pl-5 text-sm text-slate-300">
			{#each pipeline as step}
				<li>
					<span class="font-mono text-xs text-slate-500">{step.id}</span>
					— {step.title}
				</li>
			{:else}
				<li class="text-slate-500">Загрузка…</li>
			{/each}
		</ol>
	</section>

	<div class="grid gap-8 lg:grid-cols-2">
		<section class="ds-card p-6">
			<h2 class="font-semibold text-slate-100">Обучение по БД</h2>
			<p class="mt-1 text-xs text-slate-400">
				POST /forecast/train — product_id (целое), warehouse_id (целое, необязательно)
			</p>
			<form
				class="mt-4 space-y-3"
				onsubmit={(e) => {
					e.preventDefault();
					void train();
				}}
			>
				<div>
					<label class="text-xs font-medium text-slate-400" for="tp">Код товара (product_id)</label>
					<input id="tp" type="number" class="mt-1 w-full ds-input text-sm" bind:value={trainProductId} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="tw">Код склада (warehouse_id)</label>
					<input id="tw" type="number" class="mt-1 w-full ds-input text-sm" bind:value={trainWarehouseId} placeholder="пусто = все" />
				</div>
				<button
					type="submit"
					class="ds-btn-primary text-sm disabled:opacity-50"
					disabled={pending}>Обучить</button
				>
			</form>
		</section>

		<section class="ds-card p-6">
			<h2 class="font-semibold text-slate-100">Прогноз</h2>
			<p class="mt-1 text-xs text-slate-400">
				<code>horizon_days</code> задаёт горизонт в днях; на графике — дневной ряд.
			</p>
			<form
				class="mt-4 space-y-3"
				onsubmit={(e) => {
					e.preventDefault();
					void predict();
				}}
			>
				<div>
					<label class="text-xs font-medium text-slate-400" for="pp">Код товара (product_id)</label>
					<input id="pp" class="mt-1 w-full ds-input text-sm" bind:value={predProductId} required />
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="text-xs font-medium text-slate-400" for="ph">Горизонт, дней (horizon_days)</label>
						<input id="ph" type="number" class="mt-1 w-full ds-input text-sm" bind:value={horizonDays} required />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-400" for="pw">Код склада (warehouse_id)</label>
						<input id="pw" class="mt-1 w-full ds-input text-sm" bind:value={predWarehouseId} />
					</div>
				</div>
				<div class="grid grid-cols-2 gap-3">
					<div>
						<label class="text-xs font-medium text-slate-400" for="pl">Срок поставки, мес. (lead_time_months)</label>
						<input id="pl" type="number" step="any" class="mt-1 w-full ds-input text-sm" bind:value={leadTimeMonths} />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-400" for="ps">Страховой запас (safety_stock)</label>
						<input id="ps" type="number" step="any" class="mt-1 w-full ds-input text-sm" bind:value={safetyStock} />
					</div>
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="pc">Текущий остаток (current_stock)</label>
					<input id="pc" type="number" step="any" class="mt-1 w-full ds-input text-sm" bind:value={currentStock} placeholder="опционально" />
				</div>
				<button
					type="submit"
					class="ds-btn-primary text-sm disabled:opacity-50"
					disabled={pending}>Спрогнозировать</button
				>
			</form>
		</section>
	</div>

	{#if lastPrediction && lastPrediction.forecast.length > 0}
		<section class="ds-card space-y-4 p-6">
			<h2 class="font-semibold text-slate-100">График последнего прогноза</h2>
			<p class="text-xs text-slate-400">
				Товар <span class="font-mono">{lastPrediction.product_id}</span> · шаги по дням: {lastPrediction.forecast.length}
			</p>
			{#key lastPrediction.product_id + String(lastPrediction.forecast.at(-1)?.date)}
				<ForecastLineChart
					labels={lineLabels}
					values={lineValues}
					title="Прогноз продаж (по дням)"
					height={300}
				/>
			{/key}
		</section>
	{/if}

	{#if lastPrediction?.shap_explanation?.length}
		<section class="ds-card space-y-4 p-6">
			<h2 class="font-semibold text-slate-100">Интерпретация (SHAP)</h2>
			<p class="text-sm leading-relaxed text-slate-300">{shapNarrative}</p>
			{#if lastPrediction.shap_base_value != null && Number.isFinite(lastPrediction.shap_base_value)}
				<p class="text-xs text-slate-500">
					База модели: <span class="font-mono">{lastPrediction.shap_base_value.toFixed(4)}</span> · сумма SHAP + база ≈ прогноз на
					первый день (с учётом численных погрешностей).
				</p>
			{/if}
			{#key (lastPrediction.shap_explanation ?? []).map((f) => f.feature_name + f.shap_value).join('|')}
				<ShapBarChart factors={lastPrediction.shap_explanation ?? []} height={420} />
			{/key}
			<div class="overflow-x-auto">
				<table class="min-w-full text-left text-xs">
					<thead class="border-b border-slate-700 text-slate-400">
						<tr>
							<th class="py-2 pr-4 font-medium">Признак</th>
							<th class="py-2 pr-4 font-medium">Значение</th>
							<th class="py-2 font-medium">Вклад SHAP</th>
						</tr>
					</thead>
					<tbody>
						{#each lastPrediction.shap_explanation ?? [] as row}
							<tr class="border-b border-slate-700/60">
								<td class="py-1.5 pr-4 font-mono text-slate-200">{row.feature_name}</td>
								<td class="py-1.5 pr-4 text-slate-400">{row.feature_value ?? '—'}</td>
								<td
									class="py-1.5 font-mono {row.shap_value >= 0 ? 'text-emerald-400' : 'text-red-400'}"
								>
									{row.shap_value.toFixed(4)}
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</section>
	{/if}

	<section class="space-y-4">
		<div class="flex flex-wrap items-center justify-between gap-2">
			<h2 class="font-semibold text-slate-100">История прогнозов</h2>
			<button
				type="button"
				class="ds-btn-ghost border border-slate-600 px-3 py-1 text-sm"
				onclick={() => loadHistory()}>Обновить</button
			>
		</div>
		<div class="space-y-6">
			{#each history as h}
				<article class="ds-card p-4">
					<div class="flex flex-wrap items-baseline justify-between gap-2">
						<h3 class="font-medium text-slate-100">
							Товар <span class="font-mono text-sm">{h.product_id}</span>
						</h3>
						<span class="text-xs text-slate-500">{h.model_backend ?? ''}</span>
					</div>
					<p class="mt-1 text-sm text-slate-400">
						Точек: {h.horizon} · рекомендованный заказ: {h.suggested_order_quantity ?? '—'}
					</p>
					{#if h.forecast.length > 0}
						<div class="mt-4">
							{#key h.product_id}
								<ForecastLineChart
									labels={h.forecast.map((p) => p.date)}
									values={h.forecast.map((p) => p.predicted_sales)}
									title={`Товар ${h.product_id}`}
									height={240}
								/>
							{/key}
						</div>
					{/if}
				</article>
			{:else}
				<p class="text-sm text-slate-500">Пока пусто</p>
			{/each}
		</div>
	</section>
</div>
