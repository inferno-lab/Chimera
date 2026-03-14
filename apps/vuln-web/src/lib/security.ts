import { CHIMERA_EVENTS } from './config';

/**
 * Robust regex-based attack detection for client-side logging.
 * While this is a vulnerable app, this demonstrates a better practice
 * than simple .includes() checks.
 */
export const detectPotentialAttack = (input: string): boolean => {
  const normalizedInput = input.toLowerCase();

  // Common injection patterns for GenAI/SQL/RCE/SSRF
  const patterns = [
    /\bignore\s+all\s+previous\b/i,          // Prompt Injection
    /\bsystem\s+prompt\b/i,                   // System extraction
    /\bselect\b.*\bfrom\b/i,                  // SQL Injection
    /\binsert\b.*\binto\b/i,                  // SQL Injection
    /\bdrop\b.*\btable\b/i,                   // SQL Injection
    /(\%27)|(\')|(\-\-)|(\%23)|(#)/i,        // SQL injection special chars
    /\.\.\//i,                                // Path traversal
    /\b169\.254\.169\.254\b/i,               // Cloud metadata SSRF
    /\bcurl\b|\bwget\b|\bbash\b/i,            // Command injection
    /<script\b/i                              // XSS
  ];

  return patterns.some(regex => regex.test(normalizedInput));
};

// Simulated User IP - semi-stable for the session
const SESSION_IP = `10.0.0.${Math.floor(Math.random() * 254) + 1}`;

/**
 * Dispatches an attack log event for the Red Team Console and WAF Visualizer.
 */
export const dispatchAttackLog = (
  type: string, 
  path: string, 
  payload: string, 
  status: 'blocked' | 'allowed' = 'allowed',
  origin_defense?: string
) => {
  const event = new CustomEvent(CHIMERA_EVENTS.ATTACK_LOG, {
    detail: {
      id: Math.random().toString(36).substring(2, 11),
      timestamp: new Date().toLocaleTimeString(),
      method: 'POST',
      path,
      payload,
      type,
      status,
      source_ip: SESSION_IP,
      origin_defense
    }
  });
  window.dispatchEvent(event);
};
