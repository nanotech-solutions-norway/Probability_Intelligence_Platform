<?php
/**
 * Fail-soft PIP client for Domeneshop/PHP-compatible FEA deployments.
 *
 * This client only performs read-only GET calls to PIP. It never writes, never
 * executes bookmaker actions and never enables real-money or auto-betting logic.
 */

function pip_env_bool(string $name, bool $default = false): bool {
    $value = getenv($name);
    if ($value === false || $value === '') {
        return $default;
    }
    return in_array(strtolower(trim($value)), ['1', 'true', 'yes', 'on'], true);
}

function football_edge_get_pip_probability(int $fixtureId, string $market = '1X2'): array {
    $enabled = pip_env_bool('PIP_INTEGRATION_ENABLED', false);
    $failsafe = pip_env_bool('PIP_FAILSAFE_MODE', true);
    $useMock = pip_env_bool('PIP_USE_MOCK', false);
    $baseUrl = rtrim((string) getenv('PIP_BASE_URL'), '/');
    $apiKey = (string) getenv('PIP_API_KEY');
    $timeout = (int) (getenv('PIP_TIMEOUT_SECONDS') ?: 5);
    if ($timeout < 1) {
        $timeout = 5;
    }

    if (!$enabled) {
        return [
            'enabled' => false,
            'available' => false,
            'fallback_used' => true,
            'data' => null,
            'error_code' => 'PIP_DISABLED',
            'error_message' => 'PIP integration is disabled by configuration.',
            'latency_ms' => null,
        ];
    }

    if ($useMock) {
        $mockPath = dirname(__DIR__, 2) . '/examples/mock_pip_probability_response.json';
        if (is_readable($mockPath)) {
            $payload = json_decode(file_get_contents($mockPath), true);
            $payload['fixture_id'] = $fixtureId;
            $payload['market'] = $market;
            return [
                'enabled' => true,
                'available' => true,
                'fallback_used' => false,
                'data' => $payload,
                'error_code' => null,
                'error_message' => null,
                'latency_ms' => 0,
            ];
        }
        return pip_failsoft_result('PIP_MOCK_LOAD_FAILED', 'Mock PIP response could not be loaded.');
    }

    if ($baseUrl === '') {
        return pip_failsoft_result('PIP_BASE_URL_MISSING', 'PIP_BASE_URL is not configured.');
    }

    $url = $baseUrl . '/api/v1/probability/football/fixture/' . rawurlencode((string) $fixtureId) . '?market=' . rawurlencode($market);
    $start = microtime(true);

    try {
        $headers = ["Accept: application/json"];
        if ($apiKey !== '') {
            $headers[] = "X-PIP-API-Key: " . $apiKey;
        }

        if (function_exists('curl_init')) {
            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_TIMEOUT => $timeout,
                CURLOPT_HTTPHEADER => $headers,
            ]);
            $body = curl_exec($ch);
            $httpCode = (int) curl_getinfo($ch, CURLINFO_HTTP_CODE);
            $curlError = curl_error($ch);
            curl_close($ch);
            if ($body === false || $httpCode !== 200) {
                return pip_failsoft_result('PIP_HTTP_ERROR', 'PIP HTTP request failed: ' . ($curlError ?: $httpCode));
            }
        } else {
            $context = stream_context_create([
                'http' => [
                    'method' => 'GET',
                    'header' => implode("\r\n", $headers),
                    'timeout' => $timeout,
                ],
            ]);
            $body = @file_get_contents($url, false, $context);
            if ($body === false) {
                return pip_failsoft_result('PIP_HTTP_ERROR', 'PIP HTTP request failed with stream fallback.');
            }
        }

        $payload = json_decode($body, true);
        if (!is_array($payload)) {
            return pip_failsoft_result('PIP_INVALID_JSON', 'PIP returned invalid JSON.');
        }
        if (($payload['execution_allowed'] ?? null) !== false) {
            return pip_failsoft_result('PIP_CONTRACT_EXECUTION_FLAG', 'PIP violated execution_allowed=false contract.');
        }

        return [
            'enabled' => true,
            'available' => true,
            'fallback_used' => false,
            'data' => $payload,
            'error_code' => null,
            'error_message' => null,
            'latency_ms' => (int) round((microtime(true) - $start) * 1000),
        ];
    } catch (Throwable $e) {
        if (!$failsafe) {
            throw $e;
        }
        return pip_failsoft_result('PIP_CLIENT_EXCEPTION', $e->getMessage());
    }
}

function pip_failsoft_result(string $code, string $message): array {
    return [
        'enabled' => true,
        'available' => false,
        'fallback_used' => true,
        'data' => null,
        'error_code' => $code,
        'error_message' => $message,
        'latency_ms' => null,
    ];
}
?>
