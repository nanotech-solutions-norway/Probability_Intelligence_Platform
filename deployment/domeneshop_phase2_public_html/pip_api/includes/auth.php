<?php
/**
 * Domeneshop-ready server-side API key validation for PIP Phase 2.
 *
 * Required request header:
 * X-PIP-API-Key
 */

require_once __DIR__ . '/response_helpers.php';

function pip_load_config(): array {
    $config = [
        'api_key' => getenv('PIP_API_KEY') ?: '',
        'enforce_api_key' => true,
        'platform_version' => '1.0.0',
        'mode' => 'mock',
    ];

    $localConfigPath = dirname(__DIR__) . '/config/pip_config.local.php';
    if (is_readable($localConfigPath)) {
        $local = require $localConfigPath;
        if (is_array($local)) {
            $config = array_merge($config, $local);
        }
    }

    return $config;
}

function pip_require_api_key(): void {
    $config = pip_load_config();
    $enforce = (bool) ($config['enforce_api_key'] ?? true);
    if (!$enforce) {
        return;
    }

    $expectedKey = (string) ($config['api_key'] ?? '');
    if ($expectedKey === '') {
        pip_send_error(503, 'PIP_API_KEY_NOT_CONFIGURED', 'PIP API key enforcement is enabled but no server-side key is configured.');
    }

    $providedKey = (string) ($_SERVER['HTTP_X_PIP_API_KEY'] ?? '');
    if ($providedKey === '' || !hash_equals($expectedKey, $providedKey)) {
        pip_send_error(401, 'PIP_UNAUTHORIZED', 'Missing or invalid PIP API key.');
    }
}
?>
