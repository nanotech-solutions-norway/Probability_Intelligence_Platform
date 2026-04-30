<?php
/**
 * Domeneshop-ready PIP Phase 2 local configuration example.
 *
 * Upload target:
 * /public_html/pip_api/config/pip_config.example.php
 *
 * Deployment:
 * 1. Copy this file to pip_config.local.php on Domeneshop.
 * 2. Replace CHANGE_ME_SERVER_SIDE_ONLY with a strong internal API key.
 * 3. Keep pip_config.local.php out of Git.
 */

return [
    'api_key' => getenv('PIP_API_KEY') ?: 'CHANGE_ME_SERVER_SIDE_ONLY',
    'enforce_api_key' => true,
    'platform_version' => '1.0.0',
    'mode' => 'mock',
];
