/**
 * Client HTTP minimal de l'interface Web Mnesis.
 *
 * Rôle : isoler les appels vers FastAPI de la logique d'affichage du navigateur.
 */

export type InstanceDto = { id: string; name: string; locale: string };
export type DeploymentDto = {
  concepts_deployed: number;
  lexemes_deployed: number;
  claims_deployed: number;
};
export type TurnDto = {
  response_text: string;
  intent: string | null;
  trace_id: string;
  learned_items: string[];
};
export type TraceDto = {
  action: string;
  confidence: number;
  candidate_actions: Record<string, number>;
  consulted_concepts: string[];
  affect_snapshot: Record<string, number>;
};

export class MnesisApiClient {
  /** Client réseau de l'interface Mnesis. */
  constructor(private readonly baseUrl = "") {}

  async createInstance(name: string): Promise<InstanceDto> {
    /** Crée une instance et retourne sa représentation HTTP. */
    const response = await fetch(`${this.baseUrl}/api/v1/instances`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name, locale: "fr-FR" }),
    });
    if (!response.ok) throw new Error("Impossible de créer l'instance Mnesis.");
    return response.json() as Promise<InstanceDto>;
  }

  async deployCoreFr(instanceId: string): Promise<DeploymentDto> {
    /** Déploie volontairement le socle linguistique français dans l'instance. */
    const response = await fetch(
      `${this.baseUrl}/api/v1/instances/${instanceId}/knowledge-packs/core-fr`,
      { method: "POST" },
    );
    if (!response.ok) throw new Error("Impossible de déployer le socle français.");
    return response.json() as Promise<DeploymentDto>;
  }

  async sendMessage(instanceId: string, text: string): Promise<TurnDto> {
    /** Envoie un message à une instance et retourne le tour conversationnel. */
    const response = await fetch(
      `${this.baseUrl}/api/v1/instances/${instanceId}/messages`,
      {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text }),
      },
    );
    if (!response.ok) throw new Error("Mnesis n'a pas pu traiter ce message.");
    return response.json() as Promise<TurnDto>;
  }

  async getTrace(instanceId: string, traceId: string): Promise<TraceDto> {
    /** Charge une trace cognitive en lecture seule. */
    const response = await fetch(
      `${this.baseUrl}/api/v1/instances/${instanceId}/traces/${traceId}`,
    );
    if (!response.ok) throw new Error("Trace cognitive indisponible.");
    return response.json() as Promise<TraceDto>;
  }
}
