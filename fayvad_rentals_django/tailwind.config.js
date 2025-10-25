/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './**/templates/**/*.html',
    './accounts/templates/**/*.html',
    './dashboard/templates/**/*.html',
    './maintenance/templates/**/*.html',
    './payments/templates/**/*.html',
    './properties/templates/**/*.html',
    './tenant/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Primary brand colors from logo
        primary: {
          50: '#fef9ec',
          100: '#fbeec9',
          200: '#f7db8e',
          300: '#f3c453',
          400: '#efad28',
          500: '#c88a1c', // Main golden/amber from house
          600: '#ad6e15',
          700: '#8f5215',
          800: '#754118',
          900: '#623618',
        },
        secondary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#b9e4fe',
          300: '#7dd0fc',
          400: '#3cb8f7',
          500: '#4a9bb8', // Light blue wave
          600: '#3b7d96',
          700: '#31677a',
          800: '#2c5465',
          900: '#294756',
        },
        accent: {
          50: '#f0f7fa',
          100: '#daeaf2',
          200: '#b9d8e6',
          300: '#8abfd4',
          400: '#569fbc',
          500: '#1e4d66', // Dark blue wave
          600: '#1a4158',
          700: '#163549',
          800: '#142d3d',
          900: '#132734',
        },
        // Semantic colors for property management
        success: {
          DEFAULT: '#10b981',
          light: '#d1fae5',
          dark: '#065f46',
        },
        warning: {
          DEFAULT: '#f59e0b',
          light: '#fef3c7',
          dark: '#92400e',
        },
        danger: {
          DEFAULT: '#ef4444',
          light: '#fee2e2',
          dark: '#991b1b',
        },
        info: {
          DEFAULT: '#3b82f6',
          light: '#dbeafe',
          dark: '#1e40af',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'property-card': '0 4px 6px -1px rgba(200, 138, 28, 0.1), 0 2px 4px -1px rgba(200, 138, 28, 0.06)',
        'property-card-hover': '0 10px 15px -3px rgba(200, 138, 28, 0.2), 0 4px 6px -2px rgba(200, 138, 28, 0.1)',
      },
      borderRadius: {
        'property': '0.75rem',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #c88a1c 0%, #efad28 100%)',
        'gradient-wave': 'linear-gradient(135deg, #1e4d66 0%, #4a9bb8 100%)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
