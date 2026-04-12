<script lang="ts">
	import { onMount } from 'svelte';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch, apiUrl } from '$lib/api/client';
	import { ACCESS_TOKEN_KEY } from '$lib/constants';
	import { formatApiError } from '$lib/api/errors';
	import type { Sale, SaleCsvImportResult } from '$lib/api/types';

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

	let importFormat = $state<'auto' | 'kaggle' | 'legacy'>('auto');
	let fileInput = $state<HTMLInputElement | undefined>(undefined);

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

	async function importCsv() {
		err = null;
		ok = null;
		const input = fileInput;
		const file = input?.files?.[0];
		if (!file) {
			err = 'Выберите CSV файл';
			return;
		}
		pending = true;
		try {
			const fd = new FormData();
			fd.append('file', file);
			const token = typeof localStorage !== 'undefined' ? localStorage.getItem(ACCESS_TOKEN_KEY) : null;
			const headers = new Headers();
			if (token) headers.set('Authorization', `Bearer ${token}`);
			const q = new URLSearchParams({ import_format: importFormat });
			const res = await fetch(apiUrl(`/api/v1/sales/import/csv?${q}`), {
				method: 'POST',
				body: fd,
				headers
			});
			if (!res.ok) {
				const body = await res.json().catch(() => ({}));
				throw { detail: body.detail ?? res.statusText, status: res.status };
			}
			const data = (await res.json()) as SaleCsvImportResult;
			ok = `Импорт: ${data.imported} добавлено, ${data.skipped} пропущено${
				data.format_detected ? `, формат: ${data.format_detected}` : ''
			}`;
			if (data.errors?.length) ok += `. Ошибки: ${data.errors.slice(0, 5).join('; ')}`;
			await load();
			if (input) input.value = '';
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
			<h1 class="text-2xl font-bold text-slate-900">Продажи</h1>
			<p class="text-sm text-slate-600">GET/POST <code class="text-xs">/api/v1/sales</code>, импорт CSV</p>
		</div>
		<button
			type="button"
			class="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium hover:bg-slate-50"
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

	<div class="grid gap-8 lg:grid-cols-2">
		<section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
			<h2 class="font-semibold text-slate-900">Новая продажа</h2>
			<form class="mt-4 grid gap-3 sm:grid-cols-2" onsubmit={createSale}>
				<div class="sm:col-span-2">
					<label class="text-xs font-medium text-slate-600" for="p-id">product_id</label>
					<input id="p-id" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={product_id} required />
				</div>
				<div class="sm:col-span-2">
					<label class="text-xs font-medium text-slate-600" for="p-name">product_name</label>
					<input id="p-name" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={product_name} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-cat">category</label>
					<input id="p-cat" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={category} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-wh">warehouse_id</label>
					<input id="p-wh" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={warehouse_id} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-date">sale_date</label>
					<input id="p-date" type="date" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={sale_date} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-qty">quantity</label>
					<input id="p-qty" type="number" step="any" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={quantity} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-price">price</label>
					<input id="p-price" type="number" step="any" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={price} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="p-rev">revenue</label>
					<input id="p-rev" type="number" step="any" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={revenue} required />
				</div>
				<div class="sm:col-span-2">
					<button
						type="submit"
						class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
						disabled={pending}>Сохранить</button
					>
				</div>
			</form>
		</section>

		<section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
			<h2 class="font-semibold text-slate-900">Импорт CSV</h2>
			<p class="mt-1 text-xs text-slate-600">POST <code>/api/v1/sales/import/csv</code></p>
			<div class="mt-4 space-y-3">
				<div>
					<label class="text-xs font-medium text-slate-600" for="fmt">Формат</label>
					<select id="fmt" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={importFormat}>
						<option value="auto">auto</option>
						<option value="kaggle">kaggle</option>
						<option value="legacy">legacy</option>
					</select>
				</div>
				<input bind:this={fileInput} type="file" accept=".csv,text/csv" class="block w-full text-sm" />
				<button
					type="button"
					class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
					disabled={pending}
					onclick={() => importCsv()}>Загрузить</button
				>
			</div>
		</section>
	</div>

	<section class="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
		<table class="min-w-full text-left text-sm">
			<thead class="border-b border-slate-200 bg-slate-50 text-xs font-medium uppercase text-slate-600">
				<tr>
					<th class="px-3 py-2">id</th>
					<th class="px-3 py-2">дата</th>
					<th class="px-3 py-2">товар</th>
					<th class="px-3 py-2">склад</th>
					<th class="px-3 py-2 text-right">qty</th>
					<th class="px-3 py-2 text-right">выручка</th>
				</tr>
			</thead>
			<tbody>
				{#each sales.slice(0, 200) as s}
					<tr class="border-b border-slate-100 hover:bg-slate-50/80">
						<td class="px-3 py-2 font-mono text-xs">{s.id}</td>
						<td class="px-3 py-2 whitespace-nowrap">{s.sale_date}</td>
						<td class="px-3 py-2">{s.product_name}</td>
						<td class="px-3 py-2 font-mono text-xs">{s.warehouse_id}</td>
						<td class="px-3 py-2 text-right">{s.quantity}</td>
						<td class="px-3 py-2 text-right">{s.revenue}</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="px-3 py-8 text-center text-slate-500">Нет данных</td>
					</tr>
				{/each}
			</tbody>
		</table>
		{#if sales.length > 200}
			<p class="border-t border-slate-200 px-3 py-2 text-xs text-slate-500">Показаны первые 200 из {sales.length}</p>
		{/if}
	</section>
</div>
