@'
# Practo For Animals – Project Workflow

## 1. Project Structure

The project contains three independent frontend modules and one shared backend.

- Practo_For_Animals: Animal healthcare frontend.
- AI_Education: Educational courses frontend.
- AI_Content_Creator: Carousel content creation frontend.
- backend: FastAPI application, database, routers and services.
- Documentation: Project report and workflow documentation.

## 2. Overall Application Architecture

```text
                 USER
                   |
                   v
          FRONTEND APPLICATION
                   |
          HTML / CSS / JavaScript
                   |
                   v
              FASTAPI
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
    ANIMALS     EDUCATION    CONTENT
     ROUTER      ROUTER      ROUTER
       |           |           |
       +-----------+-----------+
                   |
                   v
              SQLITE DB
                   |
                   v
           RESPONSE TO USER