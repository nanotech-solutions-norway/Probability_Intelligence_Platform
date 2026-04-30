<?php
/**
 * Isolated namespace PIP Phase 2 local configuration example.
 *
 * Upload target:
 * /public_html/pip_phase2/pip_api/config/pip_config.example.php
 *
 * Copy to:
 * /public_html/pip_phase2/pip_api/config/pip_config.local.php
 */

return [
    'api_key' => getenv('PIP_API_KEY') ?: 'CHANGE_ME_SERVER_SIDE_ONLY',
    'enforce_api_key' => true,
    'platform_version' => '1.0.0',
    'mode' => 'mock',
];
