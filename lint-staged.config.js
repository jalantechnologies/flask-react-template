const quote = (files) => files.map((file) => JSON.stringify(file)).join(' ');

module.exports = {
  '*.{js,ts,tsx,yml,yaml,md}': (files) =>
    `prettier --write --ignore-path .prettierignore ${quote(files)}`,
  '*.py': (files) => [
    `pipenv run autoflake -i ${quote(files)}`,
    `pipenv run isort ${quote(files)}`,
    `pipenv run black ${quote(files)}`,
  ],
};
