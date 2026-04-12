<script lang="ts">
	import { goto } from '$app/navigation';
	import Alert from '$lib/components/Alert.svelte';
	import { formatApiError } from '$lib/api/errors';
	import { login } from '$lib/auth.svelte';

	let username = $state('');
	let password = $state('');
	let err = $state<string | null>(null);
	let pending = $state(false);

	async function onsubmit(e: Event) {
		e.preventDefault();
		err = null;
		pending = true;
		try {
			await login(username.trim(), password);
			await goto('/');
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

<div class="mx-auto max-w-md space-y-6">
	<h1 class="text-2xl font-bold text-slate-900">Вход</h1>
	{#if err}
		<Alert variant="error">{err}</Alert>
	{/if}
	<form class="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm" onsubmit={onsubmit}>
		<div>
			<label class="block text-sm font-medium text-slate-700" for="login">Логин</label>
			<input
				id="login"
				class="mt-1 block w-full rounded-md border-slate-300 shadow-sm"
				autocomplete="username"
				bind:value={username}
				required
			/>
		</div>
		<div>
			<label class="block text-sm font-medium text-slate-700" for="password">Пароль</label>
			<input
				id="password"
				type="password"
				class="mt-1 block w-full rounded-md border-slate-300 shadow-sm"
				autocomplete="current-password"
				bind:value={password}
				required
			/>
		</div>
		<button
			type="submit"
			class="w-full rounded-md bg-slate-900 px-4 py-2 font-medium text-white hover:bg-slate-800 disabled:opacity-50"
			disabled={pending}>{pending ? 'Вход…' : 'Войти'}</button
		>
	</form>
	<p class="text-center text-sm text-slate-600">
		Учётную запись выдаёт администратор в разделе «Админка».
	</p>
</div>
