/**
 * Tests de la vue de diagnostic cognitif.
 *
 * Rôle : vérifier que les informations internes restent lisibles dans une vue
 * dédiée sans être mélangées à l'historique conversationnel.
 */

import assert from "node:assert/strict";
import test from "node:test";

import { renderDiagnosticsMarkup } from "../src/components/diagnostics.ts";

test("le diagnostic affiche action, confiance, concepts et état émotionnel", () => {
  const html = renderDiagnosticsMarkup({
    action: "RÉPONDRE",
    confidence: 0.82,
    candidate_actions: { "RÉPONDRE": 0.9 },
    consulted_concepts: ["concept-1"],
    affect_snapshot: { curiosity: 0.7, joy: 0.5 },
  });

  assert.match(html, /RÉPONDRE/);
  assert.match(html, /82 %/);
  assert.match(html, /concept-1/);
  assert.match(html, /curiosity/);
});
