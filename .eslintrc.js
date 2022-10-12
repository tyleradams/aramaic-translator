module.exports = {
  env: {
    browser: true,
    es2020: true,
    jquery: true,
  },
  extends: [
    'airbnb-base',
    'plugin:react/recommended'
  ],
  parserOptions: {
    ecmaVersion: 11,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  },
  rules: {
  },
  settings: {
    "import/core-modules": ["styled-jsx", "styled-jsx/css"]
  },
  plugins: [
    "react", "react-hooks"
  ]
};
