<script lang="ts">
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

	let {
		labels,
		values,
		title = 'Прогноз',
		height = 280,
		dark = true
	}: {
		labels: string[];
		values: number[];
		title?: string;
		height?: number;
		dark?: boolean;
	} = $props();

	let canvas = $state<HTMLCanvasElement | null>(null);

	$effect(() => {
		const el = canvas;
		if (!el || labels.length === 0 || values.length === 0) return;

		const lineColor = dark ? '#3B82F6' : 'rgb(15 23 42)';
		const fillColor = dark ? 'rgba(59, 130, 246, 0.12)' : 'rgba(15, 23, 42, 0.06)';
		const grid = dark ? 'rgba(148, 163, 184, 0.12)' : 'rgba(0,0,0,0.06)';
		const tick = dark ? '#94A3B8' : '#64748B';
		const legend = dark ? '#E2E8F0' : undefined;

		const instance = new Chart(el, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label: title,
						data: values,
						borderColor: lineColor,
						backgroundColor: fillColor,
						fill: true,
						tension: 0.25,
						pointRadius: 3,
						pointHoverRadius: 5
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				scales: {
					x: {
						grid: { color: grid },
						ticks: { color: tick }
					},
					y: {
						beginAtZero: true,
						grid: { color: grid },
						ticks: { color: tick }
					}
				},
				plugins: {
					legend: {
						display: true,
						labels: legend ? { color: legend } : undefined
					}
				}
			}
		});

		return () => {
			instance.destroy();
		};
	});
</script>

<div
	class="relative w-full rounded-xl border p-2 {dark
		? 'border-slate-700 bg-[#1E293B]'
		: 'border-slate-100 bg-white'}"
	style:height="{height}px"
>
	<canvas bind:this={canvas} class="!h-full !w-full max-h-full"></canvas>
</div>
