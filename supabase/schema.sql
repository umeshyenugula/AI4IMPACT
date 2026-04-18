create table if not exists artisans (
  id bigint primary key,
  name text not null,
  email text not null,
  region text,
  village text,
  craft_tradition text,
  created_at timestamptz not null default now()
);

create table if not exists portfolio_items (
  id bigint primary key,
  artisan_id bigint not null references artisans(id) on delete cascade,
  title text,
  description text,
  image_path text not null,
  image_url text,
  complexity_score double precision not null,
  uniqueness_score double precision not null,
  complexity_label text not null,
  detected_techniques jsonb not null default '[]'::jsonb,
  color_palette jsonb not null default '[]'::jsonb,
  texture_features jsonb not null default '{}'::jsonb,
  structural_features jsonb not null default '{}'::jsonb,
  analysed_at timestamptz not null default now()
);

create table if not exists learning_paths (
  id bigint primary key,
  artisan_id bigint not null references artisans(id) on delete cascade,
  title text not null,
  total_modules integer not null,
  modules jsonb not null default '[]'::jsonb
);

create table if not exists provenance_certificates (
  certificate_id text primary key,
  blockchain text not null,
  product_id text not null,
  minted_at timestamptz not null default now()
);

create table if not exists escrow_contracts (
  order_id text primary key,
  artisan_id bigint not null references artisans(id) on delete cascade,
  buyer_name text not null,
  total_amount_usd double precision not null,
  milestones jsonb not null default '[]'::jsonb
);
