<script lang="ts">
	import './layout.css';
	import { page } from '$app/state';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { auth, refreshCurrentUser, logout } from '$lib/auth.svelte';

	let { children } = $props();

	const navAuthed = [
		{ href: '/sales', label: 'Продажи' },
		{ href: '/forecast', label: 'Прогноз' },
		{ href: '/integration', label: '1С' },
		{ href: '/api/docs', label: 'API' }
	];

	onMount(() => {
		void refreshCurrentUser();
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Upsale AI</title>
</svelte:head>

<div class="min-h-screen bg-slate-50 text-slate-900">
	<header class="border-b border-slate-200 bg-white">
		<div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-3">
			<a href="/" class="text-lg font-semibold tracking-tight text-slate-900">Upsale AI</a>
			<nav class="flex flex-wrap items-center gap-1">
				{#if auth.currentUser}
					{#each navAuthed as item}
						<a
							href={item.href}
							class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors {page.url.pathname ===
								item.href ||
							(item.href !== '/' && page.url.pathname.startsWith(item.href))
								? 'bg-slate-900 text-white'
								: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
						>
							{item.label}
						</a>
					{/each}
					{#if auth.currentUser.is_admin}
						<a
							href="/admin"
							class="rounded-md px-3 py-1.5 text-sm font-medium transition-colors {page.url.pathname ===
								'/admin' || page.url.pathname.startsWith('/admin/')
								? 'bg-slate-900 text-white'
								: 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'}"
						>
							Админка
						</a>
					{/if}
				{/if}
			</nav>
			<div class="flex items-center gap-3 text-sm">
				{#if auth.authLoading}
					<span class="text-slate-500">…</span>
				{:else if auth.currentUser}
					<span class="hidden text-slate-600 sm:inline">{auth.currentUser.login}</span>
					<a
						href="/account"
						class="rounded-md px-2 py-1 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
						>Профиль</a
					>
					<button
						type="button"
						class="rounded-md bg-slate-900 px-3 py-1.5 font-medium text-white hover:bg-slate-800"
						onclick={() => logout()}>Выйти</button
					>
				{:else}
					<a
						href="/login"
						class="rounded-md bg-slate-900 px-3 py-1.5 font-medium text-white hover:bg-slate-800"
						>Вход</a
					>
				{/if}
			</div>
		</div>
	</header>

	<main class="mx-auto max-w-6xl px-4 py-8">
		{@render children()}
	</main>
</div>
