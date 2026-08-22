// Run with: node .github/workflows/pr-labeler.test.js
//
// The labelling rules live inside the github-script block of pr-labeler.yml so the
// workflow itself needs no checkout. This test lifts that block out of the YAML and
// runs it against a fake `context` and `core`, so what is tested is what is deployed.

const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const workflow = fs.readFileSync(
  path.join(__dirname, 'pr-labeler.yml'),
  'utf-8',
);

const scriptStart = workflow.indexOf('script: |');
assert.notStrictEqual(scriptStart, -1, 'pr-labeler.yml has no script block');

const scriptBody = workflow
  .slice(workflow.indexOf('\n', scriptStart) + 1)
  .split('\n')
  .map((line) => line.replace(/^ {12}/, ''))
  .join('\n');

// Everything from the first API call onward needs a live GitHub client. The label
// decision is complete before that point, so only the part above it is run here.
const decisionEnd = scriptBody.indexOf('// Get existing labels on the PR');
assert.notStrictEqual(decisionEnd, -1, 'pr-labeler.yml changed shape');

const decisionScript = scriptBody.slice(0, decisionEnd);

// github-script runs the block inside an async function, which is what makes the
// early `return` after setFailed legal, so the block is wrapped the same way here.
const wrapped = `result = (function () {\n${decisionScript}\nreturn labelsToAdd;\n})();`;

function labelsFor(title) {
  const failures = [];
  const sandbox = {
    context: { payload: { pull_request: { title, number: 1 } } },
    core: { setFailed: (message) => failures.push(message) },
    console: { log: () => {} },
    result: null,
  };

  vm.createContext(sandbox);
  vm.runInContext(wrapped, sandbox);

  // The sandbox is a separate realm whose Array has a different prototype, so the
  // values are copied out before deepStrictEqual compares them.
  return { labels: Array.from(sandbox.result ?? []), failures };
}

const REJECTED = 'rejected';

const cases = [
  ['feat(api)!: drop the v1 payload', ['type: feat', 'semver: major']],
  ['feat!: drop the v1 payload', ['type: feat', 'semver: major']],
  ['feat!(api): drop the v1 payload', ['type: feat', 'semver: major']],
  ['fix(auth)!: stop returning the token', ['type: fix', 'semver: major']],
  ['fix!(auth): stop returning the token', ['type: fix', 'semver: major']],
  ['perf(logger)!: remove the transport', ['type: perf', 'semver: major']],
  ['refactor(store)!: rename the verbs', ['type: refactor', 'semver: major']],
  ['build!: require node 22', ['type: build', 'semver: major']],
  ['chore!: drop the python 3.11 target', ['type: chore', 'semver: major']],
  ['FEAT(API)!: drop the v1 payload', ['type: feat', 'semver: major']],
  ['feat(api): add a new endpoint', ['type: feat', 'semver: minor']],
  ['feat: add a new endpoint', ['type: feat', 'semver: minor']],
  ['fix(api): handle an empty body', ['type: fix', 'semver: patch']],
  ['perf(logger): batch writes', ['type: perf', 'semver: patch']],
  ['docs(readme): explain the setup', ['type: docs']],
  ['ci: cache npm downloads', ['type: ci']],
  ['revert(api): undo the payload change', ['type: revert']],
  ['features: add a new endpoint', REJECTED],
  ['add a new endpoint', REJECTED],
  ['feat(api)! drop the v1 payload', REJECTED],
];

let failed = 0;

for (const [title, expected] of cases) {
  try {
    const { labels, failures } = labelsFor(title);

    if (expected === REJECTED) {
      assert.strictEqual(
        failures.length,
        1,
        'expected the title to be rejected',
      );
    } else {
      assert.deepStrictEqual(
        failures,
        [],
        `unexpectedly rejected: ${failures[0]}`,
      );
      assert.deepStrictEqual(labels, expected, 'wrong labels');
    }

    console.log(`pass  ${title}`);
  } catch (error) {
    failed += 1;
    console.error(`FAIL  ${title}\n      ${error.message}`);
  }
}

if (failed > 0) {
  console.error(`\n${failed} of ${cases.length} pr-labeler cases failed`);
  process.exit(1);
}

console.log(`\nall ${cases.length} pr-labeler cases passed`);
