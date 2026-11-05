import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Lê as configurações do SeaweedFS; sem o arquivo, as imagens ficam na pasta media
load_dotenv(BASE_DIR / 'env.conf')

SECRET_KEY = 'django-insecure-x19c0*qyi5l2n3+#)0#2z(f*1++068x==qge0qidpm2z^lojgz'

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    # o jazzmin precisa vir antes do admin para substituir os templates dele
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'usuarios',
    'catalogo',
    'vendas',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'acervo_sonoro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'acervo_sonoro.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

USAR_SEAWEEDFS = os.environ.get('USAR_SEAWEEDFS', 'False') == 'True'

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

if USAR_SEAWEEDFS:
    STORAGES['default'] = {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'bucket_name': os.environ.get('SEAWEEDFS_BUCKET'),
            'endpoint_url': os.environ.get('SEAWEEDFS_ENDPOINT'),
            'access_key': os.environ.get('SEAWEEDFS_ACCESS_KEY'),
            'secret_key': os.environ.get('SEAWEEDFS_SECRET_KEY'),
            'region_name': 'us-east-1',
            'addressing_style': 'path',
            # endereço usado nas URLs das imagens (inclui o bucket)
            'custom_domain': os.environ.get('SEAWEEDFS_PUBLIC_DOMAIN'),
            'url_protocol': 'http:',
            'querystring_auth': False,
            'file_overwrite': False,
        },
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/auth/login'

JAZZMIN_SETTINGS = {
    'site_title': 'Acervo Sonoro',
    'site_header': 'Acervo Sonoro',
    'site_brand': 'Acervo Sonoro',
    'welcome_sign': 'Bem-vindo ao ambiente de gestão da loja Acervo Sonoro',
    'copyright': 'Acervo Sonoro - Loja de CDs e Álbuns',
    'icons': {
        'auth.User': 'fas fa-user',
        'auth.Group': 'fas fa-users',
        'usuarios.Perfil': 'fas fa-id-card',
        'usuarios.Endereco': 'fas fa-map-marker-alt',
        'catalogo.Artista': 'fas fa-microphone',
        'catalogo.Genero': 'fas fa-tags',
        'catalogo.Gravadora': 'fas fa-building',
        'catalogo.Album': 'fas fa-compact-disc',
        'catalogo.Faixa': 'fas fa-music',
        'catalogo.Produto': 'fas fa-box',
        'catalogo.Avaliacao': 'fas fa-star',
        'vendas.Carrinho': 'fas fa-shopping-cart',
        'vendas.ItemCarrinho': 'fas fa-cart-plus',
        'vendas.Pedido': 'fas fa-receipt',
        'vendas.ItemPedido': 'fas fa-list',
    },
}

JAZZMIN_UI_TWEAKS = {
    'theme': 'flatly',
    'dark_mode_theme': 'darkly',
    'navbar': 'navbar-dark bg-primary',
    'sidebar': 'sidebar-dark-primary',
}
