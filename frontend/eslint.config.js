// Basic ESLint config that won't error
export default [
  {
    files: ['**/*.js', '**/*.jsx'],
    rules: {
      'no-unused-vars': 'warn',
      'no-console': 'off'
    }
  }
];