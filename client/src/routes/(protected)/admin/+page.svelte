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
			void goto('/');
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

{#if auth.currentUser?.is_admin}
	<div class="space-y-8">
		<div>
			<h1 class="text-2xl font-bold text-slate-900">Админка</h1>
			<p class="mt-1 text-sm text-slate-600">Создание учётных записей (публичная регистрация отключена).</p>
		</div>

		{#if err}
			<Alert variant="error">{err}</Alert>
		{/if}
		{#if ok}
			<Alert variant="success">{ok}</Alert>
		{/if}

		<section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
			<h2 class="font-semibold text-slate-900">Новый пользователь</h2>
			<p class="mt-1 text-xs text-slate-600">POST <code>/api/v1/users</code> — только для администратора.</p>
			<form class="mt-4 grid max-w-xl gap-3" onsubmit={onsubmit}>
				<div>
					<label class="text-xs font-medium text-slate-600" for="a-login">Логин</label>
					<input id="a-login" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={login} required />
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="a-pass">Пароль</label>
					<input
						id="a-pass"
						type="password"
						class="mt-1 w-full rounded-md border-slate-300 text-sm"
						bind:value={password}
						required
						autocomplete="new-password"
					/>
				</div>
				<div>
					<label class="text-xs font-medium text-slate-600" for="a-email">Email</label>
					<input id="a-email" type="email" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={email} />
				</div>
				<div class="grid gap-3 sm:grid-cols-3">
					<div>
						<label class="text-xs font-medium text-slate-600" for="a-sur">Фамилия</label>
						<input id="a-sur" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={surname} />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-600" for="a-name">Имя</label>
						<input id="a-name" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={name} />
					</div>
					<div>
						<label class="text-xs font-medium text-slate-600" for="a-patr">Отчество</label>
						<input id="a-patr" class="mt-1 w-full rounded-md border-slate-300 text-sm" bind:value={patr} />
					</div>
				</div>
				<label class="flex items-center gap-2 text-sm text-slate-700">
					<input type="checkbox" bind:checked={is_admin} class="rounded border-slate-300" />
					Администратор
				</label>
				<button
					type="submit"
					class="w-fit rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
					disabled={pending}>{pending ? 'Создание…' : 'Создать пользователя'}</button
				>
			</form>
		</section>

		<section class="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
			<div class="border-b border-slate-200 px-4 py-3">
				<h2 class="font-semibold text-slate-900">Пользователи</h2>
			</div>
			<table class="min-w-full text-left text-sm">
				<thead class="border-b border-slate-200 bg-slate-50 text-xs font-medium uppercase text-slate-600">
					<tr>
						<th class="px-4 py-2">id</th>
						<th class="px-4 py-2">логин</th>
						<th class="px-4 py-2">имя</th>
						<th class="px-4 py-2">админ</th>
						<th class="px-4 py-2">создан</th>
					</tr>
				</thead>
				<tbody>
					{#each users as u}
						<tr class="border-b border-slate-100">
							<td class="px-4 py-2 font-mono text-xs">{u.id}</td>
							<td class="px-4 py-2">{u.login}</td>
							<td class="px-4 py-2 text-slate-600">{u.surname ?? ''} {u.name ?? ''}</td>
							<td class="px-4 py-2">{u.is_admin ? 'да' : 'нет'}</td>
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
	<p class="text-slate-600">Нет доступа.</p>
{/if}
