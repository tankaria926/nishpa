# Nishpa Django Project

This project provides an `inquiry` app where users can submit contact information and select products by category with quantities. Submissions are stored in the database.

Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
cd Nishpa
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Seeding data

- Use the hardcoded seeder:

```powershell
cd Nishpa
python manage.py create_sample_data
```

- Or import from an Excel file with columns: `Category`, `ProductName`, `ImageURL`, `SKU` (headers on first row). Example:

```powershell
cd Nishpa
python manage.py import_products_excel path\to\products.xlsx
```

If no Excel file is provided, the import command will fall back to the built-in hardcoded product list.
