

export interface EvaluatorResponse {
    id?: number;
    eventId?: number;
    firstName?: string;
    lastName?: string;
    email?: string;
    phone?: string;
    titleRole?: string;
    affiliation?: string;
    expertiseDescription?: string;
    areasOfExpertise?: string;
    status?: string;
    acceptedInviteToken?: string;
    acceptedInviteDate?: string;
    acceptedInvite?: boolean;
    createdAt?: string;
    updatedAt?: string;
}


export interface EvaluatorUI {
    id: number;
    eventId: number;
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    titleRole: string;
    affiliation: string;
    expertiseDescription: string;
    areasOfExpertise: string;
    status: string;
    acceptedInviteToken: string;
    acceptedInviteDate: string;
    acceptedInvite: boolean;
    createdAt: string;
    updatedAt: string;
}
