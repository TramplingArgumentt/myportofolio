# Copilot instructions

## Commands

This is a Django project; run commands from the repository root.

```bash
python -m pip install -r requirements.txt
python manage.py runserver
python manage.py check
python manage.py test main
python manage.py test main.tests.ModelTest.test_create_experience_ajax_adds_an_experience
python manage.py makemigrations main
python manage.py migrate
```

Tests use Django's `TestCase` in `main/tests.py`. The focused test command above shows how to run one test; replace the class and method with the target test. There is no separate frontend build or configured lint command in the repository.

## Architecture

- `portofolio/` is the Django project configuration: `portofolio/urls.py` includes the `main` app routes, and `settings.py` configures templates, static files, authentication, and the database. Local development uses SQLite; setting `PRODUCTION=true` switches to PostgreSQL using `DB_*` environment variables.
- `main/` owns the portfolio domain: `models.py` defines Experience, Project, Education, Skill, and shared Tag records; `forms.py` defines their `ModelForm`s; `views.py` handles page rendering, authentication, CRUD, and JSON responses; `urls.py` maps named routes.
- Templates live in the root `templates/` directory. `base.html` provides shared navigation and layout; the feature pages render the portfolio sections. Experience, Projects, Education, and Skill pages fetch their JSON endpoints and build their cards in inline JavaScript. The add flows use the shared `components/project_form_modal.html`; the standalone create/edit flows use `form_page.html`.
- `static/css/style.css` contains the site styling, and `static/js/toast.js` provides toast behavior. Database schema changes are tracked in `main/migrations/`.

## Repository conventions

- Keep route names in the `main` namespace and use Django's `reverse()` / `{% url %}` helpers rather than hard-coded app URLs. Routes for portfolio records use UUIDs.
- The portfolio JSON endpoints return a list of objects with `pk` and `fields`; the page scripts depend on those field names. Coordinate changes to response shape with the corresponding inline JavaScript and tests.
- Portfolio forms are `ModelForm`s, and the same forms are used by normal create/edit views and AJAX create endpoints. The four feature pages share add-modal markup; retain this shared structure when updating those forms.
- Enforce permissions in views, not only by hiding controls in templates: create/delete flows are restricted to the portfolio superuser, while edit controls and views use Django model change permissions. Preserve these checks for both regular and AJAX routes.
- New model schema changes need a migration under `main/migrations/`. Keep model/form/view/template updates in sync, and cover changed routes, permissions, or JSON fields in `main/tests.py`.
- Templates and user-facing messages use a mix of English and Indonesian; retain the existing wording style and Django template patterns when changing UI.
- Environment files and the local SQLite database are ignored by Git. Do not commit local credentials or database files.
