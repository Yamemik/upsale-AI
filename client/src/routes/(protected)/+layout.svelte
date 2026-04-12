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
	<p class="text-center text-slate-600">Проверка доступа…</p>
{:else if auth.currentUser}
	{@render children()}
{:else}
	<p class="text-center text-slate-600">Перенаправление на вход…</p>
{/if}
