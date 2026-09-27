/**
 * Rendu de la conversation principale de Mnesis.
 *
 * Rôle : produire une interface volontairement simple, centrée sur l'historique
 * et la saisie, sans éléments visuels associés aux assistants génératifs.
 */

export type ConversationMessage = {
  author: "user" | "mnesis";
  text: string;
};

function escapeHtml(value: string): string {
  /** Échappe les données conversationnelles avant leur insertion dans le DOM. */
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#039;");
}

export function renderConversationMarkup(instanceName: string, messages: ConversationMessage[]): string {
  /**
   * Produit le balisage HTML de la vue principale.
   *
   * Paramètres : nom de l'instance et messages actuellement visibles.
   * Retour : fragment HTML prêt à être inséré dans la page.
   */
  const history = messages.length === 0
    ? '<div class="conversation-empty">La conversation peut commencer.</div>'
    : messages.map((message) => `<article class="message message--${message.author}"><span>${escapeHtml(message.text)}</span></article>`).join("");

  return `
    <main class="conversation-shell">
      <header class="conversation-header">
        <div>
          <p class="eyebrow">Instance</p>
          <h1>${escapeHtml(instanceName)}</h1>
        </div>
        <a class="diagnostic-link" href="#diagnostic" aria-label="Ouvrir le diagnostic">État</a>
      </header>
      <section id="history" class="conversation-history" aria-live="polite">${history}</section>
      <form id="composer" class="composer">
        <label class="sr-only" for="message">Écrire un message</label>
        <textarea id="message" name="message" rows="1" placeholder="Écrire un message" autocomplete="off"></textarea>
        <button type="submit">Envoyer</button>
      </form>
    </main>`;
}
