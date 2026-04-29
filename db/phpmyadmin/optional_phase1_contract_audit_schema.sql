-- Atlas Probability Intelligence Platform v1.0
-- Phase 1 optional contract/audit persistence scaffold
-- Execution method: Domeneshop phpMyAdmin built-in SQL console
-- Timestamp: 14:57, 29.04.2026
--
-- IMPORTANT:
-- Phase 1 does not require database deployment. Execute this script only if
-- controlled internal validation needs persistent PIP audit records.
-- This script creates PIP-owned tables only and does not alter FEA tables.

CREATE TABLE IF NOT EXISTS pip_model_versions (
    pip_model_version_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    model_key VARCHAR(128) NOT NULL,
    model_version VARCHAR(128) NOT NULL,
    sport VARCHAR(64) NOT NULL DEFAULT 'football',
    market VARCHAR(64) NOT NULL DEFAULT '1X2',
    lifecycle_status VARCHAR(64) NOT NULL DEFAULT 'candidate',
    calibration_version VARCHAR(128) DEFAULT NULL,
    feature_version VARCHAR(128) DEFAULT NULL,
    governance_notes TEXT,
    locked_for_production TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (pip_model_version_id),
    UNIQUE KEY uq_pip_model_version (model_version),
    KEY idx_pip_model_key_market (model_key, sport, market)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pip_prediction_requests (
    pip_request_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    request_uuid CHAR(36) NOT NULL,
    fixture_id BIGINT UNSIGNED NOT NULL,
    sport VARCHAR(64) NOT NULL DEFAULT 'football',
    market VARCHAR(64) NOT NULL DEFAULT '1X2',
    requested_by_system VARCHAR(64) NOT NULL DEFAULT 'FEA',
    requester_context VARCHAR(128) DEFAULT 'phase5_read_only',
    pip_integration_enabled TINYINT(1) NOT NULL DEFAULT 0,
    pip_required_for_recommendations TINYINT(1) NOT NULL DEFAULT 0,
    failsafe_mode TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pip_request_id),
    UNIQUE KEY uq_pip_request_uuid (request_uuid),
    KEY idx_pip_request_fixture_market (fixture_id, sport, market),
    KEY idx_pip_request_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pip_prediction_outputs (
    pip_output_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    request_uuid CHAR(36) NOT NULL,
    model_version VARCHAR(128) NOT NULL,
    calibration_version VARCHAR(128) DEFAULT NULL,
    response_status VARCHAR(64) NOT NULL DEFAULT 'ok',
    compliance_mode VARCHAR(64) NOT NULL DEFAULT 'display_only',
    execution_allowed TINYINT(1) NOT NULL DEFAULT 0,
    response_payload LONGTEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pip_output_id),
    KEY idx_pip_output_request_uuid (request_uuid),
    KEY idx_pip_output_model_version (model_version),
    CONSTRAINT chk_pip_execution_disabled CHECK (execution_allowed = 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pip_fea_integration_log (
    pip_fea_log_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    fixture_id BIGINT UNSIGNED DEFAULT NULL,
    market VARCHAR(64) DEFAULT NULL,
    pip_enabled TINYINT(1) NOT NULL DEFAULT 0,
    pip_available TINYINT(1) NOT NULL DEFAULT 0,
    fallback_used TINYINT(1) NOT NULL DEFAULT 1,
    error_code VARCHAR(128) DEFAULT NULL,
    latency_ms INT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pip_fea_log_id),
    KEY idx_pip_fea_fixture_market (fixture_id, market),
    KEY idx_pip_fea_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pip_contract_audit_events (
    pip_contract_audit_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    contract_name VARCHAR(128) NOT NULL,
    contract_version VARCHAR(64) NOT NULL,
    validation_status VARCHAR(64) NOT NULL,
    error_message TEXT DEFAULT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (pip_contract_audit_id),
    KEY idx_pip_contract_name_version (contract_name, contract_version),
    KEY idx_pip_contract_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
