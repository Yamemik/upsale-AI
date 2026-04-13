<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch } from '$lib/api/client';
	import { formatApiError } from '$lib/api/errors';
	import type { UserMe } from '$lib/api/types';
	import { auth, refreshCurrentUser } from '$lib/auth.svelte';

	let login = $state('');
	let name = $state('');
	let surname = $state('');
	let patr = $state('');
	let password = $state('');
	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);

	$effect(() => {
		if (!browser || auth.authLoading) return;
		if (!auth.currentUser) {
			void goto('/login');
			return;
		}
		login = auth.currentUser.login;
		name = auth.currentUser.name ?? '';
		surname = auth.currentUser.surname ?? '';
		patr = auth.currentUser.patr ?? '';
	});

	async function onsubmit(e: Event) {
		e.preventDefault();
		if (!auth.currentUser) return;
		err = null;
		ok = null;
		pending = true;
		try {
			const body: Record<string, unknown> = {
				login: login.trim(),
				name: name.trim() || null,
				surname: surname.trim() || null,
				patr: patr.trim() || null
			};
			if (password.trim()) body.password = password.trim();
			await apiFetch<UserMe>('/users/me', { method: 'PUT', json: body });
			password = '';
			ok = 'Сохранено';
			await refreshCurrentUser();
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

{#if !auth.currentUser}
	<p class="text-slate-400">Перенаправление на вход…</p>
{:else}
	<div class="mx-auto max-w-lg space-y-6">
		<h1 class="text-2xl font-semibold text-white">Профиль</h1>
		<p class="text-sm text-slate-400">
			ID: {auth.currentUser.id} · администратор: {auth.currentUser.is_admin ? 'да' : 'нет'}
		</p>
		{#if err}
			<Alert variant="error">{err}</Alert>
		{/if}
		{#if ok}
			<Alert variant="success">{ok}</Alert>
		{/if}
		<form class="ds-card space-y-4 p-6" onsubmit={onsubmit}>
			<div>
				<label class="block text-sm font-medium text-slate-300" for="acc-login">Логин</label>
				<input id="acc-login" class="ds-input" bind:value={login} required />
			</div>
			<div class="grid gap-4 sm:grid-cols-3">
				<div>
					<label class="block text-sm font-medium text-slate-300" for="acc-sur">Фамилия</label>
					<input id="acc-sur" class="ds-input" bind:value={surname} />
				</div>
				<div>
					<label class="block text-sm font-medium text-slate-300" for="acc-name">Имя</label>
					<input id="acc-name" class="ds-input" bind:value={name} />
				</div>
				<div>
					<label class="block text-sm font-medium text-slate-300" for="acc-patr">Отчество</label>
					<input id="acc-patr" class="ds-input" bind:value={patr} />
				</div>
			</div>
			<div>
				<label class="block text-sm font-medium text-slate-300" for="acc-pass">Новый пароль</label>
				<input
					id="acc-pass"
					type="password"
					class="ds-input"
					bind:value={password}
					placeholder="оставьте пустым, чтобы не менять"
				/>
			</div>
			<button type="submit" class="ds-btn-primary" disabled={pending}
				>{pending ? 'Сохранение…' : 'Сохранить'}</button
			>
		</form>
	</div>
{/if}
