/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        wine: {
          deep: '#58111A',
          burgundy: '#72222D',
          hover: '#661922',
          tint: '#F9EFF1',
          light: '#F4E4E7',
        },
        sand: {
          canvas: '#F8F6F0',
          surface: '#FCFAF7',
          card: '#FFFFFF',
          border: '#E8E2D5',
          muted: '#D6CEBF',
          accent: '#EDE7DC',
        },
        ink: {
          charcoal: '#231F20',
          muted: '#69615E',
          subtle: '#8C827D',
        },
        status: {
          success: '#2D6A4F',
          warning: '#B57614',
          error: '#9E2A2B',
          info: '#2C5282',
        }
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'wine-sm': '0 4px 20px -2px rgba(88, 17, 26, 0.05)',
        'wine-md': '0 10px 30px -10px rgba(88, 17, 26, 0.08)',
        'wine-lg': '0 20px 40px -15px rgba(88, 17, 26, 0.14)',
        'wine-glow': '0 0 25px rgba(88, 17, 26, 0.25)',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.25rem',
        '3xl': '1.75rem',
      }
    },
  },
  plugins: [],
}
