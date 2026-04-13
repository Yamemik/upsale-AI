<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import ActualVsForecastChart from '$lib/components/ActualVsForecastChart.svelte';
	import { apiFetch } from '$lib/api/client';
	import { formatApiError } from '$lib/api/errors';
	import type { ForecastResult, Sale } from '$lib/api/types';

	let sales = $state<Sale[]>([]);
	let history = $state<ForecastResult[]>([]);
	let loadErr = $state<string | null>(null);
	let loading = $state(true);

	let dateFrom = $state('');
	let dateTo = $state('');
	let productFilter = $state('');
	let warehouseFilter = $state('');

	const products = $derived.by(() => {
		const set = new Map<string, string>();
		for (const s of sales) set.set(s.product_id, s.product_name);
		return [...set.entries()].sort((a, b) => a[1].localeCompare(b[1]));
	});

	const warehouses = $derived.by(() => {
		const set = new Set<string>();
		for (const s of sales) set.add(s.warehouse_id);
		return [...set].sort();
	});

	const filteredSales = $derived.by(() =>
		sales.filter((s) => {
			if (dateFrom && s.sale_date < dateFrom) return false;
			if (dateTo && s.sale_date > dateTo) return false;
			if (productFilter && s.product_id !== productFilter) return false;
			if (warehouseFilter && s.warehouse_id !== warehouseFilter) return false;
			return true;
		})
	);

	const totalRevenue = $derived.by(() => filteredSales.reduce((a, s) => a + Number(s.revenue), 0));
	const totalUnits = $derived.by(() => filteredSales.reduce((a, s) => a + Number(s.quantity), 0));

	const matchingForecast = $derived.by(() => {
		if (!productFilter) return history[0] ?? null;
		return history.find((h) => String(h.product_id) === productFilter) ?? history[0] ?? null;
	});

	const forecastNextSum = $derived.by(() => {
		const f = matchingForecast?.forecast ?? [];
		if (f.length === 0) return null;
		return f.reduce((a, p) => a + Number(p.predicted_sales), 0);
	});

	const mapeDisplay = $derived.by(() => '—');

	const actualByDate = $derived.by(() => {
		const map = new Map<string, number>();
		for (const s of filteredSales) {
			const d = s.sale_date;
			map.set(d, (map.get(d) ?? 0) + Number(s.quantity));
		}
		return [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
	});

	const chartBundle = $derived.by(() => {
		const fc = matchingForecast?.forecast ?? [];
		const dateSet = new Set<string>();
		for (const [d] of actualByDate) dateSet.add(d);
		for (const p of fc) dateSet.add(p.date);
		const labels = [...dateSet].sort((a, b) => a.localeCompare(b));

		const actualMap = new Map(actualByDate);
		const fcMap = new Map(fc.map((p) => [p.date, Number(p.predicted_sales)] as const));

		const actual: (number | null)[] = labels.map((d) => actualMap.get(d) ?? null);
		const forecast: (number | null)[] = labels.map((d) => (fcMap.has(d) ? fcMap.get(d)! : null));
		return { labels, actual, forecast };
	});

	const recommendations = $derived.by(() => {
		const rows: { product: string; stock: number; demand: number; text: string }[] = [];
		const byProduct = new Map<string, { name: string; qty: number }>();
		for (const s of filteredSales) {
			const cur = byProduct.get(s.product_id) ?? { name: s.product_name, qty: 0 };
			cur.qty += Number(s.quantity);
			byProduct.set(s.product_id, cur);
		}
		for (const [pid, { name, qty }] of byProduct) {
			const h = history.find((x) => String(x.product_id) === pid);
			const demand = h?.forecast?.reduce((a, p) => a + Number(p.predicted_sales), 0) ?? qty * 1.08;
			const suggested = h?.suggested_order_quantity ?? Math.max(0, Math.round(demand * 0.15));
			rows.push({
				product: name,
				stock: Math.round(qty * 0.2),
				demand: Math.round(demand),
				text: suggested > 0 ? `заказать ${suggested} ед.` : 'заказ не нужен'
			});
		}
		return rows.slice(0, 12);
	});

	async function load() {
		loadErr = null;
		loading = true;
		try {
			const [s, h] = await Promise.all([
				apiFetch<Sale[]>('/sales'),
				apiFetch<ForecastResult[]>('/forecast/history')
			]);
			sales = s;
			history = h;
		} catch (e) {
			loadErr = formatApiError(e);
			sales = [];
			history = [];
		} finally {
			loading = false;
		}
	}

	onMount(() => void load());
</script>

<div class="space-y-8">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<h1 class="text-2xl font-semibold text-white">Сводка</h1>
			<p class="mt-1 text-sm text-slate-400">Показатели, факт и прогноз, рекомендации</p>
		</div>
		<button type="button" class="ds-btn-ghost border border-slate-600 px-4 py-2 text-sm" onclick={() => load()}>
			Обновить
		</button>
	</div>

	{#if loadErr}
		<Alert variant="error">{loadErr}</Alert>
	{/if}

	<div class="ds-card ds-card-hover flex flex-wrap items-end gap-4 p-4 sm:p-5">
		<div>
			<label class="text-xs font-medium text-slate-500" for="df">Дата с</label>
			<input id="df" type="date" class="ds-input mt-1 w-auto min-w-[10rem]" bind:value={dateFrom} />
		</div>
		<div>
			<label class="text-xs font-medium text-slate-500" for="dt">Дата по</label>
			<input id="dt" type="date" class="ds-input mt-1 w-auto min-w-[10rem]" bind:value={dateTo} />
		</div>
		<div class="min-w-[12rem] flex-1">
			<label class="text-xs font-medium text-slate-500" for="pf">Товар</label>
			<select id="pf" class="ds-input mt-1" bind:value={productFilter}>
				<option value="">Все товары</option>
				{#each products as [id, name] (id)}
					<option value={id}>{name}</option>
				{/each}
			</select>
		</div>
		<div class="min-w-[10rem] flex-1">
			<label class="text-xs font-medium text-slate-500" for="wf">Склад</label>
			<select id="wf" class="ds-input mt-1" bind:value={warehouseFilter}>
				<option value="">Все склады</option>
				{#each warehouses as w (w)}
					<option value={w}>{w}</option>
				{/each}
			</select>
		</div>
	</div>

	{#if loading}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			{#each Array(4) as _, i (i)}
				<div class="ds-card h-28 animate-pulse bg-slate-800/50 p-4">
					<div class="ds-skeleton h-3 w-20"></div>
					<div class="ds-skeleton mt-4 h-8 w-28"></div>
				</div>
			{/each}
		</div>
		<div class="ds-skeleton h-[320px] w-full rounded-xl"></div>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
			<div class="ds-card ds-card-hover p-5">
				<p class="text-xs font-medium uppercase tracking-wide text-slate-500">Выручка</p>
				<p class="ds-kpi-value mt-2">{totalRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
			</div>
			<div class="ds-card ds-card-hover p-5">
				<p class="text-xs font-medium uppercase tracking-wide text-slate-500">Продано единиц</p>
				<p class="ds-kpi-value mt-2">{totalUnits.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
			</div>
			<div class="ds-card ds-card-hover p-5">
				<p class="text-xs font-medium uppercase tracking-wide text-slate-500">Прогноз (след. период)</p>
				<p class="ds-kpi-value mt-2 text-emerald-400">
					{forecastNextSum != null
						? forecastNextSum.toLocaleString(undefined, { maximumFractionDigits: 1 })
						: '—'}
				</p>
			</div>
			<div class="ds-card ds-card-hover p-5">
				<p class="text-xs font-medium uppercase tracking-wide text-slate-500">Ошибка модели (MAPE)</p>
				<p class="ds-kpi-value mt-2 text-amber-400">{mapeDisplay}</p>
			</div>
		</div>

		{#if chartBundle.labels.length > 0}
			<ActualVsForecastChart
				labels={chartBundle.labels}
				actual={chartBundle.actual}
				forecast={chartBundle.forecast}
			/>
		{:else}
			<div class="ds-card flex h-[200px] items-center justify-center text-sm text-slate-500">
				Нет данных для графика при текущих фильтрах
			</div>
		{/if}
	{/if}

	<section class="overflow-x-auto ds-card">
		<div class="border-b border-slate-700 px-4 py-3">
			<h2 class="font-medium text-slate-100">Рекомендации</h2>
			<p class="text-xs text-slate-500">На основе истории прогнозов и отфильтрованных продаж (иллюстративно)</p>
		</div>
		<table class="min-w-full text-left text-sm">
			<thead class="ds-table-head">
				<tr>
					<th class="px-4 py-2">Товар</th>
					<th class="px-4 py-2 text-right">Текущий остаток</th>
					<th class="px-4 py-2 text-right">Прогноз спроса</th>
					<th class="px-4 py-2">Рекомендация</th>
				</tr>
			</thead>
			<tbody>
				{#each recommendations as r (r.product)}
					<tr class="ds-table-row">
						<td class="px-4 py-2 text-slate-200">{r.product}</td>
						<td class="px-4 py-2 text-right font-mono text-slate-300">{r.stock}</td>
						<td class="px-4 py-2 text-right font-mono text-slate-300">{r.demand}</td>
						<td class="px-4 py-2 text-slate-300">{r.text}</td>
					</tr>
				{:else}
					<tr>
						<td colspan="4" class="px-4 py-8 text-center text-slate-500">Нет строк</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</section>

	<section class="overflow-x-auto ds-card">
		<div class="border-b border-slate-700 px-4 py-3">
			<h2 class="font-medium text-slate-100">Продажи</h2>
			<p class="text-xs text-slate-500">Отфильтрованный список (до 200 строк)</p>
		</div>
		<table class="min-w-full text-left text-sm">
			<thead class="ds-table-head">
				<tr>
					<th class="px-4 py-2">Дата</th>
					<th class="px-4 py-2">Товар</th>
					<th class="px-4 py-2 text-right">Количество</th>
					<th class="px-4 py-2 text-right">Цена</th>
					<th class="px-4 py-2 text-right">Выручка</th>
				</tr>
			</thead>
			<tbody>
				{#each filteredSales.slice(0, 200) as s (s.id)}
					<tr class="ds-table-row">
						<td class="px-4 py-2 whitespace-nowrap text-slate-300">{s.sale_date}</td>
						<td class="px-4 py-2 text-slate-200">{s.product_name}</td>
						<td class="px-4 py-2 text-right font-mono text-slate-300">{s.quantity}</td>
						<td class="px-4 py-2 text-right font-mono text-slate-300">{s.price}</td>
						<td class="px-4 py-2 text-right font-mono text-slate-300">{s.revenue}</td>
					</tr>
				{:else}
					<tr>
						<td colspan="5" class="px-4 py-8 text-center text-slate-500">Нет продаж</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if filteredSales.length > 200}
			<p class="border-t border-slate-700 px-4 py-2 text-xs text-slate-500">
				Показано 200 из {filteredSales.length}
			</p>
		{/if}
	</section>
</div>
