<script lang="ts">
	type Variant = 'error' | 'success' | 'info';

	let {
		variant = 'info',
		children
	}: {
		variant?: Variant;
		children?: import('svelte').Snippet;
	} = $props();

	const styles: Record<Variant, string> = {
		error: 'border-red-500/40 bg-red-950/40 text-red-200',
		success: 'border-emerald-500/40 bg-emerald-950/35 text-emerald-200',
		info: 'border-slate-600 bg-slate-800/80 text-slate-200'
	};
</script>

<div class="rounded-lg border px-4 py-3 text-sm {styles[variant]}" role="alert">
	{@render children?.()}
</div>
