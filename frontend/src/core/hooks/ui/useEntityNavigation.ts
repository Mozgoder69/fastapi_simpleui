// frontend/src/core/hooks/ui/useEntityNavigation.ts

import { useErrorHandler } from "@/core/hooks/useErrorHandler";
import type { Dict } from "@/core/types";
import { useRouter } from "vue-router";

export function useEntityNavigation() {
	const router = useRouter();

	const navigateTo = useErrorHandler(
		async (table: string, keys: Dict | null | undefined) => {
			if (!table || !keys || !Object.keys(keys).length) {
				throw new Error("Table и keys обязательны");
			}
			await router.push({
				name: "BssEntity",
				params: { tableName: table },
				query: keys,
			});
		},
		"Navigate",
	);

	function getKeysFromRecord(record: Dict, pks: string[]): Dict | null {
		const out: Dict = {};
		for (const k of pks) {
			if (record[k] != null) out[k] = record[k];
			else return null;
		}
		return out;
	}

	return { navigateTo, getKeysFromRecord };
}
