-- Delivery receipts only. Contact details and vehicle notes are sent by email, not stored here.
CREATE TABLE IF NOT EXISTS appointment_receipts (
  request_id TEXT PRIMARY KEY,
  payload_hash TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'uncertain')),
  message_id TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS appointment_receipts_created ON appointment_receipts(created_at);
