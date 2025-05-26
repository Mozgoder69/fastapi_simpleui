// frontend/src/global/plugins/colorUtils.ts

import tinycolor from "tinycolor2";

function getPastelTextColor(bgColor: string): string {
	const color = tinycolor(bgColor);
	const hsl = color.toHsl();
	hsl.l =
		hsl.l < 0.25 || hsl.l > 0.75
			? 1 - hsl.l
			: hsl.l < 0.5
				? hsl.l + 0.5
				: hsl.l - 0.5;
	return tinycolor(hsl).toHexString();
}

function getContrastTextColor(bgColor: string): string {
	const r = Number.parseInt(bgColor.slice(1, 3), 16);
	const g = Number.parseInt(bgColor.slice(3, 5), 16);
	const b = Number.parseInt(bgColor.slice(5, 7), 16);

	const yiq = r * 0.23 + g * 0.69 + b * 0.08;

	return yiq >= 128 ? "#000000" : "#FFFFFF";
}

export function getTextColor(bgColor: string, contrastMode = true): string {
	return contrastMode
		? getContrastTextColor(bgColor)
		: getPastelTextColor(bgColor);
}
