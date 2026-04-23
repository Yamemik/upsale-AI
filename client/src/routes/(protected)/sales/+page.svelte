<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch } from '$lib/api/client';
	import { formatApiError } from '$lib/api/errors';
	import type { Sale } from '$lib/api/types';

	let sales = $state<Sale[]>([]);
	let loadErr = $state<string | null>(null);
	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);

	let product_id = $state('');
	let product_name = $state('');
	let category = $state('');
	let warehouse_id = $state('');
	let sale_date = $state(new Date().toISOString().slice(0, 10));
	let quantity = $state(1);
	let price = $state(0);
	let revenue = $state(0);

	async function load() {
		loadErr = null;
		try {
			sales = await apiFetch<Sale[]>('/sales');
		} catch (e) {
			loadErr = formatApiError(e);
			sales = [];
		}
	}

	onMount(() => {
		void load();
	});

	async function createSale(e: Event) {
		e.preventDefault();
		err = null;
		ok = null;
		pending = true;
		try {
			await apiFetch<Sale>('/sales', {
				method: 'POST',
				json: {
					product_id: product_id.trim(),
					product_name: product_name.trim(),
					category: category.trim(),
					warehouse_id: warehouse_id.trim(),
					sale_date,
					quantity,
					price,
					revenue
				}
			});
			ok = 'Продажа добавлена';
			await load();
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}

</script>

<div class="space-y-8">
	<div class="flex flex-wrap items-end justify-between gap-4">
		<div>
			<h1 class="text-2xl font-semibold text-white">Продажи</h1>
			<p class="text-sm text-slate-400">GET/POST <code class="text-xs text-slate-500">/api/v1/sales</code>, импорт CSV</p>
		</div>
		<button
			type="button"
			class="ds-btn-ghost border border-slate-600 px-3 py-1.5 text-sm"
			onclick={() => load()}>Обновить</button
		>
	</div>

	{#if loadErr}
		<Alert variant="error">{loadErr}</Alert>
	{/if}
	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}
	{#if ok}
		<Alert variant="success">{ok}</Alert>
	{/if}

	<div class="grid gap-8">
		<section class="ds-card p-6">
			<h2 class="font-semibold text-slate-100">Новая продажа</h2>
			<form class="mt-4 grid gap-3 sm:grid-cols-2" onsubmit={createSale}>
				<div class="sm:col-span-2">
					<label class="text-xs font-medium text-slate-400" for="p-id">Код товара (product_id)</label>
					<input id="p-id" class="ds-input mt-1 text-sm" bind:value={product_id} required />
				</div>
				<div class="sm:col-span-2">
					<label class="text-xs font-medium text-slate-400" for="p-name">Наименование (product_name)</label>
					<input id="p-name" class="ds-input mt-1 text-sm" bind:value={product_name} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-cat">Категория (category)</label>
					<input id="p-cat" class="ds-input mt-1 text-sm" bind:value={category} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-wh">Код склада (warehouse_id)</label>
					<input id="p-wh" class="ds-input mt-1 text-sm" bind:value={warehouse_id} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-date">Дата продажи (sale_date)</label>
					<input id="p-date" type="date" class="ds-input mt-1 text-sm" bind:value={sale_date} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-qty">Количество (quantity)</label>
					<input id="p-qty" type="number" step="any" class="ds-input mt-1 text-sm" bind:value={quantity} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-price">Цена (price)</label>
					<input id="p-price" type="number" step="any" class="ds-input mt-1 text-sm" bind:value={price} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="p-rev">Выручка (revenue)</label>
					<input id="p-rev" type="number" step="any" class="ds-input mt-1 text-sm" bind:value={revenue} required />
				</div>
				<div class="sm:col-span-2">
					<button type="submit" class="ds-btn-primary text-sm" disabled={pending}>Сохранить</button>
				</div>
			</form>
		</section>
	</div>

	<section class="ds-card overflow-x-auto">
		<table class="min-w-full text-left text-sm">
			<thead class="ds-table-head">
				<tr>
					<th class="px-3 py-2">ID</th>
					<th class="px-3 py-2">дата</th>
					<th class="px-3 py-2">товар</th>
					<th class="px-3 py-2">склад</th>
					<th class="px-3 py-2 text-right">Кол-во</th>
					<th class="px-3 py-2 text-right">выручка</th>
				</tr>
			</thead>
			<tbody>
				{#each sales.slice(0, 200) as s}
					<tr class="ds-table-row">
						<td class="px-3 py-2 font-mono text-xs text-slate-400">{s.id}</td>
						<td class="px-3 py-2 whitespace-nowrap text-slate-300">{s.sale_date}</td>
						<td class="px-3 py-2 text-slate-200">{s.product_name ?? `Товар ${s.product_id}`}</td>
						<td class="px-3 py-2 font-mono text-xs text-slate-400">{s.warehouse_id}</td>
						<td class="px-3 py-2 text-right text-slate-300">{s.quantity}</td>
						<td class="px-3 py-2 text-right text-slate-300">{s.revenue}</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="px-3 py-8 text-center text-slate-500">Нет данных</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if sales.length > 200}
			<p class="border-t border-slate-700 px-3 py-2 text-xs text-slate-500">Показаны первые 200 из {sales.length}</p>
		{/if}
	</section>
</div>
