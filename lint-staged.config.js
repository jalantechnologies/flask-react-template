module.exports = {
  '*.{js,ts,tsx}': ['prettier --write --ignore-path .prettierignore'],
  '*.py': ['pipenv run autoflake -i', 'pipenv run isort', 'pipenv run black'],
};
