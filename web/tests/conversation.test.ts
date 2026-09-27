/**
 * Tests de la vue conversationnelle Web.
 *
 * Rôle : vérifier que l'interface reste centrée sur l'échange et n'adopte pas
 * les codes visuels d'un assistant d'IA générative.
 */

import assert from "node:assert/strict";
import test from "node:test";

import { renderConversationMarkup } from "../src/components/conversation.ts";

test("la conversation affiche l'identité, l'historique et le compositeur", () => {
  const html = renderConversationMarkup("Mnesis personnel", [
    { author: "mnesis", text: "Bonjour." },
    { author: "user", text: "Salut" },
  ]);

  assert.match(html, /Mnesis personnel/);
  assert.match(html, /Bonjour\./);
  assert.match(html, /Salut/);
  assert.match(html, /Écrire un message/);
});

test("la conversation n'utilise pas les codes de génération IA", () => {
  const html = renderConversationMarkup("Mnesis", []).toLowerCase();

  for (const forbidden of ["régénérer", "générer", "suggestion de prompt", "ia réfléchit"]) {
    assert.equal(html.includes(forbidden), false);
  }
});
