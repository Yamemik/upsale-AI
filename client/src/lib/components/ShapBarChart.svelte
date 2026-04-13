<script lang="ts">
	import { Chart, registerables } from 'chart.js';
	import type { ShapFactorContribution } from '$lib/api/types';

	Chart.register(...registerables);

	let {
		factors,
		height = 360
	}: {
		factors: ShapFactorContribution[];
		height?: number;
	} = $props();

	let canvas = $state<HTMLCanvasElement | null>(null);

	const top = $derived(factors.slice(0, 18));

	$effect(() => {
		const el = canvas;
		const rows = top;
		if (!el || rows.length === 0) return;

		const instance = new Chart(el, {
			type: 'bar',
			data: {
				labels: rows.map((r) =>
					r.feature_name.length > 28 ? `${r.feature_name.slice(0, 26)}…` : r.feature_name
				),
				datasets: [
					{
						label: 'SHAP-вклад',
						data: rows.map((r) => r.shap_value),
						backgroundColor: rows.map((r) =>
							r.shap_value >= 0 ? 'rgba(5, 150, 105, 0.75)' : 'rgba(220, 38, 38, 0.75)'
						)
					}
				]
			},
			options: {
				indexAxis: 'y',
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						title: { display: true, text: 'Влияние на прогноз (первый шаг)', color: '#94A3B8' },
						grid: { color: 'rgba(148, 163, 184, 0.12)' },
						ticks: { color: '#94A3B8' }
					},
					y: {
						grid: { color: 'rgba(148, 163, 184, 0.12)' },
						ticks: { color: '#94A3B8' }
					}
				},
				plugins: {
					legend: { display: false },
					tooltip: {
						callbacks: {
							afterLabel: (ctx) => {
								const i = ctx.dataIndex;
								const f = rows[i];
								if (!f || f.feature_value == null) return '';
								return `Значение признака: ${f.feature_value}`;
							}
						}
					}
				}
			}
		});

		return () => {
			instance.destroy();
		};
	});
</script>

{#if top.length > 0}
	<div
		class="relative w-full rounded-xl border border-slate-700 bg-[#1E293B] p-2"
		style:height="{height}px"
	>
		<canvas bind:this={canvas} class="!h-full !w-full max-h-full"></canvas>
	</div>
{:else}
	<p class="text-sm text-slate-500">Нет данных SHAP</p>
{/if}
