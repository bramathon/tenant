CREATE TABLE IF NOT EXISTS "vancouver" (
"date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT
);
CREATE TABLE IF NOT EXISTS "portland" (
"date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT
);
CREATE TABLE IF NOT EXISTS "montreal" (
"date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT
);
CREATE TABLE IF NOT EXISTS "toronto" (
"date" TEXT,
  "id" TEXT,
  "title" TEXT,
  "latitude" REAL,
  "longitude" REAL,
  "address" TEXT,
  "date_available" TEXT,
  "price" REAL,
  "area" REAL,
  "neighbourhood" TEXT,
  "extras" TEXT,
  "bedrooms" REAL,
  "bathrooms" REAL,
  "unit_type" TEXT,
  "parking" TEXT,
  "smoking" REAL,
  "pets" TEXT,
  "laundry" TEXT,
  "furnished" INTEGER,
  "City" TEXT,
  "location" TEXT
);

CREATE INDEX van_id on vancouver (id);
CREATE INDEX van_id_date on vancouver (id,date);

CREATE INDEX po_id on portland (id);
CREATE INDEX po_id_date on portland (id,date);

CREATE INDEX to_id on toronto (id);
CREATE INDEX to_id_date on toronto (id,date);

CREATE INDEX mtl_id on montreal (id);
CREATE INDEX mtl_id_date on montreal (id,date);

ALTER TABLE "vancouver" ADD "body" TEXT;
ALTER TABLE "montreal" ADD "body" TEXT;
ALTER TABLE "portland" ADD "body" TEXT;