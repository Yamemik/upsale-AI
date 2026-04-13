<script lang="ts">
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

	let {
		labels,
		actual,
		forecast,
		height = 320
	}: {
		labels: string[];
		actual: (number | null)[];
		forecast: (number | null)[];
		height?: number;
	} = $props();

	let canvas = $state<HTMLCanvasElement | null>(null);

	$effect(() => {
		const el = canvas;
		if (!el || labels.length === 0) return;

		const instance = new Chart(el, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label: 'Факт',
						data: actual,
						borderColor: '#3B82F6',
						backgroundColor: 'rgba(59, 130, 246, 0.12)',
						fill: true,
						tension: 0.25,
						pointRadius: 2,
						borderWidth: 2
					},
					{
						label: 'Прогноз',
						data: forecast,
						borderColor: '#10B981',
						backgroundColor: 'rgba(16, 185, 129, 0.08)',
						fill: false,
						tension: 0.25,
						pointRadius: 2,
						borderWidth: 2,
						borderDash: [5, 5]
					}
				]
			},
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: { intersect: false, mode: 'index' },
				scales: {
					x: {
						grid: { color: 'rgba(148, 163, 184, 0.12)' },
						ticks: { color: '#94A3B8' }
					},
					y: {
						beginAtZero: true,
						grid: { color: 'rgba(148, 163, 184, 0.12)' },
						ticks: { color: '#94A3B8' }
					}
				},
				plugins: {
					legend: {
						display: true,
						labels: { color: '#E2E8F0' }
					}
				}
			}
		});

		return () => instance.destroy();
	});
</script>

<div class="ds-card ds-card-hover relative w-full overflow-hidden p-4" style:height="{height}px">
	<canvas bind:this={canvas} class="!h-full !w-full max-h-full"></canvas>
</div>
