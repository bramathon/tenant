CREATE TABLE IF NOT EXISTS "listings" (
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
  "location" TEXT,
  "metro" TEXT
);

CREATE INDEX listings_id on listings (id);
CREATE INDEX listings_date on listings (id,date);
CREATE INDEX listings_date_metro on listings (id,date,metro);

ALTER TABLE vancouver ADD metro TEXT;
UPDATE vancouver SET metro = "vancouver";
INSERT INTO listings SELECT * FROM vancouver;

ALTER TABLE portland ADD metro TEXT;
UPDATE portland SET metro = "portland";
INSERT INTO listings SELECT * FROM portland;

ALTER TABLE montreal ADD metro TEXT;
UPDATE montreal SET metro = "montreal";
INSERT INTO listings SELECT * FROM montreal;

ALTER TABLE toronto ADD metro TEXT;
UPDATE toronto SET metro = "toronto";
INSERT INTO listings SELECT * FROM toronto;

DROP TABLE vancouver;
DROP TABLE montreal;
DROP TABLE portland;
DROP TABLE toronto;