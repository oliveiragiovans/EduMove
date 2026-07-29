-- =====================================================
-- Migration 010 - Add school active status
--
-- Schools must be deactivated instead of permanently
-- deleted so their historical records remain available.
-- =====================================================

ALTER TABLE schools
    ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE
        AFTER state;
