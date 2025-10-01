

export interface ParticipantResponse {
    id?: number;
    eventId?: number;
    firstName?: string;
    lastName?: string;
    email?: string;
    urgentContact?: string;
    titleRole?: string;
    affiliation?: string;
    additionalContributors?: string;
    createdAt?: string;
    updatedAt?: string;
}


export interface ParticipantUI {
    id: number;
    eventId: number;
    firstName: string;
    lastName: string;
    email: string;
    urgentContact: string;
    titleRole: string;
    affiliation: string;
    additionalContributors: string;
    createdAt: string;
    updatedAt: string;
}
