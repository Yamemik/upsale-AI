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
		error: 'border-red-200 bg-red-50 text-red-900',
		success: 'border-emerald-200 bg-emerald-50 text-emerald-900',
		info: 'border-slate-200 bg-slate-50 text-slate-800'
	};
</script>

<div
	class="rounded-lg border px-4 py-3 text-sm {styles[variant]}"
	role="alert"
>
	{@render children?.()}
</div>
