<script lang="ts">
	import { browser } from '$app/environment';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { auth, refreshCurrentUser } from '$lib/auth.svelte';

	let { children } = $props();
	let checked = $state(false);

	onMount(async () => {
		await refreshCurrentUser();
		checked = true;
		if (!auth.currentUser) {
			await goto('/login');
		}
	});

	$effect(() => {
		if (!browser || !checked || auth.authLoading) return;
		if (!auth.currentUser) {
			void goto('/login');
		}
	});
</script>

{#if !checked || auth.authLoading}
	<div class="flex flex-col items-center gap-3 py-16">
		<div class="h-3 w-40 animate-pulse rounded-full bg-slate-700"></div>
		<p class="text-center text-sm text-slate-400">Проверка доступа…</p>
	</div>
{:else if auth.currentUser}
	{@render children()}
{:else}
	<p class="text-center text-sm text-slate-400">Перенаправление на вход…</p>
{/if}
