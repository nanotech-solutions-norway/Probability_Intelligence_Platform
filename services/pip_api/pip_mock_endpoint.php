<?php
/**
 * PIP Phase 1 mock endpoint for controlled internal testing.
 * Upload only behind server-side protection. Do not expose as public write API.
 */
header('Content-Type: application/json; charset=utf-8');

$expectedKey = getenv('PIP_API_KEY');
if ($expectedKey !== false && $expectedKey !== '') {
    $provided = $_SERVER['HTTP_X_PIP_API_KEY'] ?? '';
    if (!hash_equals($expectedKey, $provided)) {
        http_response_code(401);
        echo json_encode(['status' => 'error', 'message' => 'Unauthorized']);
        exit;
    }
}

$fixtureId = isset($_GET['fixture_id']) ? (int) $_GET['fixture_id'] : 982331;
$market = isset($_GET['market']) ? (string) $_GET['market'] : '1X2';

$payloadPath = __DIR__ . '/../../examples/mock_pip_probability_response.json';
$payload = json_decode(file_get_contents($payloadPath), true);
$payload['fixture_id'] = $fixtureId;
$payload['market'] = $market;
$payload['execution_allowed'] = false;
$payload['compliance_mode'] = 'display_only';

echo json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
?>
