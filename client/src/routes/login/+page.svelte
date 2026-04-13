<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import Alert from '$lib/components/Alert.svelte';
	import { formatApiError } from '$lib/api/errors';
	import { auth, login } from '$lib/auth.svelte';

	let loginField = $state('');
	let password = $state('');
	let rememberMe = $state(true);
	let showPassword = $state(false);
	let err = $state<string | null>(null);
	let pending = $state(false);

	function nextPath(): string {
		const q = $page.url.searchParams.get('next');
		if (q && q.startsWith('/') && !q.startsWith('//')) return q;
		return '/dashboard';
	}

	$effect(() => {
		if (!browser || !auth.currentUser) return;
		void goto(nextPath());
	});

	async function onsubmit(e: Event) {
		e.preventDefault();
		err = null;
		pending = true;
		try {
			await login(loginField.trim(), password, rememberMe);
			await goto(nextPath());
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

<div class="mx-auto flex min-h-[60vh] max-w-md flex-col justify-center space-y-6 py-8">
	<div class="text-center">
		<h1 class="text-2xl font-semibold text-white">Вход</h1>
		<p class="mt-2 text-sm text-slate-400">Внутренняя консоль прогнозирования продаж</p>
	</div>

	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}

	<form class="ds-card space-y-4 p-6 sm:p-8" onsubmit={onsubmit}>
		<div>
			<label class="block text-sm font-medium text-slate-300" for="login">Логин</label>
			<input
				id="login"
				type="text"
				class="ds-input"
				autocomplete="username"
				bind:value={loginField}
				required
			/>
			<p class="mt-1 text-xs text-slate-500">Тот же логин, что в учётной записи (в запросе передаётся как username).</p>
		</div>
		<div>
			<label class="block text-sm font-medium text-slate-300" for="password">Пароль</label>
			<div class="relative mt-1">
				<input
					id="password"
					type={showPassword ? 'text' : 'password'}
					class="ds-input pr-24"
					autocomplete="current-password"
					bind:value={password}
					required
				/>
				<button
					type="button"
					class="absolute right-2 top-1/2 -translate-y-1/2 rounded-md px-2 py-1 text-xs font-medium text-slate-400 hover:bg-slate-800 hover:text-slate-200"
					onclick={() => (showPassword = !showPassword)}
				>
					{showPassword ? 'Скрыть' : 'Показать'}
				</button>
			</div>
		</div>
		<label class="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
			<input
				type="checkbox"
				bind:checked={rememberMe}
				class="rounded border-slate-600 bg-slate-900 text-blue-600 focus:ring-blue-500"
			/>
			Запомнить меня
		</label>
		<button type="submit" class="ds-btn-primary w-full py-2.5" disabled={pending}>
			{pending ? 'Вход…' : 'Войти'}
		</button>
	</form>

	<p class="text-center text-sm text-slate-500">
		Учётную запись выдаёт администратор в разделе «Администрирование».
	</p>
</div>
