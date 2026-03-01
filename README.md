# Система процессинга банковских транзакций

### Описание системы
End-to-end система генерации и мониторинга банковских документов. 
Имитирует прохождение платежа через шлюз безопасности и адаптер распределенной обработки.

### Архитектура
- **Generator**: Python (FastAPI + Kafka). Генерирует поток документов и управляет аномалиями.
- **GWFI (Gateway)**: Шлюз безопасности. Фильтрация SQL-инъекций и проверка сертификатов.
- **Adapter**: Бизнес-логика и имитация работы с шардированной БД.
- **Kafka**: Брокер сообщений для гарантированной доставки.
- **Vector**: Сборщик логов и метрик хоста.
- **ClickHouse**: Аналитическое хранилище (OLAP) для логов.
- **Prometheus**: Хранилище технических метрик.
- **Grafana**: Мониторинг (Бизнес, Очереди, Инфраструктура).

### Запуск
1. Скачать Docker Desktop
2. Склонировать проект с GitHub
3. Зайти в папку с проектом через командную строку и прописать команду 
```bash
docker-compose up -d --build
```
4. Создадим таблицу для логов: перейди по адресу http://localhost:8123/play
   log/pass: admin/SecretPassword123! (лучше скопировать и вставить)
   Затем создать таблицу:
   ```sql
   CREATE TABLE IF NOT EXISTS default.logs (timestamp Float64, service String, event String, doc_id Nullable(String), doc_type Nullable(String), client_id Nullable(String), amount Nullable(Float32), currency Nullable(String), shard_id Nullable(UInt8), cert_valid Nullable(Bool), payload Nullable(String), db_delay Nullable(Float32), processing_time Nullable(Float32), factory Nullable(String), reason Nullable(String), level Nullable(String)) ENGINE = MergeTree() ORDER BY timestamp;
   ```
5. Настроим графану
   Перейти по адресу http://localhost:3000 (log/pass: admin/admin)
   В левой меню выбираем Connections - Data Sources
   Добавляем два источника:
   - **Prometheus**:
    - URL: http://prometheus:9090
    - **Save & Test**.
   - **ClickHouse**:
    - Server Address: clickhouse
    - Server Port: 8123
    - Protocol: HTTP
    - Username: admin
    - Password: SecretPassword123!
    - **Save & Test**.
      
   Импортируем дашборд
   В левом меню выбираем Dashboards
   На странице справа жмем New - Import
   И загружаешь в него .json файл, который лежит в корневой папке проекта (dashboard.json)
 6. В файле index.html изменяем ссылку на дашборд (чтобы ее найти, нужно справа сверху над дашбордом нажать на стрелочку рядом с кнопкой Share, выбрать Share intenally, внутри отключить тумблер shorten link и Copy link)
