<script lang="ts">
	import { auth } from '$lib/auth.svelte';
</script>

<div class="space-y-8">
	<div>
		<h1 class="text-3xl font-bold tracking-tight text-slate-900">Upsale AI</h1>
		<p class="mt-2 max-w-2xl text-slate-600">
			Продажи, прогноз спроса (LightGBM/CatBoost) с графиками и SHAP-объяснениями, интеграция с 1С. Эта страница доступна без входа;
			остальные разделы — после авторизации.
		</p>
	</div>

	<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
		{#if auth.currentUser}
			<a
				href="/sales"
				class="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
			>
				<h2 class="font-semibold text-slate-900 group-hover:text-slate-950">Продажи</h2>
				<p class="mt-2 text-sm text-slate-600">Список, ручной ввод и импорт CSV (Kaggle / legacy).</p>
			</a>
			<a
				href="/forecast"
				class="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
			>
				<h2 class="font-semibold text-slate-900 group-hover:text-slate-950">Прогноз</h2>
				<p class="mt-2 text-sm text-slate-600">Обучение, графики прогноза и факторы SHAP.</p>
			</a>
			<a
				href="/integration"
				class="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-slate-300 hover:shadow"
			>
				<h2 class="font-semibold text-slate-900 group-hover:text-slate-950">1С</h2>
				<p class="mt-2 text-sm text-slate-600">Синхронизация, выгрузка Kaggle ZIP, push заказов.</p>
			</a>
		{:else}
			<div class="rounded-xl border border-dashed border-slate-300 bg-slate-50/80 p-5 sm:col-span-2 lg:col-span-3">
				<p class="text-sm text-slate-700">
					<a href="/login" class="font-medium text-slate-900 underline">Войдите</a>
					, чтобы открыть продажи, прогнозы и интеграцию с 1С. Регистрация недоступна — пользователей создаёт
					администратор.
				</p>
			</div>
		{/if}
	</div>
</div>
