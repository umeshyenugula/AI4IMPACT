# ArtisanAI Unified Platform

A full-stack FastAPI platform that combines artisan onboarding, portfolio intelligence, adaptive learning, market intelligence, B2B quoting, edge telemetry, and trust workflows (provenance + escrow) into one runtime.

This repository includes:
- Backend API and orchestration layer
- Frontend multi-page UI served by FastAPI
- In-memory runtime state with optional Supabase persistence
- Optional integrations for Gemini, Cloudinary, and Firecrawl
- Service-level and scenario tests

## 1. What This Platform Does

The platform is designed to support artisan growth across multiple stages:

1. Portfolio Intelligence
- Upload portfolio images
- Analyze visual complexity and uniqueness
- Detect likely techniques and color palette

2. Adaptive Learning
- Generate personalized learning paths from craft profile and portfolio signals
- Add learning modules with skill nodes, estimated hours, and tutorial links

3. Market Intelligence and Product Pivoting
- Suggest product pivots for B2B demand
- Add market signals from web intelligence (Firecrawl when configured, fallback otherwise)
- Generate market mockup URLs for suggested products

4. B2B Catalog and Quote Generation
- Build SKU catalog entries from uploaded portfolio products (or pivot fallback)
- Generate quote math for MOQ, discount tiers, shipping, tax, and totals

5. Edge and Telemetry
- Produce edge readiness summaries for portfolio items
- Receive telemetry synchronization payloads from field devices

6. Trust Layer
- Mint provenance certificate IDs from artisan and product context
- Create and release milestone-based escrow contracts

## 2. Tech Stack

- Python 3.10+ recommended
- FastAPI and Uvicorn
- Pydantic v2 and pydantic-settings
- Pillow + NumPy for image scoring
- HTTPX for external API calls
- Optional Google GenAI client (only used if installed and API key exists)

Core dependencies are declared in requirements.txt.

## 3. Repository Layout

Top-level:
- main.py: local runner entry point
- requirements.txt: pinned Python dependencies
- README.md: project documentation
- tests/: pytest smoke tests
- app/: main application package

Application package:
- app/main.py: FastAPI app bootstrap, CORS, static mounts, router registration
- app/core/config.py: settings, directories, integration keys
- app/core/state.py: in-memory runtime state
- app/api/routes/: HTTP routes
- app/schemas/platform.py: request and response schemas
- app/services/: orchestration and integrations
- app/agents/: domain agents (portfolio, market, pedagogy, demand, edge, trust)
- app/frontend/: static HTML/CSS/JS pages served by FastAPI

Extra source snapshots:
- merged_backend_src/
- merged_frontend_src/

## 4. Local Setup (Windows PowerShell)

1. Open a terminal at project root.
2. Create virtual environment:
   py -m venv .venv
3. Activate virtual environment:
   .venv\Scripts\Activate.ps1
4. Install dependencies:
   pip install -r requirements.txt
5. Run server:
   python main.py

App defaults:
- Host: 0.0.0.0
- Port: 8000
- Reload: enabled in main.py

Open in browser:
- Home page: http://localhost:8000/
- API docs: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 5. Environment Configuration

Settings are loaded from .env at project root through pydantic-settings.

Important variables:
- allowed_origins: frontend CORS origins (default list in config)
- gemini_api_key
- gemini_text_model (default gemini-2.5-flash)
- gemini_image_model (default gemini-2.5-flash-image)
- cloudinary_cloud_name
- cloudinary_api_key
- cloudinary_api_secret
- cloudinary_folder (default artisan-ai)
- supabase_url
- supabase_service_role_key
- supabase_artisans_table (default artisans)
- supabase_portfolio_table (default portfolio_items)
- supabase_learning_paths_table (default learning_paths)
- supabase_certificates_table (default provenance_certificates)
- supabase_escrow_table (default escrow_contracts)
- firecrawl_api_key
- firecrawl_api_root (default https://api.firecrawl.dev/v1)
- edge_model_name (default phi-3-mini-simulated)
- blockchain_name (default solana-simulated)

Minimal .env for local fallback-only mode:
- Keep file empty, or only set CORS origins.

Full integration mode:
- Provide keys for Gemini, Cloudinary, Supabase, and Firecrawl.

Behavior when integrations are missing:
- Supabase: service is disabled; data stays in-memory for process lifetime.
- Firecrawl: market signals fallback to deterministic local summaries.
- Cloudinary: uploaded portfolio uses local media path URL.
- Gemini: agents use fallback generation logic where implemented.

## 6. API Route Reference

Base prefix:
- Most platform APIs are under /api/v1
- Trust APIs are under /api/v1/trust

Health:
- GET /api/v1/health

Artisan:
- POST /api/v1/artisans
- GET /api/v1/artisans/{artisan_id}

Portfolio:
- POST /api/v1/artisans/{artisan_id}/portfolio
- GET /api/v1/artisans/{artisan_id}/portfolio

Learning:
- POST /api/v1/artisans/{artisan_id}/learning-paths
- GET /api/v1/artisans/{artisan_id}/learning-paths

Market and Demand:
- GET /api/v1/artisans/{artisan_id}/market-pivots
- GET /api/v1/artisans/{artisan_id}/market-insights
- GET /api/v1/artisans/{artisan_id}/demand-forecast
- GET /api/v1/market/mockup-image?src=...

B2B:
- GET /api/v1/artisans/{artisan_id}/b2b/catalog
- POST /api/v1/artisans/{artisan_id}/b2b/quotes

Edge and Workspace:
- GET /api/v1/artisans/{artisan_id}/edge-summary
- POST /api/v1/telemetry/sync
- GET /api/v1/artisans/{artisan_id}/workspace

Trust:
- POST /api/v1/trust/provenance
- POST /api/v1/trust/escrow/contracts
- POST /api/v1/trust/escrow/contracts/{order_id}/release/{milestone_name}

Frontend and Dashboard:
- GET /
- GET /dashboard.html
- GET /register.html
- GET /portfolio.html
- GET /learning.html
- GET /workspace.html
- GET /pages/{page_name}.html
- GET /api/v1/dashboard-summary

## 7. Frontend Notes

The frontend is served as static multi-page HTML from app/frontend.

Primary pages:
- index.html
- dashboard.html
- register.html
- portfolio.html
- learning.html
- workspace.html

Assets:
- CSS mount at /css from app/frontend/css
- JS mount at /js from app/frontend/js
- Static mount at /static
- Uploaded media mount at /media

## 8. Data and Runtime Model

In-memory state object tracks:
- artisans
- portfolios by artisan
- learning paths by artisan
- demand forecasts by artisan
- telemetry batches
- provenance certificates
- escrow contracts
- incremental ID counters

Persistence strategy:
- In-memory first for live runtime speed
- Optional Supabase upsert and fetch for durability
- If Supabase is disabled or unavailable, platform continues with in-memory operation

## 9. Test Strategy and Commands

Main smoke tests:
- tests/test_final_platform.py

Additional scenario scripts:
- test_agents.py
- test_portfolio_all_items.py
- test_portfolio_gallery_workspace.py
- test_portfolio_techniques.py

Run all pytest tests:
- pytest -q

Run specific smoke module:
- pytest tests/test_final_platform.py -q

Run scenario scripts directly:
- python test_agents.py
- python test_portfolio_all_items.py
- python test_portfolio_gallery_workspace.py
- python test_portfolio_techniques.py

## 10. Typical End-to-End Flow

1. Register artisan via POST /api/v1/artisans.
2. Upload one or more images to portfolio endpoint.
3. Retrieve portfolio analysis and generated techniques.
4. Build or fetch learning paths.
5. Fetch market pivots and demand forecast.
6. Pull B2B catalog and generate a quote.
7. Mint provenance certificate for a product.
8. Create escrow contract and release milestones.
9. Fetch unified workspace for full dashboard composition.

## 11. Troubleshooting

1. Server starts but pages are missing
- Confirm app/frontend files exist.
- Verify settings.frontend_dir points to app/frontend.

2. Data disappears after restart
- Expected in fallback mode because state is in-memory.
- Configure Supabase URL and service role key for persistence.

3. Market insights do not show real web sources
- Set firecrawl_api_key in .env.
- Without key, fallback market signals are returned by design.

4. Upload succeeds but image URL is local only
- Configure Cloudinary credentials to get secure hosted URLs.

5. Learning generation is basic or fallback
- Install and configure Google GenAI package and set gemini_api_key.

6. CORS errors from frontend app
- Add frontend origin to allowed_origins in settings.

## 12. Security and Production Notes

- Do not commit real API keys to source control.
- Use environment-specific .env files or secret managers.
- Replace simulated blockchain and edge model names with real values in production.
- Add authentication and authorization before production exposure.
- Validate and rate-limit file upload endpoints.

## 13. Roadmap Suggestions

- Add database migrations and stronger persistence model.
- Introduce auth (JWT or session) and role-based access control.
- Add background jobs for expensive AI/image tasks.
- Add contract status transitions and escrow audit trails.
- Expand test coverage for route layer and error paths.

## 14. Maintainer Quick Checklist

Before shipping a change:
1. Run pytest -q.
2. Start server and verify key pages load.
3. Test artisan registration and portfolio upload.
4. Confirm market, learning, and trust endpoints respond.
5. Check dashboard summary and workspace payload shape.
6. Validate .env keys for target environment.

---

If you want, this README can also be extended with:
- ready-to-import Postman collection examples,
- sample request and response JSON snippets per endpoint,
- Dockerfile and docker-compose local stack instructions.
