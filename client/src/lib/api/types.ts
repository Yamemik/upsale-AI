export type TokenResponse = {
	access_token: string;
	token_type: string;
};

export type UserMe = {
	id: number;
	login: string;
	surname: string | null;
	name: string | null;
	patr: string | null;
	is_admin: boolean;
	created_at: string;
};

export type Sale = {
	id: number;
	product_id: number;
	product_name: string | null;
	category: string | null;
	warehouse_id: number;
	sale_date: string;
	quantity: number;
	price: number;
	revenue: number;
};

export type SaleCsvImportResult = {
	imported: number;
	skipped: number;
	errors: string[];
	format_detected: string | null;
};

export type PipelineStep = {
	id: string;
	order: number;
	title: string;
};

export type KaggleImportStep = {
	id: string;
	order: number;
	title: string;
};

export type KaggleImportStepResult = {
	step: string;
	title: string;
	rows_read: number;
	inserted: number;
	updated: number;
	skipped: number;
	errors: string[];
};

export type KaggleImportRunResult = {
	mode: 'upsert' | 'reload';
	dry_run: boolean;
	steps_requested: string[];
	steps_executed: KaggleImportStepResult[];
	totals: {
		rows_read: number;
		inserted: number;
		updated: number;
		skipped: number;
		errors: number;
	};
};

export type ForecastPoint = {
	date: string;
	predicted_sales: number;
};

export type ShapFactorContribution = {
	feature_name: string;
	feature_value: number | null;
	shap_value: number;
};

export type ForecastResult = {
	product_id: string;
	horizon: number;
	forecast: ForecastPoint[];
	suggested_order_quantity: number | null;
	model_backend: string | null;
	shap_explanation?: ShapFactorContribution[] | null;
	shap_base_value?: number | null;
};

export type TrainResult = {
	product_id: number;
	warehouse_id: number | null;
	rows_used: number;
	mape: number | null;
	rmse: number | null;
	mae: number | null;
	backend: string;
	model_path: string;
	model_version: number;
	trained_at: string;
};

export type ApiError = {
	detail: string | string[] | { msg?: string }[];
	status: number;
};
