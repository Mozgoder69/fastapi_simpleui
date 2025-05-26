// frontend/src/global/plugins/vuetify.ts

import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { mdi } from "vuetify/iconsets/mdi";
import "vuetify/styles";
import { getTextColor } from "./colorUtils";

export const commonColors = {
	warn: "#ffaa00",
	fail: "#cc4444",
	fade: "#333333",
	acid: "#aaff00",
	grey: "#999999",
	link: "#aa00ff",
	glow: "#ffffff",
	pass: "#009966",
	info: "#4444cc",
};

const savedAccent = localStorage.getItem("accentColor") || commonColors.link;

export default createVuetify({
	components,
	directives,
	theme: {
		defaultTheme: "dark",
		themes: {
			light: {
				colors: {
					accent: savedAccent,
					background: commonColors.glow,
					foreground: getTextColor(commonColors.glow, true),
					...commonColors,
				},
			},
			dark: {
				colors: {
					accent: savedAccent,
					background: commonColors.fade,
					foreground: getTextColor(commonColors.fade, true),
					...commonColors,
				},
			},
		},
	},
	icons: { defaultSet: "mdi", sets: { mdi } },
});
