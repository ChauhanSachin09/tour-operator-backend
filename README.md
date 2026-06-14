# Tour Operator Backend

A lightweight Spring Boot backend for a tour operator website.

### Features
- JWT Authentication for admin content updates
- Read/Write website content from `data/content.json`
- REST APIs for content management

### Endpoints
- `POST /api/auth/login` → Returns JWT for admin
- `GET /api/content` → Public content
- `POST /api/content/update` → Update content (requires JWT)

### Run
```bash
mvn spring-boot:run
```
