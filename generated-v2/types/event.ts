

export interface EventResponse {
    id?: number;
    userId?: number;
    name?: string;
    description?: string;
    eventTz?: string;
    startDateTime?: string;
    endDateTime?: string;
    location?: string;
    affiliation?: string;
    logoPath?: string;
    maxParticipantsPerEvaluator?: number;
    createdAt?: string;
}


export interface EventUI {
    id: number;
    userId: number;
    name: string;
    description: string;
    eventTz: string;
    startDateTime: string;
    endDateTime: string;
    location: string;
    affiliation: string;
    logoPath: string;
    maxParticipantsPerEvaluator: number;
    createdAt: string;
}
