# Todo Application API Service

Невеликий навчальний FastAPI проєкт для знайомства з pytest, pre-commit та GitHub Actions.
Користувачі й задачі зберігаються у звичайних Python списках. База даних і файли зі станом не потрібні.

## Швидкий запуск

Потрібні Git та [uv](https://docs.astral.sh/uv/getting-started/installation/).
uv автоматично встановить Python 3.12, якщо його ще немає.

```bash
uv sync --locked
uv run pre-commit install
uv run uvicorn todo_api.main:app --reload
```

Відкрийте [Swagger UI](http://127.0.0.1:8000/docs) для виконання запитів.

## Структура

```text
src/todo_api/
├── main.py                  # app = FastAPI() і підключення роутерів
├── _detail/
│   └── storage.py           # два списки та лічильники ідентифікаторів
├── users/
│   └── _detail/
│       ├── router.py        # HTTP запити для /users
│       ├── schemas.py       # UserCreate, User
│       └── service.py       # створення, пошук, видалення користувачів
└── todos/
    └── _detail/
        ├── router.py        # HTTP запити для /todos
        ├── schemas.py       # TodoCreate, TodoUpdate, Todo
        └── service.py       # створення, пошук, зміна, видалення задач

tests/                      # API тести та тести власного hook
scripts/                    # перевірка порожніх рядків у функціях
.github/workflows/ci.yml     # перевірки якості й тести
```

Роутер приймає запит, Pydantic перевіряє дані, функція в `service.py` працює зі списком.
Вся реалізація ресурсів розміщена в їхніх `_detail/`; `main.py` лише збирає застосунок.
Обробники `async def` виконують короткі операції у пам'яті без очікування вводу-виводу.

## API

| Метод | Шлях | Результат |
| --- | --- | --- |
| POST | `/users` | Створити користувача, `201` |
| GET | `/users` | Отримати список користувачів |
| GET | `/users/{user_id}` | Отримати користувача |
| DELETE | `/users/{user_id}` | Видалити користувача та його задачі, `204` |
| POST | `/todos` | Створити задачу для наявного користувача, `201` |
| GET | `/todos` | Отримати список задач |
| GET | `/todos/{todo_id}` | Отримати задачу |
| PATCH | `/todos/{todo_id}` | Оновити вказані поля задачі |
| DELETE | `/todos/{todo_id}` | Видалити задачу, `204` |

Приклад для щойно запущеного сервера:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H 'Content-Type: application/json' \
  -d '{"name": "Olena", "email": "olena@example.com"}'

curl -X POST http://127.0.0.1:8000/todos \
  -H 'Content-Type: application/json' \
  -d '{"user_id": 1, "title": "Write the first test"}'

curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H 'Content-Type: application/json' \
  -d '{"completed": true}'
```

Email є унікальним без урахування регістру: повторне створення повертає `409`.
Відсутній користувач або задача дають `404`, некоректні дані — `422`.
`PATCH` приймає `title`, `description`, `completed`; пропущені поля зберігають свої значення.
Порожній об'єкт, `null`, невідомі поля та порожній після обрізання пробілів заголовок заборонені.
Початкове значення `completed` — `false`; порожній `description` дозволений.

Це навчальний сервіс без автентифікації: API має доступ до всіх записів.
Запускайте його з одним worker. Перезапуск очищає дані; кілька процесів матимуть окремі списки.
JSON використовується лише як формат HTTP запитів і відповідей; на диск дані не записуються.

## Перевірки перед комітом

```bash
uv run pre-commit run --all-files
uv run pytest
```

Усі hook використовують інструменти з `uv.lock`, тому локальні перевірки та CI мають однакові версії.

| Інструмент | Що перевіряє |
| --- | --- |
| Black | Форматування Python, довжина рядка 120 |
| isort | Порядок імпортів, профіль Black |
| Ruff | Помилки Python, ліміт 120, NumPy docstrings, простота функцій, небезпечні конструкції |
| pydoclint | Відповідність параметрів і результатів NumPy docstrings сигнатурам функцій |
| mypy | Типи в режимі `strict` |
| Власний hook | Відсутність порожніх рядків усередині функцій |
| pre-commit-hooks | YAML, TOML, конфлікти злиття, великі файли, whitespace та debug statements |

Порожні рядки між функціями дозволені. Усередині docstrings і багаторядкових текстових значень
вони також дозволені: NumPy docstrings потребують розділення секцій.
Власний hook аналізує Python AST, тому розрізняє код і текст.
Розгорнуті NumPy docstrings перевіряються для коду застосунку й hook; тести мають короткі пояснення.

Якщо hook виправив файл, перегляньте зміни, виконайте `git add` і повторіть коміт.

## Як працює CI

Workflow запускається на `push`, `pull_request` і вручну через `workflow_dispatch`.

1. `quality` встановлює залежності з перевіркою `uv.lock` та запускає всі pre-commit hook.
2. `tests` паралельно запускає pytest на Python 3.12, 3.13 та 3.14.
3. pytest перевіряє API та рахує покриття рядків і гілок; поріг успішності — 95%.
4. Звіти `coverage.xml` і `junit.xml` зберігаються в artifacts відповідного запуску.

Версії GitHub Actions зафіксовані SHA комітів. `permissions: contents: read` обмежує доступ workflow.
Новий push у ту саму гілку або PR скасовує попередній незавершений запуск.

Для демонстрації студентам:

1. Створіть гілку, змініть очікуваний результат одного тесту та запустіть `uv run pytest`.
2. Зробіть push і відкрийте вкладку **Actions**, щоб побачити помилку CI.
3. Виправте тест, повторіть push і перевірте успішний запуск та artifacts.
4. Додайте порожній рядок усередину функції й запустіть pre-commit, щоб побачити власне правило стилю.
5. За потреби увімкніть обов'язкові status checks у налаштуваннях захисту гілки GitHub.

При зміні залежностей виконайте `uv lock` і закомітьте `pyproject.toml` разом з `uv.lock`.
Деталі інструментів: [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/),
[NumPy docstrings у Ruff](https://docs.astral.sh/ruff/settings/#lint_pydocstyle_convention),
[uv у GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/).
