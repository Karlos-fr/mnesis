/**
 * Point d'entrée navigateur de Mnesis.
 *
 * Rôle : relier la vue de conversation au client HTTP sans introduire de logique
 * cognitive côté navigateur.
 */

import { MnesisApiClient } from "./api/client.js";
import { type ConversationMessage, renderConversationMarkup } from "./components/conversation.js";
import { renderDiagnosticsMarkup } from "./components/diagnostics.js";

const api = new MnesisApiClient();
const messages: ConversationMessage[] = [];
let instanceId = "";
let instanceName = "Mnesis";
let lastTraceId = "";

function render(): void {
  /** Met à jour la conversation puis reconnecte le formulaire au gestionnaire d'envoi. */
  document.querySelector<HTMLDivElement>("#app")!.innerHTML = renderConversationMarkup(instanceName, messages);
  document.querySelector<HTMLFormElement>("#composer")!.addEventListener("submit", handleSubmit);
  const history = document.querySelector<HTMLElement>("#history")!;
  history.scrollTop = history.scrollHeight;
}

async function handleSubmit(event: SubmitEvent): Promise<void> {
  /** Envoie le contenu non vide du compositeur puis affiche la réponse. */
  event.preventDefault();
  const field = document.querySelector<HTMLTextAreaElement>("#message")!;
  const text = field.value.trim();
  if (!text || !instanceId) return;
  messages.push({ author: "user", text });
  field.value = "";
  render();
  try {
    const turn = await api.sendMessage(instanceId, text);
    messages.push({ author: "mnesis", text: turn.response_text });
    lastTraceId = turn.trace_id;
  } catch (error) {
    messages.push({ author: "mnesis", text: error instanceof Error ? error.message : "Une erreur est survenue." });
  }
  render();
}

async function renderRoute(): Promise<void> {
  /** Affiche la conversation ou le dernier diagnostic selon le fragment d'URL. */
  if (window.location.hash === "#diagnostic" && instanceId && lastTraceId) {
    const trace = await api.getTrace(instanceId, lastTraceId);
    document.querySelector<HTMLDivElement>("#app")!.innerHTML = renderDiagnosticsMarkup(trace);
    return;
  }
  render();
}

window.addEventListener("hashchange", () => { void renderRoute(); });

async function start(): Promise<void> {
  /** Initialise l'instance de démonstration puis affiche l'interface. */
  render();
  try {
    const instance = await api.createInstance("Mnesis");
    instanceId = instance.id;
    instanceName = instance.name;
    await api.deployCoreFr(instance.id);
  } catch {
    messages.push({ author: "mnesis", text: "Connexion au service Mnesis impossible." });
  }
  render();
}

void start();
