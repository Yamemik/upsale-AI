import type { ShapFactorContribution } from '$lib/api/types';

/** Краткая текстовая интерпретация SHAP для первого шага прогноза. */
export function interpretShap(
	base: number | null | undefined,
	factors: ShapFactorContribution[]
): string {
	if (!factors.length) return '';

	const pos = factors.filter((f) => f.shap_value > 0).slice(0, 4);
	const neg = factors.filter((f) => f.shap_value < 0).slice(0, 4);

	const parts: string[] = [];

	if (base != null && Number.isFinite(base)) {
		parts.push(
			`Базовое ожидание модели (средний уровень по обучающим данным): ${base.toFixed(4)}. От него отклоняет каждый признак на величину SHAP — сумма вкладов и базы даёт прогноз на первый шаг.`
		);
	} else {
		parts.push(
			'SHAP (SHapley Additive exPlanations) показывает вклад каждого признака в прогноз на первый месяц: положительные значения тянут прогноз вверх, отрицательные — вниз.'
		);
	}

	if (pos.length) {
		parts.push(
			`Сильнее всего повышают прогноз: ${pos.map((f) => `${humanFeatureName(f.feature_name)} (+${f.shap_value.toFixed(4)})`).join('; ')}.`
		);
	}
	if (neg.length) {
		parts.push(
			`Сильнее всего снижают: ${neg.map((f) => `${humanFeatureName(f.feature_name)} (${f.shap_value.toFixed(4)})`).join('; ')}.`
		);
	}

	return parts.join(' ');
}

function humanFeatureName(name: string): string {
	const map: Record<string, string> = {
		item_cnt_month: 'продажи за месяц (таргет/лаг)',
		shop_id: 'магазин',
		item_id: 'товар',
		category_id: 'категория',
		price: 'цена',
		promo: 'промо'
	};
	return map[name] ?? name;
}
