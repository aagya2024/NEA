/** @type {import('tailwindcss').Config} */
export default {
    content: ['./index.html', './src/**/*.{js,jsx}'],
    theme: {
        extend: {
            colors: {
                nea: {
                    blue: '#003893',
                    'blue-dark': '#002a6e',
                    'blue-light': '#0050c8',
                    red: '#dc2626',
                    gold: '#d4a017',
                    gray: '#f4f5f7',
                    'gray-dark': '#374151',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
            },
        },
    },
    plugins: [],
};
