lint:
	cat data.json | jq '.' > /dev/null
	pylint3 app.py --disable=missing-docstring || true
	npx eslint static/dashboard.js
lint-fix:
	json-format data.json
	autopep8 -i app.py
	npx eslint static/dashboard.js --fix
	npx eslint static/utilities.js --fix
	npx eslint static/financial-assets.js --fix
