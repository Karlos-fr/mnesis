/**
 * Vue de diagnostic cognitif de Mnesis.
 *
 * Rôle : rendre lisibles les principaux facteurs d'une décision dans une vue
 * secondaire, distincte de la conversation.
 */

export type DiagnosticTrace = {
  action: string;
  confidence: number;
  candidate_actions: Record<string, number>;
  consulted_concepts: string[];
  affect_snapshot: Record<string, number>;
};

function escapeHtml(value: string): string {
  /** Échappe une valeur avant affichage dans la vue de diagnostic. */
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

export function renderDiagnosticsMarkup(trace: DiagnosticTrace): string {
  /** Produit la vue HTML en lecture seule d'une trace cognitive. */
  const concepts = trace.consulted_concepts.length
    ? trace.consulted_concepts.map((value) => `<li>${escapeHtml(value)}</li>`).join("")
    : "<li>Aucun</li>";
  const affect = Object.keys(trace.affect_snapshot).length
    ? Object.entries(trace.affect_snapshot).map(([name, value]) => `<li><span>${escapeHtml(name)}</span><strong>${Math.round(value * 100)} %</strong></li>`).join("")
    : "<li>Aucun état affectif enregistré</li>";
  return `<section class="diagnostic"><a href="#">← Conversation</a><p class="eyebrow">Décision</p><h1>${escapeHtml(trace.action)}</h1><div class="diagnostic-confidence"><span>Confiance</span><strong>${Math.round(trace.confidence * 100)} %</strong></div><h2>Concepts consultés</h2><ul>${concepts}</ul><h2>État émotionnel</h2><ul>${affect}</ul></section>`;
}
