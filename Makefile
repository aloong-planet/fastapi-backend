local:
	uvicorn app.main:app --reload --host localhost --port 8000

test:
	pytest --disable-warnings

export:
	poetry export --without-hashes > requirements.txt

swagger:
	python app/main.py

## alembic
# alembic upgrade head
# alembic revision --autogenerate -m "your migration message"
# alembic downgrade -1
