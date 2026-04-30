<?php
/**
 * Isolated namespace shared response helpers for PIP Phase 2.
 */

function pip_security_headers(): void {
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
    header('Pragma: no-cache');
    header('X-Content-Type-Options: nosniff');
    header('X-Robots-Tag: noindex, nofollow');
}

function pip_send_json(array $payload, int $statusCode = 200): void {
    pip_security_headers();
    http_response_code($statusCode);
    echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
    exit;
}

function pip_send_error(int $statusCode, string $code, string $message): void {
    pip_send_json([
        'status' => 'error',
        'code' => $code,
        'message' => $message,
    ], $statusCode);
}

function pip_allow_methods(array $allowedMethods): void {
    $method = strtoupper((string) ($_SERVER['REQUEST_METHOD'] ?? 'GET'));
    $normalized = array_map('strtoupper', $allowedMethods);
    if (!in_array($method, $normalized, true)) {
        header('Allow: ' . implode(', ', $normalized));
        pip_send_error(405, 'PIP_METHOD_NOT_ALLOWED', 'This PIP endpoint is read-only and accepts GET only.');
    }
}

function pip_iso_timestamp(): string {
    return (new DateTimeImmutable('now', new DateTimeZone('UTC')))->format(DateTimeInterface::ATOM);
}
?>
