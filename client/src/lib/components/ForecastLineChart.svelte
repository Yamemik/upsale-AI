<script lang="ts">
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

	let {
		labels,
		values,
		title = 'Прогноз',
		height = 280
	}: {
		labels: string[];
		values: number[];
		title?: string;
		height?: number;
	} = $props();

	let canvas = $state<HTMLCanvasElement | null>(null);

	$effect(() => {
		const el = canvas;
		if (!el || labels.length === 0 || values.length === 0) return;

		const instance = new Chart(el, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label: title,
						data: values,
						borderColor: 'rgb(15 23 42)',
						backgroundColor: 'rgba(15, 23, 42, 0.06)',
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
					y: { beginAtZero: true }
				},
				plugins: {
					legend: { display: true }
				}
			}
		});

		return () => {
			instance.destroy();
		};
	});
</script>

<div class="relative w-full rounded-lg border border-slate-100 bg-white p-2" style:height="{height}px">
	<canvas bind:this={canvas} class="!h-full !w-full max-h-full"></canvas>
</div>
