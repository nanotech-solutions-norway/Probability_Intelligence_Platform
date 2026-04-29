<?php
/**
 * PIP Phase 2 local configuration example.
 *
 * Deployment procedure:
 * 1. Copy this file to pip_config.local.php on the server.
 * 2. Replace CHANGE_ME_SERVER_SIDE_ONLY with a strong internal API key.
 * 3. Keep pip_config.local.php out of Git and outside public browser paths.
 *
 * The API key must never be placed in frontend JavaScript, static HTML,
 * browser-visible configuration, public repo secrets, or client-side code.
 */

return [
    'api_key' => getenv('PIP_API_KEY') ?: 'CHANGE_ME_SERVER_SIDE_ONLY',
    'enforce_api_key' => true,
    'platform_version' => '1.0.0',
    'mode' => 'mock',
];
