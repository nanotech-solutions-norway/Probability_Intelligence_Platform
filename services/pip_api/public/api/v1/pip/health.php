<?php
/**
 * PIP Phase 2 internal health endpoint.
 *
 * Endpoint:
 * GET /api/v1/pip/health
 *
 * Behavior:
 * - Requires server-side X-PIP-API-Key validation by default.
 * - Returns no secrets.
 * - Provides read-only mock/internal readiness status only.
 */

require_once __DIR__ . '/../../../../includes/response_helpers.php';
require_once __DIR__ . '/../../../../includes/auth.php';

pip_allow_methods(['GET']);
pip_require_api_key();

$config = pip_load_config();

pip_send_json([
    'status' => 'ok',
    'platform' => 'atlas_probability_intelligence_platform',
    'platform_version' => (string) ($config['platform_version'] ?? '1.0.0'),
    'mode' => 'mock',
    'api_surface' => 'internal_read_only',
    'execution_allowed' => false,
    'compliance_mode' => 'display_only',
    'timestamp' => pip_iso_timestamp(),
]);
?>
