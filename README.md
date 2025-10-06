# Interpol Red Notice Tracker

Interpol kırmızı liste verilerini periyodik olarak çekip RabbitMQ kuyruğuna yazan, oradan tüketip PostgreSQL’e kaydeden ve FastAPI tabanlı bir web arayüzünde canlı olarak gösteren mikroservis projesi.

### Mimarinin Özeti

- Fetcher (Container A): Interpol Red Notice verisini çeker, RabbitMQ’ya mesaj olarak yayınlar.
- Web Server (Container B): RabbitMQ’dan mesaj tüketir, PostgreSQL’e kaydeder, web arayüzünde listeler. 
- RabbitMQ (Container C): Mesaj kuyruğu sistemi, Management UI ile gözlemleme.

## Özellikler

- FastAPI + Jinja2 ile basit ve hızlı web arayüzü.
- RabbitMQ üzerinden producer/consumer mimarisi.
- SQLAlchemy ORM ile PostgreSQL kalıcı depolama.
- Docker Compose ile tek komutla build ve orkestrasyon.
- .env ile konfigürasyon, kod değiştirmeden ayar yönetimi.
- Test modu (TEST_MODE) ile gerçek API olmadan mock veri akışı.

## Gereksinimler

- Docker 20.10+ ve Docker Compose
- 2 GB+ RAM önerilir (RabbitMQ + PostgreSQL için)

## Hızlı Başlangıç

1) Depoyu klonla
- git clone <repo-url>
- cd interpol-notice-tracker

2) .env dosyasını hazırla
- .env içeriği:
  - RABBITMQ_USER=admin
  - RABBITMQ_PASSWORD=admin123
  - RABBITMQ_QUEUE=interpol_notices
  - POSTGRES_USER=interpol_user
  - POSTGRES_PASSWORD=interpol_pass
  - POSTGRES_DB=interpol_db
  - INTERPOL_API_URL=https://ws-public.interpol.int/notices/v1/red
  - FETCH_INTERVAL=30
  - RESULTS_PER_PAGE=20
  - TEST_MODE=true

3) Servisleri başlat
- docker-compose up --build

4) Arayüzler
- Web Uygulaması: http://localhost:8000
- RabbitMQ UI: http://localhost:15672 (admin/admin123)

## Proje Yapısı

- container_a: Veri toplayıcı (curl-cffi + pika)
- container_b: Web sunucu (FastAPI, SQLAlchemy, Jinja2)
- docker-compose.yml: Orkestrasyon
- tests: Basit entegrasyon testleri

## Çalışma Akışı

- Fetcher, INTERPOL_API_URL adresinden periyodik GET isteği yapar ve notice’leri tek tek RabbitMQ kuyruğuna gönderir
- Web Server, RabbitMQ kuyruğunu dinler, mesajları PostgreSQL’e yazar ve / üzerinden HTML tablo olarak gösterir
- Kayıt güncellenirse arayüzde “GÜNCELLENDİ” olarak vurgulanır.

## Konfigürasyon

- Tüm ayarlar .env ile yapılır:
  - FETCH_INTERVAL: Saniye cinsinden çekme periyodu
  - RESULTS_PER_PAGE: API’dan sayfa başına çekilecek kayıt
  - TEST_MODE: true ise mock veri üretilir
- docker-compose.yml, .env içindeki değişkenleri kullanır. 

## RabbitMQ

- Kuyruk adı: interpol_notices
- Kalıcılık: queue durable, mesaj delivery_mode=2 ile kalıcı.
- İzleme: RabbitMQ UI üzerinden Queues sekmesi.

## Veritabanı

- PostgreSQL servis adı: db
- Varsayılan bağlantı: postgresql://interpol_user:interpol_pass@db:5432/interpol_db
- Tablo: interpol_notices (entity_id PK, JSON alanları, timestamp alanları)

## Geliştirme ve Test

- Kod formatı ve yorumlar PEP8 uyumlu tutulmuştur.
- Test modu: TEST_MODE=true iken fetcher gerçek API yerine mock notice üretir.
- Container log’ları:
  - docker logs interpol_fetcher
  - docker logs interpol_webserver

## Sık Karşılaşılan Sorunlar

- 403 Forbidden (API): Browser’da çalışıp kodda çalışmıyorsa anti-bot korumalarından dolayı curl-cffi ile browser impersonation kullanılır.
- “database does not exist”: Eski volume çakışmaları için docker-compose down -v ardından yeniden başlatın.
- Healthcheck hataları: Postgres healthcheck’te -d ${POSTGRES_DB} parametresi kullanın.
## References

- [Dockerizing Celery and FastAPI - TestDriven.io](https://testdriven.io/courses/fastapi-celery/docker/)
- [FastAPI + Celery + Flower + RabbitMQ + Redis Example](https://github.com/luovkle/fastapi-celery-flower-rabbitmq-redis)
- [Building a FastAPI Application with Celery, RabbitMQ, and PostgreSQL](https://blog.devgenius.io/building-a-fastapi-application-with-celery-rabbitmq-and-postgresql-dockerized-a-step-by-step-e4583bde4d6b)
- [FastAPI + PostgreSQL + RabbitMQ + Docker Example](https://blog.devops.dev/fastapi-postgresql-alembic-sqlalchemy-rabbitmq-docker-example-10c34f100167)
- [Python ML in Production - FastAPI + Celery with Docker](https://denisbrogg.hashnode.dev/python-ml-in-production-part-1-fastapi-celery-with-docker)
- [FastAPI Template Issues - Open Collective](https://opencollective.ecosyste.ms/collectives/fastapi-template/issues)
- [FastAPI + PostgreSQL + Celery + RabbitMQ + Redis Backend Discussion](https://www.reddit.com/r/FastAPI/comments/nshn5b/fastapipostgresqlceleryrabbitmq-redis_backend_with/)

## Lisans

- MIT Lisansı