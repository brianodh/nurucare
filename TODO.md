# NuruCare Project TODO List

A comprehensive, categorized backlog of incomplete items, bugs, technical debt and future features for the NuruCare platform.

## High Priority Items

### Security Fixes
| Item | Type | Description |
|------|------|-------------|
| Remove hardcoded nurse credentials | Bug/Security | Nurse accounts are currently hardcoded in `backend/auth.py`; move to database with bcrypt-hashed passwords |
| Hash nurse session keys in database | Security | Session keys are stored in plaintext; store SHA-256 hashes instead |
| Enforce strong JWT secret requirement | Security | Make `SECRET_KEY` a required env variable with no default |
| Fix CORS configuration | Security | Restrict `allow_origins` from `["*"]` to specific trusted frontend domains |
| Add rate limiting to all endpoints | Feature/Security | Add rate limiting (e.g., using `slowapi`) to prevent brute-force attacks |

### Bug Fixes
| Item | Type | Description |
|------|------|-------------|
| Resolve duplicate backend app confusion | Bug/Refactor | Choose either `main.py` or `app.py` as single entry point (remove one) |
| Fix database migration for `used` column | Bug | Ensure `partner_sync.used` column exists (add automatic migration logic) |
| Fix partner sync endpoint inconsistency | Bug | Frontend uses `main.py` endpoints, but `backend/api/endpoints/sync.py` has alternate implementation |
| Fix duplicate vite config files | Refactor | Remove either `vite.config.js` or `vite.config.mjs` (keep only one) |

### Feature Completion
| Item | Type | Description |
|------|------|-------------|
| Full implementation of `backend/api/endpoints/` | Feature | Connect the alternate API endpoints to the main app |
| Complete RAG integration | Feature | Implement full embedding pipeline with pgvector |

## Medium Priority Items

### Security
| Item | Type | Description |
|------|------|-------------|
| Improve nurse session key entropy | Security | Increase key length or add alphanumeric characters (still keep user-friendly) |
| Add dependency vulnerability scanning | DevOps | Set up Snyk, Dependabot, or similar for automated dependency checks |
| Improve logging practices | Refactor | Use structured logging (e.g., structlog) and redact sensitive data |

### Features
| Item | Type | Description |
|------|------|-------------|
| Full offline-first PWA | Feature | Complete offline data storage with local sync |
| Enhanced partner sync with conflict resolution | Feature | Add conflict handling and real-time sync |
| Clinical audit trail | Feature | Log all recommendation access and changes for audit |
| Input validation & sanitization | Refactor | Add strict Pydantic validation for all API inputs |

### DevOps
| Item | Type | Description |
|------|------|-------------|
| Remove hardcoded database credentials from docker-compose.yml | Refactor | Use environment variables exclusively for all credentials |
| Add monitoring (Prometheus/Grafana) | DevOps | Set up metrics collection and dashboards |
| Add error tracking (Sentry) | DevOps | Implement error tracking and alerting |

### Documentation
| Item | Type | Description |
|------|------|-------------|
| Update API documentation (docs/api_documentation.md) | Documentation | Keep API docs in sync with latest changes |
| Add complete setup guide for new contributors | Documentation | Step-by-step guide for local setup |
| Add testing documentation | Documentation | How to run unit/integration tests |

## Low Priority Items

### Features & UX
| Item | Type | Description |
|------|------|-------------|
| Add more language support (beyond English/Swahili) | Feature | Add support for additional local languages |
| Enhanced UI/UX animations | Feature | Improve micro-animations and transitions |
| User preferences persistence | Feature | Store user preferences locally |

### Refactoring & Code Quality
| Item | Type | Description |
|------|------|-------------|
| Adopt Clean/Hexagonal Architecture | Refactor | Separate domain logic from API/database layers for better testability |
| Microservices readiness | Refactor | Split monolith into modular components (auth, recommendations, sync) |
| Async processing for AI tasks | Refactor | Use Celery/RQ to avoid blocking API calls on AI recommendations |
| Code duplication cleanup | Refactor | Remove duplicate files (e.g., database.py in two places) |

## Test Coverage
| Item | Type | Description |
|------|------|-------------|
| Increase unit test coverage | Test | Add tests for all core modules |
| Add end-to-end tests | Test | Implement E2E tests with Playwright or Cypress |
| Add integration tests for sync flows | Test | Test full partner sync and nurse handoff flows |
