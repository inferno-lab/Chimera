/**
 * Central configuration for the Chimera Portal.
 * Ensure environment variables are correctly handled if they are needed.
 */

// If VITE_API_BASE_URL is set, use it. Otherwise, default to empty string for relative paths.
export const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '';

export const CHIMERA_EVENTS = {
  ATTACK_LOG: 'chimera:attack-log',
  TOGGLE_KILL_CHAIN: 'chimera:toggle-kill-chain',
  TOGGLE_RED_TEAM_CONSOLE: 'chimera:toggle-red-team-console',
  TOGGLE_XRAY_INSPECTOR: 'chimera:toggle-xray-inspector',
  TOGGLE_WAF_VISUALIZER: 'chimera:toggle-waf-visualizer',
  KILL_CHAIN_PROGRESS: 'chimera:kill-chain-progress',
} as const;
