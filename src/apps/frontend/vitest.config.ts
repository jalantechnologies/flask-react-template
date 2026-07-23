import path from 'node:path';

import { defineConfig } from 'vitest/config';

const frontendRoot = path.resolve(__dirname);

export default defineConfig({
  resolve: {
    alias: {
      frontend: frontendRoot,
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    restoreMocks: true,
    setupFiles: [path.resolve(frontendRoot, 'vitest.setup.ts')],
    include: ['**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'cobertura'],
      reportsDirectory: path.resolve(
        frontendRoot,
        '../../../output/frontend-coverage',
      ),
      include: ['src/apps/frontend/**/*.{ts,tsx}'],
      exclude: [
        '**/*.test.{ts,tsx}',
        '**/*.d.ts',
        'src/apps/frontend/index.tsx',
        '**/webpack.*.js',
        '**/vendor/**',
      ],
    },
  },
});
