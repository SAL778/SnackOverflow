import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import tailwindcss from "tailwindcss";

// module.exports = {
// 	root: 'src',
// 	build: {
// 	  outDir: '../dist'
// 	}
// }

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	css: {
		postcss: {
			plugins: [tailwindcss()],
		},
	},
	build: {
		outDir: 'dist', // Specify the output directory here
		assetsDir: './static' // Specify that assets should be directly outputted to outDir
	  }
});


