<?php
/**
 * Isolated Domeneshop PIP Phase 2 health endpoint.
 *
 * Upload target:
 * /public_html/pip_phase2/api/v1/pip/health.php
 *
 * URL:
 * https://www.atlas-ai.no/pip_phase2/api/v1/pip/health
 */

require_once __DIR__ . '/../../../pip_api/includes/response_helpers.php';
require_once __DIR__ . '/../../../pip_api/includes/auth.php';

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
