<script lang="ts">
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

	let canvas = $state<HTMLCanvasElement | null>(null);

	const labels = ['Н1', 'Н2', 'Н3', 'Н4', 'Н5', 'Н6'];
	const actual = [42, 48, 45, 52, 49, 55];
	const forecast = [40, 46, 47, 50, 51, 53];

	$effect(() => {
		const el = canvas;
		if (!el) return;

		const instance = new Chart(el, {
			type: 'line',
			data: {
				labels,
				datasets: [
					{
						label: 'Факт',
						data: actual,
						borderColor: '#3B82F6',
						backgroundColor: 'rgba(59, 130, 246, 0.08)',
						fill: false,
						tension: 0.35,
						pointRadius: 2,
						borderWidth: 2
					},
					{
						label: 'Прогноз',
						data: forecast,
						borderColor: '#10B981',
						backgroundColor: 'rgba(16, 185, 129, 0.08)',
						fill: false,
						tension: 0.35,
						pointRadius: 2,
						borderWidth: 2,
						borderDash: [4, 4]
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
						ticks: { color: '#94A3B8', font: { size: 10 } }
					},
					y: {
						beginAtZero: true,
						grid: { color: 'rgba(148, 163, 184, 0.12)' },
						ticks: { color: '#94A3B8', font: { size: 10 } }
					}
				},
				plugins: {
					legend: {
						display: true,
						labels: { color: '#CBD5E1', boxWidth: 10, font: { size: 10 } }
					}
				}
			}
		});

		return () => instance.destroy();
	});
</script>

<div class="relative h-[200px] w-full sm:h-[220px]">
	<canvas bind:this={canvas} class="!h-full !w-full"></canvas>
</div>
