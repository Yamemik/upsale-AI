<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { auth } from '$lib/auth.svelte';
	import LandingMockChart from '$lib/components/LandingMockChart.svelte';

	$effect(() => {
		if (!browser || !auth.currentUser) return;
		void goto('/dashboard');
	});
</script>

<div class="space-y-16 pb-12">
	<section class="grid items-center gap-10 lg:grid-cols-2 lg:gap-12">
		<div class="space-y-6">
			<h1 class="text-3xl font-semibold tracking-tight text-white sm:text-4xl">Система прогнозирования продаж</h1>
			<p class="max-w-xl text-base leading-relaxed text-slate-400">
				Анализ продаж, построение прогнозов и оптимизация запасов на основе машинного обучения
			</p>
			<div class="flex flex-wrap gap-3">
				<a href="/login" class="ds-btn-primary px-6 py-2.5">Войти</a>
			</div>
		</div>

		<div class="ds-card ds-card-hover overflow-hidden p-5 sm:p-6">
			<p class="text-xs font-medium uppercase tracking-wide text-slate-500">Превью</p>
			<p class="mt-1 text-sm text-slate-400">Факт и прогноз (пример)</p>
			<div class="mt-4">
				<LandingMockChart />
			</div>
			<div class="mt-5 grid grid-cols-3 gap-3">
				<div class="rounded-lg border border-slate-700/80 bg-slate-900/40 px-3 py-3 transition-colors hover:border-slate-600">
					<p class="text-[10px] font-medium uppercase tracking-wide text-slate-500">Выручка</p>
					<p class="ds-kpi-value mt-1 text-lg">128 тыс.</p>
				</div>
				<div class="rounded-lg border border-slate-700/80 bg-slate-900/40 px-3 py-3 transition-colors hover:border-slate-600">
					<p class="text-[10px] font-medium uppercase tracking-wide text-slate-500">Продажи</p>
					<p class="ds-kpi-value mt-1 text-lg">4,2 тыс.</p>
				</div>
				<div class="rounded-lg border border-slate-700/80 bg-slate-900/40 px-3 py-3 transition-colors hover:border-slate-600">
					<p class="text-[10px] font-medium uppercase tracking-wide text-slate-500">Прогноз</p>
					<p class="ds-kpi-value mt-1 text-lg text-emerald-400">+6%</p>
				</div>
			</div>
		</div>
	</section>

	<section>
		<h2 class="text-sm font-medium uppercase tracking-wide text-slate-500">Возможности</h2>
		<ul class="mt-6 grid gap-4 sm:grid-cols-3">
			<li class="ds-card ds-card-hover px-5 py-4">
				<h3 class="font-medium text-slate-100">Прогноз спроса</h3>
				<p class="mt-2 text-sm text-slate-400">
					Кривые спроса и горизонт прогноза на основе ML по вашей истории продаж.
				</p>
			</li>
			<li class="ds-card ds-card-hover px-5 py-4">
				<h3 class="font-medium text-slate-100">Оптимизация запасов</h3>
				<p class="mt-2 text-sm text-slate-400">
					Уровни остатков с учётом прогноза спроса и сроков поставки.
				</p>
			</li>
			<li class="ds-card ds-card-hover px-5 py-4">
				<h3 class="font-medium text-slate-100">Интеграция с 1С</h3>
				<p class="mt-2 text-sm text-slate-400">Обмен данными с 1С для операционных процессов.</p>
			</li>
		</ul>
	</section>

	<section class="ds-card border-dashed border-slate-600/80 px-5 py-4 sm:px-6">
		<p class="text-sm text-slate-400">
			После входа: <a class="font-medium text-blue-400 hover:text-blue-300" href="/dashboard">Сводка</a>,
			<a class="font-medium text-blue-400 hover:text-blue-300" href="/sales">Продажи</a>,
			<a class="font-medium text-blue-400 hover:text-blue-300" href="/forecast">Прогноз</a>,
			<a class="font-medium text-blue-400 hover:text-blue-300" href="/integration">1С</a>,
			<a class="font-medium text-blue-400 hover:text-blue-300" href="/administration">Администрирование</a>,
			<a class="font-medium text-blue-400 hover:text-blue-300" href="/account">Профиль</a>.
			Регистрация недоступна — учётные записи создаёт администратор.
		</p>
	</section>
</div>
