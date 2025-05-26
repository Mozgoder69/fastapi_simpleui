// frontend/src/core/hooks/ui/useViewLoader.ts

import { useErrorHandler } from "@/core/hooks/useErrorHandler";

const mapView = {
	TableView: () => import("@/ui/templates/TableView.vue"),
	CardView: () => import("@/ui/templates/CardView.vue"),
	FormView: () => import("@/ui/templates/FormView.vue"),
	WizardView: () => import("@/ui/templates/WizardView.vue"),
};

export function useViewLoader() {
	return {
		loadView: useErrorHandler(
			async (name: string) => (await mapView[name]())?.default,
			"Load View",
		),
	};
}
