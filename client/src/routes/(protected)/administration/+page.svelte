<script lang="ts">
	import { goto } from '$app/navigation';
	import { browser } from '$app/environment';
	import Alert from '$lib/components/Alert.svelte';
	import { apiFetch } from '$lib/api/client';
	import { formatApiError } from '$lib/api/errors';
	import type { UserMe } from '$lib/api/types';
	import { auth } from '$lib/auth.svelte';

	let err = $state<string | null>(null);
	let ok = $state<string | null>(null);
	let pending = $state(false);
	let users = $state<UserMe[]>([]);

	let login = $state('');
	let password = $state('');
	let email = $state('');
	let name = $state('');
	let surname = $state('');
	let patr = $state('');
	let is_admin = $state(false);

	$effect(() => {
		if (!browser || auth.authLoading) return;
		if (auth.currentUser && !auth.currentUser.is_admin) {
			void goto('/dashboard');
		}
	});

	async function loadUsers() {
		try {
			users = await apiFetch<UserMe[]>('/users');
		} catch (e) {
			err = formatApiError(e);
		}
	}

	$effect(() => {
		if (!browser || auth.authLoading || !auth.currentUser?.is_admin) return;
		void loadUsers();
	});

	async function onsubmit(e: Event) {
		e.preventDefault();
		err = null;
		ok = null;
		pending = true;
		try {
			await apiFetch<UserMe>('/users', {
				method: 'POST',
				json: {
					login: login.trim(),
					password,
					email: email.trim() || null,
					name: name.trim() || null,
					surname: surname.trim() || null,
					patr: patr.trim() || null,
					is_admin
				}
			});
			ok = `Пользователь «${login.trim()}» создан. Можно войти с этим логином и паролем.`;
			login = '';
			password = '';
			email = '';
			name = '';
			surname = '';
			patr = '';
			is_admin = false;
			await loadUsers();
		} catch (e) {
			err = formatApiError(e);
		} finally {
			pending = false;
		}
	}
</script>

<svelte:head>
	<title>Администрирование — Upsale AI</title>
</svelte:head>

{#if auth.currentUser?.is_admin}
	<div class="space-y-8">
		<div>
			<h1 class="text-2xl font-semibold text-white">Администрирование</h1>
			<p class="mt-1 text-sm text-slate-400">
				Управление учётными записями: создание пользователей (публичная регистрация отключена).
			</p>
		</div>

		{#if err}
			<Alert variant="error">{err}</Alert>
		{/if}
		{#if ok}
			<Alert variant="success">{ok}</Alert>
		{/if}

		<section class="ds-card p-6">
			<h2 class="font-semibold text-slate-100">Новый пользователь</h2>
			<p class="mt-1 text-xs text-slate-400">POST <code class="text-slate-500">/api/v1/users</code> — только для администратора.</p>
			<form class="mt-4 grid max-w-xl gap-3" onsubmit={onsubmit}>
				<div>
					<label class="text-xs font-medium text-slate-400" for="a-login">Логин</label>
					<input id="a-login" class="ds-input mt-1 text-sm" bind:value={login} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="a-pass">Пароль</label>
					<input
						id="a-pass"
						type="password"
						class="ds-input mt-1 text-sm"
						bind:value={password}
						required
						autocomplete="new-password"
					/>
				</div>
				<div>
					<label class="text-xs font-medium text-slate-400" for="a-email">Эл. почта</label>
					<input id="a-email" type="email" class="ds-input mt-1 text-sm" bind:value={email} />
				</div>
				<div class="grid gap-3 sm:grid-cols-3">
					<div>
						<label class="text-xs font-medium text-slate-400" for="a-sur">Фамилия</label>
						<input id="a-sur" class="ds-input mt-1 text-sm" bind:value={surname} />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-400" for="a-name">Имя</label>
						<input id="a-name" class="ds-input mt-1 text-sm" bind:value={name} />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-400" for="a-patr">Отчество</label>
						<input id="a-patr" class="ds-input mt-1 text-sm" bind:value={patr} />
					</div>
				</div>
				<label class="flex items-center gap-2 text-sm text-slate-300">
					<input
						type="checkbox"
						bind:checked={is_admin}
						class="rounded border-slate-600 bg-slate-900 text-blue-600 focus:ring-blue-500"
					/>
					Назначить администратором
				</label>
				<button type="submit" class="ds-btn-primary w-fit text-sm" disabled={pending}
					>{pending ? 'Создание…' : 'Создать пользователя'}</button
				>
			</form>
		</section>

		<section class="ds-card overflow-x-auto">
			<div class="border-b border-slate-700 px-4 py-3">
				<h2 class="font-semibold text-slate-100">Пользователи</h2>
			</div>
			<table class="min-w-full text-left text-sm">
				<thead class="ds-table-head">
					<tr>
						<th class="px-4 py-2">ID</th>
						<th class="px-4 py-2">логин</th>
						<th class="px-4 py-2">имя</th>
						<th class="px-4 py-2">администратор</th>
						<th class="px-4 py-2">создан</th>
					</tr>
				</thead>
				<tbody>
					{#each users as u}
						<tr class="ds-table-row">
							<td class="px-4 py-2 font-mono text-xs text-slate-400">{u.id}</td>
							<td class="px-4 py-2 text-slate-200">{u.login}</td>
							<td class="px-4 py-2 text-slate-400">{u.surname ?? ''} {u.name ?? ''}</td>
							<td class="px-4 py-2 text-slate-300">{u.is_admin ? 'да' : 'нет'}</td>
							<td class="px-4 py-2 text-xs text-slate-500">{u.created_at}</td>
						</tr>
					{:else}
						<tr>
							<td colspan="5" class="px-4 py-6 text-center text-slate-500">Нет данных</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</section>
	</div>
{:else if !auth.authLoading}
	<p class="text-slate-400">Нет доступа.</p>
{/if}
