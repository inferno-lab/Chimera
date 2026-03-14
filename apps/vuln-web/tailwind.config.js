/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        recursive: ["'Recursive'", "ui-monospace", "monospace"],
      },
      fontSize: {
        display: ['36px', '1.2'],
        heading: ['24px', '1.2'],
        subhead: ['14px', '1.2'],
        body: ['13px', '1.5'],
        label: ['12px', '1.2'],
        tag: ['11px', '1.2'],
        metric: ['32px', '1'],
        'metric-unit': ['13px', '1.2'],
        data: ['13px', '1.5'],
        code: ['13px', '1.5'],
        timestamp: ['11px', '1.2'],
        nav: ['14px', '1.2'],
        'nav-active': ['14px', '1.2'],
        link: ['10px', '1.2'],
        breadcrumb: ['10px', '1.2'],
      },
    },
  },
  plugins: [],
}
