<script lang="ts">
	import './layout.css';
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { auth, logout, refreshCurrentUser } from '$lib/auth.svelte';
	import { getApiDocsUrl } from '$lib/constants';

	let { children } = $props();

	const docsUrl = getApiDocsUrl();

	onMount(() => {
		void refreshCurrentUser();
	});
</script>

<div class="ds-surface flex min-h-screen flex-col">
	<header class="ds-header">
		<div class="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
			<div class="flex min-w-0 flex-1 items-center gap-4">
				<a href="/" class="flex shrink-0 items-center gap-2 text-white" aria-label="Upsale AI">
					<img src="/logo.png" alt="Upsale AI" class="h-12 w-12 rounded-lg object-cover" />
					<span class="text-sm font-semibold tracking-wide">Upsale AI</span>
				</a>
				{#if auth.currentUser}
					<nav class="hidden flex-wrap items-center gap-1 text-sm sm:flex">
						<a
							href="/dashboard"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/dashboard')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							Сводка
						</a>
						<a
							href="/sales"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/sales')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							Продажи
						</a>
						<a
							href="/forecast"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/forecast')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							Прогноз
						</a>
						<a
							href="/integration"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/integration')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							1С
						</a>
						<a
							href="/administration"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/administration')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							Администрирование
						</a>
						<a
							href="/account"
							class="rounded-lg px-3 py-1.5 font-medium transition-colors {$page.url.pathname.startsWith('/account')
								? 'ds-btn-nav-active'
								: 'text-slate-300 hover:bg-slate-700 hover:text-white'}"
						>
							Профиль
						</a>
					</nav>
				{/if}
			</div>
			<div class="flex shrink-0 items-center gap-2">
				{#if docsUrl}
					<a
						href={docsUrl}
						target="_blank"
						rel="noreferrer"
						class="hidden rounded-lg px-2 py-1 text-xs text-slate-400 hover:text-slate-200 sm:inline"
					>
						Документация API
					</a>
				{/if}
				{#if auth.currentUser}
					<button type="button" class="ds-btn-ghost text-xs sm:text-sm" onclick={() => logout()}>
						Выйти
					</button>
				{:else if !$page.url.pathname.startsWith('/login')}
					<a href="/login" class="ds-btn-primary text-sm">Войти</a>
				{/if}
			</div>
		</div>
		{#if auth.currentUser}
			<div class="border-t border-slate-700/60 px-4 py-2 sm:hidden">
				<nav class="flex flex-wrap gap-1 text-xs">
					<a href="/dashboard" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/dashboard') ? 'bg-blue-600 text-white' : 'text-slate-300'}">Сводка</a>
					<a href="/sales" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/sales') ? 'bg-blue-600 text-white' : 'text-slate-300'}">Продажи</a>
					<a href="/forecast" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/forecast') ? 'bg-blue-600 text-white' : 'text-slate-300'}">Прогноз</a>
					<a href="/integration" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/integration') ? 'bg-blue-600 text-white' : 'text-slate-300'}">1С</a>
					<a href="/administration" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/administration') ? 'bg-blue-600 text-white' : 'text-slate-300'}">Админ</a>
					<a href="/account" class="rounded-md px-2 py-1 {$page.url.pathname.startsWith('/account') ? 'bg-blue-600 text-white' : 'text-slate-300'}">Профиль</a>
				</nav>
			</div>
		{/if}
	</header>

	<main class="mx-auto w-full max-w-7xl flex-1 px-4 py-6 sm:px-6 lg:px-8">
		{@render children()}
	</main>
</div>
