Welcome to smart Cart !!😉
smartcart/                           <- GitHub repo root
├── .gitignore                       <- Global ignore rules for the whole repo
├── .env                             <- Environment variables (ignored by git)
├── requirements.txt                 <- Python dependencies
└── productcompare/                  <- Outer Django project root
    ├── manage.py
    ├── productcompare/              <- Inner folder (Django settings)
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── products/                    <- Your main Django app
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── urls.py
    │   ├── views.py
    │   ├── scraper/                 <- (Optional) scraping scripts
    │   │   ├── __init__.py
    │   │   ├── amazon_scraper.py
    │   │   ├── flipkart_scraper.py
    │   │   └── ...
    │   └── templates/               <- HTML templates
                ├── home.html
                
    ├── static/ 
            ├── home.css
    ├── media/                        <- User uploads (if any)
    └── db.sqlite3                    <- Local dev database (ignored in prod)
