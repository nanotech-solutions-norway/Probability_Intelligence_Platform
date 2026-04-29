<?php
/**
 * PIP Phase 2 internal fixture probability mock endpoint.
 *
 * Canonical endpoint contract:
 * GET /api/v1/probability/football/fixture/{fixture_id}?market=1X2
 *
 * Domeneshop flat-file fallback endpoint:
 * GET /api/v1/probability/football/fixture.php?fixture_id={fixture_id}&market=1X2
 *
 * The endpoint is display-only and read-only. It never creates bets, never
 * writes to bookmaker systems, and always returns execution_allowed=false.
 */

require_once __DIR__ . '/../../../../../includes/response_helpers.php';
require_once __DIR__ . '/../../../../../includes/auth.php';

pip_allow_methods(['GET']);
pip_require_api_key();

function pip_extract_fixture_id(): int {
    if (isset($_GET['fixture_id'])) {
        return max(1, (int) $_GET['fixture_id']);
    }

    $uri = (string) ($_SERVER['REQUEST_URI'] ?? '');
    if (preg_match('#/fixture/(\d+)#', $uri, $matches)) {
        return max(1, (int) $matches[1]);
    }

    return 982331;
}

function pip_normalize_market(): string {
    $market = strtoupper((string) ($_GET['market'] ?? '1X2'));
    $allowed = ['1X2', 'OVER_UNDER', 'BTTS', 'ASIAN_HANDICAP'];
    if (!in_array($market, $allowed, true)) {
        return '1X2';
    }
    return $market;
}

function pip_mock_probability_payload(int $fixtureId, string $market): array {
    $base = [
        'status' => 'ok',
        'platform' => 'atlas_probability_intelligence_platform',
        'platform_version' => '1.0.0',
        'fixture_id' => $fixtureId,
        'sport' => 'football',
        'market' => $market,
        'model_version' => 'pip-football-v1.0.0-phase2-mock',
        'data_timestamp' => pip_iso_timestamp(),
        'compliance_mode' => 'display_only',
        'execution_allowed' => false,
        'audit' => [
            'calibration_version' => 'mock-calibration-v1',
            'feature_version' => 'mock-feature-set-v1',
            'recommendation_policy_version' => 'pip-policy-v1',
            'source' => 'mock',
        ],
        'extensions' => [
            'contract_phase' => 'phase_2_internal_mock_api',
            'integration_mode' => 'internal_read_only_mock',
            'bookmaker_execution_enabled' => false,
            'frontend_token_exposed' => false,
            'write_endpoint_available' => false,
        ],
    ];

    if ($market === '1X2') {
        $base['selection_probabilities'] = [
            [
                'selection' => 'home',
                'model_probability' => 0.548,
                'bookmaker_no_vig_probability' => 0.502,
                'fair_odds' => 1.82,
                'best_available_odds' => 2.05,
                'expected_value' => 0.123,
                'confidence_score' => 0.71,
                'recommendation' => 'WATCHLIST',
            ],
            [
                'selection' => 'draw',
                'model_probability' => 0.247,
                'bookmaker_no_vig_probability' => 0.261,
                'fair_odds' => 4.05,
                'best_available_odds' => 3.80,
                'expected_value' => -0.061,
                'confidence_score' => 0.55,
                'recommendation' => 'NO_BET',
            ],
            [
                'selection' => 'away',
                'model_probability' => 0.205,
                'bookmaker_no_vig_probability' => 0.237,
                'fair_odds' => 4.88,
                'best_available_odds' => 4.40,
                'expected_value' => -0.098,
                'confidence_score' => 0.51,
                'recommendation' => 'NO_BET',
            ],
        ];
        return $base;
    }

    $base['selection_probabilities'] = [
        [
            'selection' => 'yes',
            'model_probability' => 0.510,
            'bookmaker_no_vig_probability' => 0.500,
            'fair_odds' => 1.96,
            'best_available_odds' => 1.95,
            'expected_value' => -0.006,
            'confidence_score' => 0.50,
            'recommendation' => 'NO_BET',
        ],
        [
            'selection' => 'no',
            'model_probability' => 0.490,
            'bookmaker_no_vig_probability' => 0.500,
            'fair_odds' => 2.04,
            'best_available_odds' => 2.00,
            'expected_value' => -0.020,
            'confidence_score' => 0.50,
            'recommendation' => 'NO_BET',
        ],
    ];
    return $base;
}

pip_send_json(pip_mock_probability_payload(pip_extract_fixture_id(), pip_normalize_market()));
?>
